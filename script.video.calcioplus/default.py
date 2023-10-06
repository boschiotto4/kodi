# -*- coding: utf-8 -*-
import base64
import re
import sys
import six
from six.moves.urllib.parse import urljoin, unquote_plus, quote_plus, quote, unquote
from six.moves import zip

import json
import xbmc
import xbmcaddon
import xbmcgui
import pyxbmct
import requests
import os, sys
import xbmcplugin

from urllib.parse import urlparse
from resources.modules import control, client
from dateutil.parser import parse
from dateutil.tz import gettz
from dateutil.tz import tzlocal

ADDON = xbmcaddon.Addon()
#CWD = ADDON.getAddonInfo('path').decode('utf-8')

ADDON_DATA = ADDON.getAddonInfo('profile')
ADDON_PATH = ADDON.getAddonInfo('path')
DESCRIPTION = ADDON.getAddonInfo('description')
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
ID = ADDON.getAddonInfo('id')
NAME = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')
Lang = ADDON.getLocalizedString

#Dialog = xbmcgui.Dialog()
base = xbmcgui.Window(xbmcgui.getCurrentWindowId())

vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

BASEURL = 'https://my.livesoccer.sx/'
Live_url = 'https://my.livesoccer.sx/'
Alt_url = 'https://liveon.sx/program'     #'https://1.livesoccer.sx/program'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

accepted_league = ['italy','england','spain','germany','france','nederlands','UEFA Champions','UEFA Europa','UEFA Conference']

STATE = 'close'
#addon_handle = int(sys.argv[1])
ACTION_PREVIOUS_MENU = 10
ACTION_BACK_MENU = 92
ACTION_SELECT_ITEM = 7

ACTION_GESTURE_SWIPE_LEFT = 511
ACTION_GESTURE_SWIPE_RIGHT = 521

ACTION_GESTURE_SWIPE_UP = 531
ACTION_GESTURE_SWIPE_DOWN = 541

ADDON_ACTION_MOUSE_LEFT_CLICK = 100 # Mouse left click.
ADDON_ACTION_MOUSE_RIGHT_CLICK = 101 # Mouse right click.
ADDON_ACTION_MOUSE_MIDDLE_CLICK = 102
ACTION_MOUSE_DOUBLE_CLICK = 103

ADDON_ACTION_TOUCH_TAP  = 401

barItems = []    

# Page grid
offset_page_top = 140
offset_page_left = 50
page_blur = 130
alpa = '0x75FFFFFF'

# Item
width = 380
height = 220
offset_w = 5
offset_h = 5

rows_item_count = []

item_selected = [0, 0]
data_rows = []

row_items_count = []
id_row = 0
item_sel = 0

ui = None

# add a class to create your xml based window
class GUI(xbmcgui.WindowXML):
    # [optional] this function is only needed of you are passing optional data to your window
    def __init__(self, *args, **kwargs):
        # get the optional data and add it to a variable you can use elsewhere in your script
        self.data = kwargs['optional1']
        
    # until now we have a blank window, the onInit function will parse your xml file
    def onInit(self):
        self.gui_rows = []
        self.lists = []
        self.data = []
        # define two temporary lists where we are going to add our the listitems to

        # create and add some items to the first temporary list
        for r in range(0, 10):
            empty_list = []
            empty_data = []
            self.lists.append(empty_list)
            self.data.append(empty_data)
            self.getControl(r * 10 + 10).setVisible(False)
            self.gui_rows.append(self.getControl(r * 10 + 10))

        #xbmc.sleep(100)
        # this puts the focus on the first listitem in the first container

        xbmc.log('boxss ' + str(len(self.lists)),xbmc.LOGERROR)
        
        #self.setFocus(gui_rows[0])
        pass

    def isInited(self):
        if len(self.lists) < 10:
            return False
        return True
        pass
    def getVisibleRow(self):
        c = 0
        for r in range(0, 10):
            if self.gui_rows[r].isVisible():
                c = c + 1
        return c
    
    def addQuad(self, row, _data):      
        #for i in range(0, 10):
        listitem = xbmcgui.ListItem()
        listitem.setInfo( type="Video", infoLabels={ "Title": "" + _data.getTeams().upper() + "", "OriginalTitle": "" + _data.getFtime() + "", "Album": "" + _data.getBaseImage() + "" }   )
        
        _data.setOnlyLeagueName(_data.getLname())
        for r in accepted_league:
            _data.setOnlyLeagueName(_data.getOnlyLeagueName().lower().replace(r, ''))
        _data.setOnlyLeagueName(_data.getOnlyLeagueName().strip().upper())
        
        listitem.setLabel(_data.getOnlyLeagueName())
        self.data[row].append(_data)
        self.lists[row].append(listitem)
        self.gui_rows[row].addItem(listitem) 
        self.gui_rows[row].setVisible(True)
        pass

    def applyContextualImages(self):
        # Apply contextual image if present   
        for r in range(0, len(self.data)):
            for i in range(0, len(self.data[r])):
                urls = []
                
                mydata = self.data[r][i]
                
                a = urlparse(mydata.getLogo_league())
                #xbmc.log(str(a.path), xbmc.LOGERROR)
                if 'football' in a.path:
                    urls = searchImageByDesc(mydata.getTeams() + ' ' + mydata.getLname() + ' site:goal.com')
                else:
                    urls = searchImageByDesc(mydata.getTeams() + ' ' + mydata.getLname())
                if urls != None and len(urls) > 0:
                    if is_url_image(urls[0]):
                        self.lists[r][i].setArt({ 'thumb' : urls[0]})

                # Apply contextual image if present
                urls = searchImageByDesc(mydata.getOnlyLeagueName() + ' logo png',True)
                if urls != None and len(urls) > 0:
                    self.lists[r][i].setArt({ 'clearlogo' : urls[0]})
                    #self.lists[r][i].setColorDiffuse('0xFFFFFFFF')
        pass
        
    def onAction(self, action):
        global id_row

        if action.getId() == xbmcgui.ACTION_MOVE_LEFT:
            move_left()
        elif action.getId() == xbmcgui.ACTION_MOVE_RIGHT:
            move_right()
        elif action.getId() == xbmcgui.ACTION_MOVE_UP:
            move_up()
        elif action.getId() == xbmcgui.ACTION_MOVE_DOWN:
            move_down()
        elif action.getId() in (ADDON_ACTION_MOUSE_LEFT_CLICK, ADDON_ACTION_MOUSE_MIDDLE_CLICK, ADDON_ACTION_MOUSE_RIGHT_CLICK, ACTION_SELECT_ITEM, ACTION_MOUSE_DOUBLE_CLICK, ADDON_ACTION_TOUCH_TAP):
            get_stream(self.data[item_selected[1]][item_selected[0]].getStreams()) 
        else:
            super(GUI, self).onAction(action)
        pass

    def onFocus(self, controlId):
        global id_row       
        #super(GUI, self).onFocus(controlId)
        #return 
        for r in range(0, len(self.lists)):
            for i in range(0, len(self.lists[r])):
                if controlId == r * 10 + 10:
                    id_row = r
                self.lists[r][i].setLabel2('icons/empty.png')
  
        for i in range(0, len(self.lists[id_row])):
            self.lists[id_row][i].setLabel2('icons/b2.png')
        pass


class EventData():
    def __init__( self, id_row, _teams, _ftime, _lname, _streams, _logo_league):
        self.teams = _teams
        self.ftime = _ftime
        self.lname = _lname
        self.streams = _streams
        self.logo_league = _logo_league
        self.onlyleague = ''
        
    def getTeams(self):
        return self.teams
    def getFtime(self):
        return self.ftime
    def getBaseImage(self):
        return 'icons/b1.png'
    def getLname(self):
        return self.lname
    def getStreams(self):
        return self.streams
    def getLogo_league(self):
        return self.logo_league
    def setOnlyLeagueName(self, n):
        self.onlyleague = n

    def getOnlyLeagueName(self):
        return self.onlyleague

# Engine 
def is_url_image(image_url):
    try:
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            return True
    except:
        return False
    return False
   
def searchImageByDesc(desc,isLogo=False):
    urls = []
    try:
        if isLogo:
            r = requests.get("https://api.qwant.com/v3/search/images",
                params={
                    'count': 1,
                    'q': desc,
                    't': 'images',
                    'safesearch': 1,
                    'locale': 'it_IT',
                    'offset': 0,
                    'device': 'desktop'
#                    'image-size':'small'
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 rv:94.0) Gecko/20100101 Firefox/94.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
                }
            )
        else:
            r = requests.get("https://api.qwant.com/v3/search/images",
                params={
                    'count': 1,
                    'q': desc,
                    't': 'images',
                    'safesearch': 1,
                    'locale': 'it_IT',
                    'offset': 0,
                    'device': 'desktop',
                    'freshness': 'year'
                },
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 rv:94.0) Gecko/20100101 Firefox/94.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
                }
            )
        
        response = r.json().get('data').get('result').get('items')
        urls = [r.get('media') for r in response]
        #xbmc.log(str(urls[0]), xbmc.LOGERROR)
    except:
        urls = None
    return urls
    
# GUI EVENTs
def move_left():
    global item_sel
    item_selected[0] = item_selected[0] - 1

    item_sel = item_sel - 1
    refresh_selection()
    pass

def move_right():
    global item_sel
    item_selected[0] = item_selected[0] + 1
    item_sel = item_sel + 1
    
    refresh_selection()
    pass

def move_up():
    item_selected[1] = item_selected[1] - 1

    refresh_selection()
    pass

def move_down():
    item_selected[1] = item_selected[1] + 1
    
    refresh_selection()
    pass
 

def refresh_selection():
    global item_sel
    global ui

    if len(row_items_count) <= 0:
        return

    if item_selected[1] < 0:
        item_selected[1] = 0
    if item_selected[1] > ui.getVisibleRow() - 1:
        item_selected[1] = ui.getVisibleRow() - 1

    if item_selected[0] < 0:
        item_selected[0] = 0

    #xbmc.log(str(row_items_count[item_selected[1]]), xbmc.LOGERROR)
    #xbmc.log(str(item_selected[0]), xbmc.LOGERROR)
    if item_selected[0] > row_items_count[item_selected[1]] - 1:
        item_selected[0] = row_items_count[item_selected[1]] - 1

    focused_row = (item_selected[1]) * 10 + 10
    if item_sel < 0:
        item_sel = 0
    
    if item_sel > 2:
        item_sel = 2
    xbmc.executebuiltin('Control.SetFocus('+ str(focused_row) + ', ' + str(item_sel) + ')')
    #xbmc.log('p:' + str(len(row_items_count)),xbmc.LOGERROR)
    
    pass
 
import threading
import time

def load_quads():
    t1 = threading.Thread(target=load_quads_backgroundWorker)
    #Background thread will finish with the main program
    t1.setDaemon(True)
    #Start load_quads_backgroundWorker() in a separate thread
    t1.start()
    #You main program imitated by sleep
    #time.sleep(5)
    pass
   

#Routine that processes whatever you want as background
def load_quads_backgroundWorker(): 
    global ui
    global row_items_count

    # Wait for gui init
    xbmc.sleep(2000)
    
    # ADD TO GUI the quads
    row = 0
    for r in data_rows:
        for i in r: 
            ui.addQuad(row, i)
        row_items_count.append(len(r))
        row = row + 1

    ui.applyContextualImages()
    pass

def convDateUtil(timestring, newfrmt='default', in_zone='UTC'):
    if newfrmt == 'default':
        newfrmt = xbmc.getRegion('time').replace(':%S', '')
        newfrmt = '%H:%M'
    try:
        in_time = parse(timestring)
        in_time_with_timezone = in_time.replace(tzinfo=gettz(in_zone))
        local_time = in_time_with_timezone.astimezone(local_tzinfo)

        return local_time.strftime(newfrmt)
    except:
        return timestring


def Main_menu():

    # addDir('[B][COLOR gold]Channels 24/7[/COLOR][/B]', 'https://1.livesoccer.sx/program.php', 14, ICON, FANART, '')
    addDir('[B][COLOR white]LIVE EVENTS[/COLOR][/B]', Live_url, 5, ICON, FANART, '')
    # addDir('[B][COLOR gold]Alternative VIEW [/COLOR][/B]', '', '', ICON, FANART, '')
    addDir('[B][COLOR gold]Alternative LIVE EVENTS[/COLOR][/B]', Alt_url, 15, ICON, FANART, '')
    addDir('[B][COLOR white]SPORTS[/COLOR][/B]', '', 3, ICON, FANART, '')
    addDir('[B][COLOR white]BEST LEAGUES[/COLOR][/B]', '', 2, ICON, FANART, '')
    addDir('[B][COLOR gold]Settings[/COLOR][/B]', '', 10, ICON, FANART, '')
    addDir('[B][COLOR gold]Version: [COLOR lime]%s[/COLOR][/B]' % vers, '', 'BUG', ICON, FANART, '')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def leagues_menu():
    addDir('[B][COLOR white]Uefa Champions League[/COLOR][/B]',
           BASEURL + 'index.php?champ=uefa-champions-league', 5,
           BASEURL + 'flags/uefa-champions-league.png', FANART, 'Uefa Champions League')
    addDir('[B][COLOR white]Uefa Europa League[/COLOR][/B]', BASEURL + 'index.php?champ=uefa-europa-league',
           5, BASEURL + 'flags/uefa-europa-league.png', FANART, 'Uefa Europa League')
    addDir('[B][COLOR white]Premier League[/COLOR][/B]', BASEURL + 'index.php?champ=premier-league', 5,
           BASEURL + 'flags/premier-league.png', FANART, 'Premier League')
    addDir('[B][COLOR white]Bundesliga[/COLOR][/B]', BASEURL + 'index.php?champ=bundesliga', 5,
           BASEURL + 'flags/bundesliga.png', FANART, 'Bundesliga')
    addDir('[B][COLOR white]Laliga[/COLOR][/B]', BASEURL + 'index.php?champ=laliga', 5,
           BASEURL + 'flags/spanish-primera-division.png', FANART, 'Laliga')
    addDir('[B][COLOR white]Serie A[/COLOR][/B]', BASEURL + 'index.php?champ=serie-a', 5,
           BASEURL + 'flags/serie-a.png', FANART, 'Serie a')
    addDir('[B][COLOR white]France Ligue 1[/COLOR][/B]', BASEURL + 'index.php?champ=france-ligue-1', 5,
           BASEURL + 'flags/france-ligue-1.png', FANART, 'France ligue 1')
    addDir('[B][COLOR white]Eredivisie[/COLOR][/B]', BASEURL + 'index.php?champ=eredivisie', 5,
           BASEURL + 'flags/eredivisie.png', FANART, 'Eredivisie')
    addDir('[B][COLOR white]Australian A League[/COLOR][/B]',
           BASEURL + 'index.php?champ=australian-a-league', 5,
           BASEURL + 'flags/australian-a-league.png', FANART, 'Australian a league')
    addDir('[B][COLOR white]MLS[/COLOR][/B]', BASEURL + 'index.php?champ=mls', 5,
           BASEURL + 'flags/mls.png', FANART, 'Mls')
    addDir('[B][COLOR white]Rugby Top 14[/COLOR][/B]', BASEURL + 'index.php?champ=rugby-top-14', 5,
           BASEURL + 'flags/rugby-top-14.png', FANART, 'Rugby top 14')
    addDir('[B][COLOR white]Greece Super League[/COLOR][/B]',
           BASEURL + 'index.php?champ=greece-super-league', 5,
           BASEURL + 'flags/greece-super-league.png', FANART, 'Greece super league')
    addDir('[B][COLOR white]Argentina Superliga[/COLOR][/B]',
           BASEURL + 'index.php?champ=argentina-superliga', 5,
           BASEURL + 'flags/argentina-superliga.png', FANART, 'Argentina superliga')
    addDir('[B][COLOR white]Portuguese Primeira Liga[/COLOR][/B]',
           BASEURL + 'index.php?champ=portuguese-primeira-liga', 5,
           BASEURL + 'flags/portuguese-primeira-liga.png', FANART, 'Portuguese primeira liga')
    addDir('[B][COLOR white]Primera Division Apertura[/COLOR][/B]',
           BASEURL + 'index.php?champ=primera-division-apertura', 5,
           BASEURL + 'flags/primera-division-apertura.png', FANART, 'Primera division apertura')
    addDir('[B][COLOR white]Bundesliga 2[/COLOR][/B]', BASEURL + 'index.php?champ=bundesliga-2', 5,
           BASEURL + 'flags/bundesliga-2.png', FANART, 'Bundesliga 2')
    addDir('[B][COLOR white]Greece Super League 2[/COLOR][/B]',
           BASEURL + 'index.php?champ=greece-super-league-2', 5,
           BASEURL + 'flags/greece-super-league-2.png', FANART, 'Greece super league 2')
    addDir('[B][COLOR white]Belarus Vysheyshaya Liga[/COLOR][/B]',
           BASEURL + 'index.php?champ=belarus-vysheyshaya-liga', 5,
           BASEURL + 'flags/belarus-vysheyshaya-liga.png', FANART, 'Belarus vysheyshaya liga')


def sports_menu():
    addDir('[B][COLOR white]Football[/COLOR][/B]', BASEURL + '?type=football', 5,
           BASEURL + 'images/football.png', FANART, 'Football')
    addDir('[B][COLOR white]Basketball[/COLOR][/B]', BASEURL + '?type=basketball', 5,
           BASEURL + 'images/basketball.png', FANART, 'Basketball')
    addDir('[B][COLOR white]MotorSport[/COLOR][/B]', BASEURL + '?type=motorsport', 5,
           BASEURL + 'images/motorsport.png', FANART, 'MotorSport')
    addDir('[B][COLOR white]Handball[/COLOR][/B]', BASEURL + '?type=handball', 5,
           BASEURL + 'images/handball.png', FANART, 'Handball')
    addDir('[B][COLOR white]Rugby[/COLOR][/B]', BASEURL + '?type=rugby', 5,
           BASEURL + 'images/rugby.png', FANART, 'Rugby')
    addDir('[B][COLOR white]NFL[/COLOR][/B]', BASEURL + '?type=nfl', 5,
           BASEURL + 'images/nfl.png', FANART, 'NFL')
    addDir('[B][COLOR white]UFC[/COLOR][/B]', BASEURL + '?type=ufc', 5,
           BASEURL + 'images/ufc.png', FANART, 'UFC')
    addDir('[B][COLOR white]Wrestling[/COLOR][/B]', BASEURL + '?type=wresling', 5,
           BASEURL + 'images/wresling.png', FANART, 'Wresling')
    addDir('[B][COLOR white]Hockey[/COLOR][/B]', BASEURL + '?type=hokey', 5,
           BASEURL + 'images/hockey.png', FANART, 'Hokey')
    addDir('[B][COLOR white]Volleyball[/COLOR][/B]', BASEURL + '?type=volleyball', 5,
           BASEURL + 'images/volleyball.png', FANART, 'Volleyball')
    addDir('[B][COLOR white]Darts[/COLOR][/B]', BASEURL + '?type=darts', 5,
           BASEURL + 'images/darts.png', FANART, 'Darts')
    addDir('[B][COLOR white]Tennis[/COLOR][/B]', BASEURL + '?type=tennis', 5,
           BASEURL + 'images/tennis.png', FANART, 'Tennis')
    addDir('[B][COLOR white]Boxing[/COLOR][/B]', BASEURL + '?type=boxing', 5,
           BASEURL + 'images/boxing.png', FANART, 'Boxing')
    addDir('[B][COLOR white]Cricket[/COLOR][/B]', BASEURL + '?type=cricket', 5,
           BASEURL + 'images/cricket.png', FANART, 'Cricket')
    addDir('[B][COLOR white]Baseball[/COLOR][/B]', BASEURL + '?type=baseball', 5,
           BASEURL + 'images/baseball.png', FANART, 'Baseball')
    addDir('[B][COLOR white]Snooker[/COLOR][/B]', BASEURL + '?type=snooker', 5,
           BASEURL + 'images/snooker.png', FANART, 'Snooker')
    addDir('[B][COLOR white]Chess[/COLOR][/B]', BASEURL + '?type=chess', 5,
           BASEURL + 'images/chess.png', FANART, 'Chess')


def get_events(url):  # 5
    #xbmc.log('%s: {}'.format(url))
    #xbmc.log(url, xbmc.LOGERROR)

    id_row = 0
    global data_rows

    data = client.request(url)
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = re.sub('\t', '', data)
    # xbmc.log('@#@EDATAAA: {}'.format(data))
    events = list(zip(client.parseDOM(data, 'li', attrs={'class': "item itemhov"}),
                      client.parseDOM(data, 'li', attrs={'class': "bahamas"})))
                      # re.findall(r'class="bahamas">(.+?)</span> </div> </li>', str(data), re.DOTALL)))
    # addDir('[COLORwhite]Time in GMT+2[/COLOR]', '', 'BUG', ICON, FANART, '')
    for event, streams in events:
        # xbmc.log('@#@EVENTTTTT:%s' % event)
        # xbmc.log('@#@STREAMS:%s' % streams)
        watch = '[COLORlime]*[/COLOR]' if '>Live<' in event else '[COLORred]*[/COLOR]'
        try:
            teams = client.parseDOM(event, 'td')
            # xbmc.log('@#@TEAMSSSS:%s' % str(teams))
            home, away = re.sub(r'\s*(<img.+?>)\s*', '', client.replaceHTMLCodes(teams[0])),\
                re.sub(r'\s*(<img.+?>)\s*', '', client.replaceHTMLCodes(teams[2]))
            if six.PY2:
                home = home.strip().encode('utf-8')
                away = away.strip().encode('utf-8')
            teams = '[B]{0} vs {1}[/B]'.format(home, away)
            teams = teams.replace('\t', '')
        except IndexError:
            teams = client.parseDOM(event, 'center')[0]
            teams = re.sub(r'<.+?>|\s{2}', '', teams)
            teams = client.replaceHTMLCodes(teams)
            teams = teams.encode('utf-8') if six.PY2 else teams
            teams = '[B]{}[/B]'.format(teams.replace('-->', ''))
        # xbmc.log('@#@TEAM-FINAL:%s' % str(teams))
        lname = client.parseDOM(event, 'a')[1]
        lname = client.parseDOM(lname, 'span')[0]
        lname = re.sub(r'<.+?>', '', lname)
        lname = client.replaceHTMLCodes(lname)
        time = client.parseDOM(event, 'span', attrs={'class': 'gmt_m_time'})[0]
        time = time.split('GMT')[0].strip()
        cov_time = convDateUtil(time, 'default', 'GMT+3')#.format(str(control.setting('timezone'))))
        ftime = '[B][COLORwhite]{}[/COLOR][/B]'.format(cov_time)
        name = '{0}{1} [COLORgold]{2}[/COLOR] - [I]{3}[/I]'.format(watch, ftime, teams, lname)

        # links = re.findall(r'<a href="(.+?)".+?>( Link.+? )</a>', event, re.DOTALL)
        streams = str(quote(base64.b64encode(six.ensure_binary(streams))))

        icon = client.parseDOM(event, 'img', ret='src')[0]
        icon = urljoin(BASEURL, icon)
 
        logo_league = icon
        
        #addDir(name, streams, 4, icon, FANART, name)
        row = []
        appended = False
        
        for r in data_rows:
            appended = False
            if r[0].getLname() == lname:
                r.append( EventData(id_row, teams, ftime,  lname, streams, logo_league) )
                appended = True
                break
        if appended == False:
            new_r = []
            new_r.append( EventData(id_row, teams, ftime,  lname, streams, logo_league) )
            data_rows.append(new_r)
            id_row = id_row + 1
        
    # SORT data_row
    #re.search(sort_priority[i_sort], r[0].getLname().lower())
    data_rows2 = []
    for a in accepted_league:
        filtered_row = []
        for r in data_rows:
            i_i = 0
            for i in r:
                # Accept only selected events
                accepted = False
                if a in i.getLname().lower():
                    accepted = True
                if accepted:
                    filtered_row.append(i)
        data_rows2.append(filtered_row)
    
    data_rows = data_rows2
    return 
    pass
#xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_livetv(url):
    data = client.request(url)
    # xbmc.log('@#@EDATAAA: {}'.format(data))
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = client.parseDOM(data, 'table', attrs={'class': 'styled-table'})[0]
    chans = list(zip(client.parseDOM(data, 'button', attrs={'class': 'tvch'}),
                    client.parseDOM(data, 'a', ret='href')))
    for chan, stream in chans:
        # stream = str(quote(base64.b64encode(six.ensure_binary(stream))))

        chan = chan.encode('utf-8') if six.PY2 else chan
        chan = '[COLOR gold][B]{}[/COLOR][/B]'.format(chan)

        addDir(chan, stream, 100, ICON, FANART, name)


#xbmcplugin.setContent(int(sys.argv[1]), 'videos')


def get_new_events(url):# 15
    #import requests
    data = six.ensure_text(client.request(url, headers=headers))
    # xbmc.log('@#@EDATAAA: {}'.format(data))
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = re.sub('\t', '', data)
    days = list(zip(client.parseDOM(data, 'button', attrs={'class': 'accordion'}),
                    client.parseDOM(data, 'div', attrs={'class': "panel"})))
    # data = client.parseDOM(str(data), 'div', attrs={'class': "panel"})
    # xbmc.log('@#@DAYSSS: {}'.format(str(days)))
    for day, events in days[1:]:
        dia = client.parseDOM(day, 'span')[-1]
        dia = '[COLOR lime][B]{}[/B][/COLOR]'.format(dia)
        events = six.ensure_text(events, encoding='utf-8', errors='ignore')
        events = list(zip(client.parseDOM(events, 'div', attrs={'class': "left.*?"}),
                          client.parseDOM(events, 'div', attrs={'class': r"d\d+"})))
        #xbmc.log('@#@EVENTS: {}'.format(str(events)))
    # addDir('[COLORcyan]Time in GMT+2[/COLOR]', '', 'BUG', ICON, FANART, '')
        addDir(dia, '', 'BUG', ICON, FANART, name)
        tevents = []
        for event, streams in events:
            if '\n' in event:
                ev = event.split('\n')
                for i in ev:
                    try:
                        time = re.findall(r'(\d{2}:\d{2})', i, re.DOTALL)[0]
                    except IndexError:
                        time = 'N/A'
                    tevents.append((i, streams, time))
            else:
                try:
                    time = re.findall(r'(\d{2}:\d{2})', event, re.DOTALL)[0]
                except IndexError:
                    time = 'N/A'
                tevents.append((event, streams, time))
        #xbmc.log('EVENTSSS: {}'.format(tevents))
        for event, streams, time in sorted(tevents, key=lambda x: x[2]):
            # links = re.findall(r'<a href="(.+?)".+?>( Link.+? )</a>', event, re.DOTALL)
            streams = str(quote(base64.b64encode(six.ensure_binary(streams))))
            cov_time = convDateUtil(time, 'default', 'GMT{}'.format(str(control.setting('timezone'))))
            ftime = '[COLORcyan]{}[/COLOR]'.format(cov_time)

            event = event.encode('utf-8') if six.PY2 else event
            event = client.replaceHTMLCodes(event)
            event = re.sub('<.+?>', '', event)
            event = re.sub(r'(\d{2}:\d{2})', '', event)
            event = ftime + ' [COLOR gold][B]{}[/COLOR][/B]'.format(event.replace('\t', ''))

            addDir(event, streams, 4, ICON, FANART, name)


#xbmcplugin.setContent(int(sys.argv[1]), 'videos')

def get_stream(url):  # 4
    data = six.ensure_text(base64.b64decode(unquote(url))).strip('\n')
    # xbmc.log('@#@DATAAAA: {}'.format(data))
    if 'info_outline' in data:
        control.infoDialog("[COLOR gold]No Links available ATM.\n [COLOR lime]Try Again Later![/COLOR]", NAME,
                           iconimage, 5000)
        return
    else:
        links = list(zip(client.parseDOM(str(data), 'a', ret='href'), client.parseDOM(str(data), 'a')))
        # xbmc.log('@#@STREAMMMMMSSSSSS:%s' % links, xbmc.LOGINFO)
        titles = []
        streams = []

        for link, title in links:
            # if not 'vecdn' in link:
            if not 'https://bedsport' in link and not 'vecdn' in link:
                if str(link) == str(title):
                    title = title
                else:
                    title += ' | {}'.format(link)
                streams.append(link.rstrip())
                titles.append(title)

        if len(streams) > 1:
            dialog = xbmcgui.Dialog()
            ret = dialog.select('[COLORgold][B]Choose Stream[/B][/COLOR]', titles)
            if ret == -1:
                return
            elif ret > -1:
                host = streams[ret]
                # xbmc.log('@#@STREAMMMMM:%s' % host)
                return resolve(host, name)
            else:
                return False
        else:
            link = links[0][0]
            return resolve(link, name)


#def idle():
#    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
#        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
#    else:
#        xbmc.executebuiltin('Dialog.Close(busydialog)')


#def busy():
#    if float(xbmcaddon.Addon('xbmc.addon').getAddonInfo('version')[:4]) > 17.6:
#        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
#    else:
#        xbmc.executebuiltin('ActivateWindow(busydialog)')


def resolve(url, name):
    ragnaru = ['liveon.sx/embed', '//em.bedsport', 'cdnz.one/ch', 'cdn1.link/ch', 'cdn2.link/ch']
    xbmc.log('RESOLVE-URL: %s' % url)
    # ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
    ua = 'Mozilla/5.0 (iPad; CPU OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1'
    # dialog.notification(AddonTitle, '[COLOR skyblue]Attempting To Resolve Link Now[/COLOR]', icon, 5000)
    if 'webplay' in url or 'livestreames' in url:
        html = six.ensure_text(client.request(url, referer=BASEURL))
        # xbmc.log('HTMLLLLL: {}'.format(html))
        url = client.parseDOM(html,'div', attrs={'class': 'container'})[0]
        url = client.parseDOM(url, 'iframe', ret='src')[0]
    if 'acestream' in url:
        url1 = "plugin://program.plexus/?url=" + url + "&mode=1&name=acestream+"
        liz = xbmcgui.ListItem(name)
        liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
        liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage,
                    'fanart': fanart})
        liz.setPath(url)
        xbmc.Player().play(url1, liz, False)
        quit()
    if '/live.cdnz' in url:
        r = six.ensure_str(client.request(url, referer=BASEURL)).replace('\t', '')
        # xbmc.log("[{}] - HTML: {}".format(ADDON.getAddonInfo('id'), str(r)))
        from resources.modules import jsunpack
        if 'script>eval' in r:
            unpack = re.findall(r'''<script>(eval.+?\{\}\)\))''', r, re.DOTALL)[0]
            r = jsunpack.unpack(unpack.strip())
            # xbmc.log('RESOLVE-UNPACK: %s' % str(r))
        else:
            r = r
        # xbmc.log("[{}] - HTML: {}".format(ADDON.getAddonInfo('id'), str(r)))
        if 'hfstream.js' in r:
            regex = '''<script type='text/javascript'> width=(.+?), height=(.+?), channel='(.+?)', g='(.+?)';</script>'''
            wid, heig, chan, ggg = re.findall(regex, r, re.DOTALL)[0]
            stream = 'https://www.playerfs.com/membedplayer/' + chan + '/' + ggg + '/' + wid + '/' + heig + ''
        else:
            if 'cbox.ws/box' in r:
                try:
                    stream = client.parseDOM(r, 'iframe', ret='src', attrs={'id': 'thatframe'})[0]
                except IndexError:
                    streams = client.parseDOM(r, 'iframe', ret='src')
                    stream = [i for i in streams if not 'adca.' in i][0]
                    # xbmc.log("[{}] - STREAM: {}".format(ADDON.getAddonInfo('id'), str(stream)))
            else:
                stream = client.parseDOM(r, 'iframe', ret='src')[-1]
                # xbmc.log("[{}] - STREAM-ELSE: {}".format(ADDON.getAddonInfo('id'), str(stream)))
        # xbmc.log("[{}] - STREAM: {}".format(ADDON.getAddonInfo('id'), str(stream)))
        rr = client.request(stream, referer=url)
        rr = six.ensure_text(rr, encoding='utf-8').replace('\t', '')
        if 'eval' in rr:
            unpack = re.findall(r'''script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0]
            # unpack = client.parseDOM(rr, 'script')
            # xbmc.log('UNPACK: %s' % str(unpack))
            # unpack = [i.rstrip() for i in unpack if 'eval' in i][0]
            rr = six.ensure_text(jsunpack.unpack(str(unpack) + ')'), encoding='utf-8')
        else:
            r = rr
        if 'youtube' in rr:
            try:
                flink = client.parseDOM(r, 'iframe', ret='src')[0]
                fid = flink.split('/')[-1]
            except IndexError:
                fid = re.findall(r'''/watch\?v=(.+?)['"]''', r, re.DOTALL)[0]
            # xbmc.log('@#@STREAMMMMM111: %s' % fid)

            flink = 'plugin://plugin.video.youtube/play/?video_id={}'.format(str(fid))
            # xbmc.log('@#@STREAMMMMM111: %s' % flink)

        else:
            if '<script>eval' in rr and not '.m3u8?':
                unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(unpack)))
                rr = jsunpack.unpack(str(unpack) + ')')
                # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(r)))
            # else:
            #     xbmc.log("[{}] - Error unpacking".format(ADDON.getAddonInfo('id')))
            if 'player.src({src:' in rr:
                flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
                # xbmc.log('@#@STREAMMMMM: %s' % flink)
            elif 'hlsjsConfig' in rr:
                flink = re.findall(r'''src=\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
            elif 'new Clappr' in rr:
                flink = re.findall(r'''source\s*:\s*["'](.+?)['"]\,''', str(rr), re.DOTALL)[0]
            elif 'player.setSrc' in rr:
                flink = re.findall(r'''player.setSrc\(["'](.+?)['"]\)''', rr, re.DOTALL)[0]

            else:
                try:
                    flink = re.findall(r'''source:\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
                except IndexError:
                    ea = re.findall(r'''ajax\(\{url:\s*['"](.+?)['"],''', rr, re.DOTALL)[0]
                    ea = six.ensure_text(client.request(ea)).split('=')[1]
                    flink = re.findall('''videoplayer.src = "(.+?)";''', ea, re.DOTALL)[0]
                    flink = flink.replace('" + ea + "', ea)

            flink += '|Referer={}'.format(quote(stream)) #if not 'azcdn' in flink else ''
        # xbmc.log('@#@STREAMMMMM111: %s' % flink)
        stream_url = flink

    elif '1l1l.to/' in url or 'l1l1.to/' in url:#https://l1l1.to/ch18
        #'//cdn122.com/embed/2k2kr220ol6yr6i&scrolling=no&frameborder=0&allowfullscreen=true'
        if 'l1l1.' in url:
            referer = 'https://l1l1.to/'
            r = six.ensure_str(client.request(url, referer=referer))
            stream = client.parseDOM(r, 'iframe', ret='src')[-1]
            stream = 'https:' + stream if stream.startswith('//') else stream
            rr = six.ensure_str(client.request(stream, referer=referer))
            # xbmc.log('@#@RRRDATA: %s' % rr)
            if '<script>eval' in rr:
                rr = six.ensure_text(rr, encoding='utf-8').replace('\t', '')
                from resources.modules import jsunpack
                unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(unpack)))
                rr = jsunpack.unpack(str(unpack) + ')')
                # xbmc.log("STREAM-UNPACK: {}".format(str(unpack)))
                if '<script>eval' in rr and not '.m3u8?':
                    unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                    rr = jsunpack.unpack(str(unpack) + ')')
                    # xbmc.log("STREAM-UNPACK22: {}".format(str(unpack)))
                else:
                    rr = rr
                if 'player.src({src:' in rr:
                    flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
                    # xbmc.log('@#@STREAMMMMM: %s' % flink)
                elif 'hlsjsConfig' in rr:
                    flink = re.findall(r'''src=\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
                elif 'new Clappr' in rr:
                    flink = re.findall(r'''source\s*:\s*["'](.+?)['"]\,''', str(rr), re.DOTALL)[0]
                elif 'player.setSrc' in rr:
                    flink = re.findall(r'''player.setSrc\(["'](.+?)['"]\)''', rr, re.DOTALL)[0]
                else:
                    try:
                        flink = re.findall(r'''source:\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
                    except IndexError:
                        ea = re.findall(r'''ajax\(\{url:\s*['"](.+?)['"],''', rr, re.DOTALL)[0]
                        ea = six.ensure_text(client.request(ea)).split('=')[1]
                        flink = re.findall('''videoplayer.src = "(.+?)";''', ea, re.DOTALL)[0]
                        flink = flink.replace('" + ea + "', ea)
                flink += '|Referer={}'.format(quote(stream))
                stream_url = flink
        else:
            referer = 'https://1l1l.to/'
            r = six.ensure_str(client.request(url))
            # xbmc.log('@#@ΡDATA: %s' % r)
            if 'video.netwrk.ru' in r:
                ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 OPR/92.0.0.0'
                frame = client.parseDOM(r, 'div', attrs={'class': 'player'})[0]
                frame = client.parseDOM(frame, 'iframe', ret='src')[0]
                data = six.ensure_str(client.request(frame, referer=referer))
                # xbmc.log('@#@SDATA: %s' % data)
                #hls:  "https://ad2017.vhls.ru.com/lb/nuevo40/index.m3u8",
                link = re.findall(r'''hls:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]
                # ua = 'Mozilla/5.0 (iPad; CPU OS 15_6_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Mobile/15E148 Safari/604.1'
                stream_url = link + '|Referer=https://video.netwrk.ru.com/&User-Agent=iPad'.format(referer, ua)
            elif 'stream2watch' in r:
                frame = client.parseDOM(r, 'div', attrs={'class': 'player'})[0]
                frame = client.parseDOM(frame, 'iframe', ret='src')[0]
                data = six.ensure_str(client.request(frame, referer=referer))
                # xbmc.log('@#@STREAM2DATA: %s' % data)
                hlsurl, pk, ea = re.findall('.*hlsUrl\s*=\s*"(.*?&\w+=)".*?var\s+\w+\s*=\s*"([^"]+).*?>\s*ea\s*=\s*"([^"]+)', data, re.DOTALL)[0]
                link = hlsurl.replace('" + ea + "', ea) + pk
                # xbmc.log('@#@STREAM2HLSURL: %s' % link)
                data_link = six.ensure_str(client.request(link, referer='https://stream2watch.freeucp.com'))
                # xbmc.log('@#@STREAM2data: %s' % data_link)
                link2 = re.findall('.*(http.+?$)', data_link)[0]
                stream_url = link2 + '|Referer=https://stream2watch.freeucp.com/&Origin=https://stream2watch.freeucp.com/&User-Agent=iPad'

            else:
                if 'fid=' in r:
                    regex = '''<script>fid=['"](.+?)['"].+?text/javascript.*?src=['"](.+?)['"]></script>'''
                    vid, getembed = re.findall(regex, r, re.DOTALL)[0]
                    #vid = re.findall(r'''fid=['"](.+?)['"]''', r, re.DOTALL)[0]
                    getembed = 'https:' + getembed if getembed.startswith('//') else getembed
                    embed = six.ensure_str(client.request(getembed))
                    embed = re.findall(r'''document.write.+?src=['"](.+?player)=''', embed, re.DOTALL)[0]
                    host = '{}=desktop&live={}'.format(embed, str(vid))
                    # xbmc.log('@#@l1l1HOST: %s' % host)
                    data = six.ensure_str(client.request(host, referer=referer))
                    # xbmc.log('@#@SDATA: %s' % data)
                    try:
                        link = re.findall(r'''return\((\[.+?\])\.join''', data, re.DOTALL)[0]
                    except IndexError:
                        link = re.findall(r'''file:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]

                    # xbmc.log('@#@STREAMMMMM111: %s' % link)
                    stream_url = link.replace('[', '').replace(']', '').replace('"', '').replace(',', '').replace('\/', '/')
                    # xbmc.log('@#@STREAMMMMM222: %s' % stream_url)
                    stream_url += '|Referer={}/&User-Agent={}'.format(host.split('embed')[0], quote(ua))

    elif any(i in url for i in ragnaru):
        headers = {'User-Agent': 'iPad'}
        # xbmc.log('@#@STREAMMMMM111: %s' % url)
        referer = 'https://liveon.sx/' if 'liveon' in url else url
        r = six.ensure_str(client.request(url, headers=headers, referer=referer))
        stream = client.parseDOM(r, 'iframe', ret='src')[-1]
        stream = 'https:' + stream if stream.startswith('//') else stream
        # xbmc.log('@#@STREAMMMMM111111: %s' % stream)
        rr = six.ensure_str(client.request(stream, headers=headers, referer=referer))
        # xbmc.log('@#@RRRDATA: %s' % rr)
        from resources.modules import jsunpack
        if '<script>eval' in rr:
            rr = six.ensure_text(rr, encoding='utf-8').replace('\t', '')
            # unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
            unpack = client.parseDOM(rr, 'script')
            unpack = [i for i in unpack if 'eval' in i][0]
            # xbmc.log("[{}] - STREAM-UNPACK: {}".format(ADDON.getAddonInfo('id'), str(unpack)))
            rr = jsunpack.unpack(str(unpack))
            # xbmc.log("STREAM-UNPACK: {}".format(str(rr)))
            if jsunpack.detect(rr) and not '.m3u8?':
                unpack = re.findall(r'''<script>(eval.+?\{\}\))\)''', rr, re.DOTALL)[0].strip()
                rr = jsunpack.unpack(str(unpack) + ')')
                # xbmc.log("STREAM-UNPACK22: {}".format(str(rr)))
            # elif 'eval(function' in rr:
            #     xbmc.log("MALAKASSSS")
            #     rr = jsunpack.unpack(str(rr))
            #     xbmc.log("STREAM-UNPACK222: {}".format(str(unpack)))
            else:
                rr = rr
            if 'player.src({src:' in rr:
                flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
                # xbmc.log('@#@STREAMMMMM: %s' % flink)
            elif 'hlsjsConfig' in rr:
                flink = re.findall(r'''src=\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
            elif 'new Clappr' in rr:
                flink = re.findall(r'''source\s*:\s*["'](.+?)['"]\,''', str(rr), re.DOTALL)[0]
            elif 'player.setSrc' in rr:
                flink = re.findall(r'''player.setSrc\(["'](.+?)['"]\)''', rr, re.DOTALL)[0]
            else:
                try:
                    flink = re.findall(r'''source:\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
                except IndexError:
                    ea = re.findall(r'''ajax\(\{url:\s*['"](.+?)['"],''', rr, re.DOTALL)[0]
                    ea = six.ensure_text(client.request(ea)).split('=')[1]
                    flink = re.findall('''videoplayer.src = "(.+?)";''', ea, re.DOTALL)[0]
                    flink = flink.replace('" + ea + "', ea)
            flink += '|Referer={}'.format(quote(stream))
            stream_url = flink
        else:

            if 'player.src({src:' in rr:
                flink = re.findall(r'''player.src\(\{src:\s*["'](.+?)['"]\,''', rr, re.DOTALL)[0]
                # xbmc.log('@#@STREAMMMMM: %s' % flink)
            elif 'Clappr.Player' in rr:
                flink = re.findall(r'''source\s*:\s*["'](.+?)['"]\,''', str(rr), re.DOTALL)[0]
                # xbmc.log('@#@STREAMMMMM: %s' % flink)

            elif 'hlsjsConfig' in rr:
                flink = re.findall(r'''src=\s*["'](.+?)['"]''', rr, re.DOTALL)[0]

            elif 'player.setSrc' in rr:
                flink = re.findall(r'''player.setSrc\(["'](.+?)['"]\)''', rr, re.DOTALL)[0]
            else:
                try:
                    flink = re.findall(r'''source:\s*["'](.+?)['"]''', rr, re.DOTALL)[0]
                except IndexError:
                    ea = re.findall(r'''ajax\(\{url:\s*['"](.+?)['"],''', rr, re.DOTALL)[0]
                    ea = six.ensure_text(client.request(ea)).split('=')[1]
                    flink = re.findall('''videoplayer.src = "(.+?)";''', ea, re.DOTALL)[0]
                    flink = flink.replace('" + ea + "', ea)
            flink += '|Referer={}'.format(quote(stream))
            stream_url = flink
        # r = six.ensure_str(client.request(url, referer=referer))
        # xbmc.log('@#@RRRDATA: %s' % r)
        # vid = re.findall(r'''fid=['"](.+?)['"]''', r, re.DOTALL)[0] #<script>fid='do4';
        # #ragnaru.net/embed.php?player='+embedded+'&live='+fid+'" '+PlaySize+' width='+v_width+' height='+v_height+'
        # host = 'https://ragnaru.net/jwembed.php?player=desktop&live={}'.format(str(vid))
        # data = six.ensure_str(client.request(host, referer=referer))
        # # xbmc.log('@#@SDATA: %s' % data)
        # try:
        #     link = re.findall(r'''return\((\[.+?\])\.join''', data, re.DOTALL)[0]
        # except IndexError:
        #     link = re.findall(r'''file:.*['"](http.+?)['"]\,''', data, re.DOTALL)[0]
        #
        # # xbmc.log('@#@STREAMMMMM111: %s' % link)
        # stream_url = link.replace('[', '').replace(']', '').replace('"', '').replace(',', '').replace('\/', '/')
        # # xbmc.log('@#@STREAMMMMM222: %s' % stream_url)
        # stream_url += '|Referer=https://ragnaru.net/&User-Agent={}'.format(quote(ua))
    elif '//bedsport' in url:
        r = six.ensure_str(client.request(url))
        frame = client.parseDOM(r, 'iframe', ret='src')[0]
        data = six.ensure_str(client.request(frame))
        # xbmc.log('@#@DATAAA: %s' % data)
        unpack = re.findall(r'''script>(eval.+?\{\}\))\)''', data, re.DOTALL)[0]
        # unpack = client.parseDOM(rr, 'script')
        # xbmc.log('UNPACK: %s' % str(unpack))
        # unpack = [i.rstrip() for i in unpack if 'eval' in i][0]
        from resources.modules import jsunpack
        data = six.ensure_text(jsunpack.unpack(str(unpack) + ')'), encoding='utf-8')
        # xbmc.log('@#@DATAAA: %s' % data)

    else:
        stream_url = url
    liz = xbmcgui.ListItem(name)
    liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty("IsPlayable", "true")
    liz.setPath(str(stream_url))
    if float(xbmc.getInfoLabel('System.BuildVersion')[0:4]) >= 17.5:
        liz.setMimeType('application/vnd.apple.mpegurl')
        liz.setProperty('inputstream.adaptive.manifest_type', 'hls')
        # liz.setProperty('inputstream.adaptive.stream_headers', str(headers))
    else:
        liz.setProperty('inputstreamaddon', None)
        liz.setContentLookup(True)
    xbmc.Player().play(stream_url, liz, False)
    quit()
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, liz)


def Open_settings():
    control.openSettings()


def addDir(name, url, mode, iconimage, fanart, description):
    u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(
        name) + "&iconimage=" + quote_plus(iconimage) + "&description=" + quote_plus(description)
    ok = True
    liz = xbmcgui.ListItem(name)
    liz.setArt({'poster': 'poster.png', 'banner': 'banner.png'})
    liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    liz.setProperty('fanart_image', fanart)
    if mode == 100:
        liz.setProperty("IsPlayable", "true")
        liz.addContextMenuItems([('GRecoTM Pair Tool', 'RunAddon(script.grecotm.pair)',)])
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    elif mode == 10 or mode == 'BUG' or mode == 4:
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    else:
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def get_params():
    param = []
    paramstring = [] #sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'): params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2: param[splitparams[0]] = splitparams[1]
    return param


def set_dummy_data():
    for r in range(0,5):
        row = []
        for i in range(0,5):
            row.append( EventData(r * 10 + i, "teams", "ftime",  "italy serie a", "streams", 'www.dummy.com/getpagedummy/football/football.png' ) )
        data_rows.append(row)
    pass
    
def postEvents(): 
    global ui
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    
    global base
    base.close()
    del base
    
    ui = GUI('script-testwindow.xml', ADDON_PATH, 'default', '720p', False, optional1='some data')

    #ui.addQuad(0)
    #refresh_selection()
    
    load_quads()
    
    # now open your window. the window will be shown until you close your addon
    ui.doModal()
    
    # window closed, now cleanup a bit: delete your window before the script fully exits
    del ui
    pass

if (__name__ == '__main__'):
    #######################################
    # Time and Date Helpers
    #######################################
    try:
        local_tzinfo = tzlocal()
        locale_timezone = json.loads(xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "locale.timezone"}, "id": 1}'))
        if locale_timezone['result']['value']:
            local_tzinfo = gettz(locale_timezone['result']['value'])
    except:
        pass

    params = get_params()
    url = BASEURL
    name = NAME
    iconimage = ICON
    mode = None
    fanart = FANART
    description = DESCRIPTION
    query = None
    ### 
    ### try:
    ###     url = unquote_plus(params["url"])
    ### except:
    ###     pass
    ### try:
    ###     name = unquote_plus(params["name"])
    ### except:
    ###     pass
    ### try:
    ###     iconimage = unquote_plus(params["iconimage"])
    ### except:
    ###     pass
    ### try:
    ###     mode = int(params["mode"])
    ### except:
    ###     pass
    ### try:
    ###     fanart = unquote_plus(params["fanart"])
    ### except:
    ###     pass
    ### try:
    ###     description = unquote_plus(params["description"])
    ### except:
    ###     pass
    ### try:
    ###     query = unquote_plus(params["query"])
    ### except:
    ###     pass
    ### 
    ### print(str(ADDON_PATH) + ': ' + str(VERSION))
    ### print("Mode: " + str(mode))
    ### print("URL: " + str(url))
    ### print("Name: " + str(name))
    ### print("IconImage: " + str(iconimage))
    ### #########################################################
    ### 
    
    #try:
    if mode == 999: #None:
        Main_menu()
    elif mode == 3:
        sports_menu()
    elif mode == 2:
        leagues_menu()
    elif mode == None:
        # Init display window object
        #initializeGUI()
        
        get_events(Live_url)
        #set_dummy_data()
        
        postEvents()
        mode = 21
    elif mode == 4:
        get_stream(url)
    elif mode == 10:
        Open_settings()
    elif mode == 14:
        get_livetv(url)
    elif mode == 15:
        get_new_events(url)

    elif mode == 100:
        resolve(url, name)
    #except:
    #    control.infoDialog("[COLOR red]Generic error. Please check the connection. Try Again Later![/COLOR]", NAME,


# the end!
