# -*- coding: utf-8 -*-
import base64
import re
import sys
import six
from six.moves.urllib.parse import urljoin, unquote_plus, quote_plus, quote, unquote
from six.moves import zip

import threading
import time

import json
import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

from PIL import Image

import pyxbmct
import requests
import os, sys
import xbmcplugin
from datetime import datetime as dt, timedelta

from urllib.parse import urlparse
from resources.modules import control, client
from dateutil.parser import parse
from dateutil.tz import gettz
from dateutil.tz import tzlocal

from resources.modules.soccer_data_api import soccer_api

from contextlib import closing
from xbmcvfs import File

soccer_data = soccer_api.SoccerDataAPI()

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

# Addon data dir
profile_dir = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))

#Dialog = xbmcgui.Dialog()
#base = xbmcgui.Window(xbmcgui.getCurrentWindowId())

vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

BASEURL = 'https://my.livesoccer.sx/'
Live_url = 'https://my.livesoccer.sx/'
Alt_url = 'https://liveon.sx/program'     #'https://1.livesoccer.sx/program'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

accepted_league = ['italy','coppa ','uefa ', 'moto', 'formula','england','spain', 'nba','germany','france','nederlands', 'mls']
nations = ['italy','england','spain','germany','france','nederlands']
filter = 'all'

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

item_selected = [0, 0]
data_rows = []

id_row = 0
item_sel = 0

ui = None

class EVENT(xbmcgui.WindowXMLDialog):
    # [optional] this function is only needed of you are passing optional data to your window
    def __init__(self, *args, **kwargs):
        global data_rows

        # get the optional data and add it to a variable you can use elsewhere in your script
        self.item = data_rows[item_selected[1]][item_selected[0]]
        self.lst = kwargs.get('optional1', None)
        self.sel = 0
        pass
    # until now we have a blank window, the onInit function will parse your xml file

    def onInit(self):
        bg = self.getControl(212)
        bg.setImage(profile_dir + self.item.getEventImage())

        self.sel = 0
        bgl = self.getControl(216)
        if 'b1.png' not in self.item.getLogoImage():
            bgl.setImage(profile_dir + self.item.getLogoImage())

        tit = self.getControl(213)
        hour = self.getControl(214)
        league = self.getControl(215)
        tit.setLabel(self.item.getTeams().upper())
        hour.setLabel(self.item.getFtime())
        league.setLabel(self.item.getOnlyLeagueName())

        self.lnk = self.getControl(222)

        self.appendList(self.lst)

        xbmc.executebuiltin('Control.SetFocus(10)')
        if len(self.lst) > 0:
            self.lnk.setLabel(self.lst[0])
        pass

    def onAction(self, action):
        if action.getId() == xbmcgui.ACTION_PREVIOUS_MENU or action.getId() == ACTION_BACK_MENU:
            self.close()
        elif action.getId() == xbmcgui.ACTION_MOVE_LEFT:
            self.sel = self.sel - 1
            if self.sel < 0:
                self.sel = len(self.lst) - 1
            self.lnk.setLabel(self.lst[self.sel])
        elif action.getId() == xbmcgui.ACTION_MOVE_RIGHT:
            self.sel = self.sel + 1
            if self.sel > len(self.lst) - 1:
                self.sel = 0
            self.lnk.setLabel(self.lst[self.sel])
        elif action.getId() in (ADDON_ACTION_MOUSE_LEFT_CLICK, ADDON_ACTION_MOUSE_MIDDLE_CLICK, ADDON_ACTION_MOUSE_RIGHT_CLICK, ACTION_SELECT_ITEM, ACTION_MOUSE_DOUBLE_CLICK, ADDON_ACTION_TOUCH_TAP):
            # Extract url
            u = self.lst[self.sel].split('|')
            resolve(u[1].strip(), self.item.getTeams().upper())#u[0].strip())
            self.close()
        else:
            super(EVENT, self).onAction(action)

    def appendList(self, lst):
        # Set links
        # Link list
        ls = self.getControl(10)
        for s in lst:
            lItem = xbmcgui.ListItem()
            text = s[s.find("(")+1:s.find(")")]
            lItem.setInfo( type="Video", infoLabels={ "Title": ""+ text +"", "OriginalTitle": "" + text + "" } )
            ls.addItem(lItem)
        
        xbmc.executebuiltin('Control.SetFocus(10)')
        pass

class SPLASH(xbmcgui.WindowXML):
    # [optional] this function is only needed of you are passing optional data to your window
    def __init__(self, *args, **kwargs):
        # get the optional data and add it to a variable you can use elsewhere in your script
        pass
    # until now we have a blank window, the onInit function will parse your xml file

    def onInit(self):
        pass
   
splash = SPLASH('splash.xml', ADDON_PATH, 'default', '720p', False, optional1='some data')
   
# add a class to create your xml based window
class GUI(xbmcgui.WindowXML):
    # [optional] this function is only needed of you are passing optional data to your window
    def __init__(self, *args, **kwargs):
        # get the optional data and add it to a variable you can use elsewhere in your script
        self.data = kwargs['optional1']
        self.ignore_action_later = False
        
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

        #xbmc.log('boxss ' + str(len(self.lists)),xbmc.LOGERROR)
       
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
        listitem.setInfo( type="Video", infoLabels={ "Title": "" + _data.getTeams().upper() + "", "OriginalTitle": "" + _data.getFtime() + "", "Album": "" + _data.getEventImage() + "" }   )
        today = dt.today()
        tdy = today.strftime("%Y-%m-%d")
        if _data.getDate().lower().strip() != tdy:
            listitem.setArt({ 'poster' : 'BBFFFF00'})
            listitem.setArt({ 'landscape' : _data.getDate()})
        else:
            listitem.setArt({ 'poster' : '00000000'})
            listitem.setArt({ 'landscape' : ''})

        _data.setOnlyLeagueName(_data.getLeagueName())
        for r in nations:
            _data.setOnlyLeagueName(_data.getOnlyLeagueName().lower().replace(r, ''))
        _data.setOnlyLeagueName(_data.getOnlyLeagueName().strip().upper())
        
        listitem.setLabel(_data.getOnlyLeagueName())
        self.data[row].append(_data)
        self.lists[row].append(listitem)
        self.gui_rows[row].addItem(listitem) 
        self.gui_rows[row].setVisible(True)
        pass

    def searchImageByDesc(self, desc,isLogo=False,r=-1,i=-1,flname=''):

        # ASYNC REQUEST
        t1 = threading.Thread(target=lambda: self.searchImageByDescAsync(desc,isLogo,r,i,flname))
        #Background thread will finish with the main program
        t1.setDaemon(True)
        t1.start()
        pass

    def searchImageByDescAsync(self, desc, isLogo=False,r=-1,i=-1,flname=''):
        global data_rows
        urls = []

        try:
            if isLogo:
                re = requests.get("https://api.qwant.com/v3/search/images",
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
                re = requests.get("https://api.qwant.com/v3/search/images",
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
            
            response = re.json().get('data').get('result').get('items')
            urls = [re.get('media') for re in response]
            #xbmc.log(str(urls[0]), xbmc.LOGERROR)
        except:
            log('error qwant img')
            urls = None

        try:
            if (False == isLogo):
                if urls != None and len(urls) > 0:
                    if is_url_image(urls[0]):
                        # download
                        response = requests.get(urls[0])
                        fname = str(abs(hash(urls[0])))
                        with open(profile_dir + 'events/' + fname, "wb") as f:
                            f.write(response.content)
                        data_rows[r][i].setEventImage('events/' + fname)
                        self.lists[r][i].setArt({ 'thumb' : profile_dir + 'events/' + fname})
                    
                    save_events_data()
            else:
                if False or urls != None and len(urls) > 0:
                    # save
                    response = requests.get(urls[0])
                    with open(profile_dir + flname + "_org", "wb") as f:
                        f.write(response.content)
                    
                    # load
                    im = Image.open(profile_dir + flname + "_org") 
                    newsize = (128, 128)
                    im = im.resize(newsize)#, Resampling.BICUBIC)
                    im.save(profile_dir + flname) 

                    data_rows[r][i].setLogoImage(flname)
                    self.lists[r][i].setArt({ 'clearlogo' : profile_dir + flname})
        except:
            log('error appling img')

        pass

    def applyContextualImages(self):
        global data_rows
        
        # Init events folder
        if not os.path.exists(profile_dir + 'events/'):
            os.makedirs(profile_dir + 'events/')
        if not os.path.exists(profile_dir + 'leagues/'):
            os.makedirs(profile_dir + 'leagues/')

        # Apply contextual image if present   
        for r in range(0, len(self.data)):
            for i in range(0, len(self.data[r])):
                urls = []
                
                mydata = self.data[r][i]
                
                # If preset, apply it...
                if data_rows[r][i].getEventImage() != 'icons/b1.png':
                    self.lists[r][i].setArt({ 'thumb' : profile_dir + data_rows[r][i].getEventImage()})
                else:
                    # else, look for it in the web
                    a = urlparse(mydata.getLogo_league())
                    
                    # ASYNC SEARCH
                    if 'football' in a.path:
                        self.searchImageByDesc(mydata.getTeams() + ' ' + ' site:www.goal.com', False, r, i, '')
                    else:
                        self.searchImageByDesc(mydata.getTeams() + ' ' + mydata.getLeagueName(), False, r, i, '')

                # Apply contextual image if present
                flname = 'leagues/' + mydata.getOnlyLeagueName() + '.png'
                if os.path.exists(profile_dir + flname): #data_rows[r][i].getLogoImage() != 'icons/empty.png':
                    self.lists[r][i].setArt({ 'clearlogo' : profile_dir + flname})
                    data_rows[r][i].setLogoImage(flname)
                else:
                    self.searchImageByDesc(mydata.getOnlyLeagueName() + ' logo png',True, r, i, flname)
        pass
        
    def onAction(self, action):

        if self.ignore_action_later == True:
            self.ignore_action_later = False
            return
            
        if action.getId() == xbmcgui.ACTION_MOVE_LEFT:
            move_left()
        elif action.getId() == xbmcgui.ACTION_MOVE_RIGHT:
            move_right()
        elif action.getId() == xbmcgui.ACTION_MOVE_UP:
            move_up()
        elif action.getId() == xbmcgui.ACTION_MOVE_DOWN:
            move_down()
        elif action.getId() in (ADDON_ACTION_MOUSE_LEFT_CLICK, ADDON_ACTION_MOUSE_MIDDLE_CLICK, ADDON_ACTION_MOUSE_RIGHT_CLICK, ACTION_SELECT_ITEM, ACTION_MOUSE_DOUBLE_CLICK, ADDON_ACTION_TOUCH_TAP):
            if item_selected[1] >= 0:
                get_stream(self.data[item_selected[1]][item_selected[0]].getStreams()) 
        else:
            super(GUI, self).onAction(action)

        pass
    
    def onClick(self, controlId):
        global item_selected
        if item_selected[1] == -1:
            self.ignore_action_later = True
        else:
            self.ignore_action_later = False
        if controlId == 201:
            refresh('all')
        if controlId == 202:
            refresh('serie a')
        if controlId == 203:
            refresh('premier')
        if controlId == 204:
            refresh('la liga')
        if controlId == 205:
            refresh('bundesliga')
        if controlId == 206:
            refresh('ligue 1')
        if controlId == 207:
            refresh('update')
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
    def __init__( self, _id_row, _teams, _home, _away, _ftime, _lname, _streams, _logo_league, _date = 'today', _eventImage = 'icons/b1.png', _logoImage = 'icons/empty.png'):
        # Text path
        if 'inter milan' in _home.lower():
            _home = _teams.replace('Inter Milan','Inter')
        if 'inter milan' in _away.lower():
            _away = _teams.replace('Inter Milan','Inter')
            
        if 'moto' in _lname.lower() or 'formula' in _lname.lower():
            self.teams = _teams
        else:
            self.teams = _home + ' - ' + _away

        self.id_row = _id_row 
        self.home = _home
        self.away = _away
        self.ftime = _ftime
        self.lname = _lname
        self.streams = _streams
        self.logo_league = _logo_league
        self.onlyleague = ''

        if _date == 'today':
            today = dt.now()
            _date = today.strftime("%Y-%m-%d")
        self.datee = _date
        self.event_image = _eventImage
        self.logoImage = _logoImage
    
    # Setters
    def setIdRow(self, ri):
        self.id_row = ri 
    def setLogoImage(self, lg):
        self.logoImage = lg
    def setEventImage(self, lg):
        self.event_image = lg
    def setStreams(self, s):
        self.streams = s
    def setOnlyLeagueName(self, n):
        self.onlyleague = n
        
    # Getters    
    def getIdRow(self):
        return self.id_row
    def getHome(self):
        return self.home
    def getAway(self):
        return self.away
    def getTeams(self):
        return self.teams
    def getFtime(self):
        return self.ftime
    def getEventImage(self):
        return self.event_image
    def getLogoImage(self):
        return self.logoImage
    def getLeagueName(self):
        return self.lname
    def getDate(self):
        return self.datee
    def getStreams(self):
        return self.streams
    def getLogo_league(self):
        return self.logo_league
    def getOnlyLeagueName(self):
        return self.onlyleague

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

# Engine 
def is_url_image(image_url):
    try:
        image_formats = ("image/png", "image/jpg")
        r = requests.head(image_url)
        if r.headers["content-type"] in image_formats:
            return True
    except:
        return False
    return False

# GUI EVENTs
def move_left():
    global item_sel

    if item_selected[1] == -1:
        return

    item_selected[0] = item_selected[0] - 1

    item_sel = item_sel - 1
    refresh_selection()
    pass

def move_right():
    global item_sel
    
    if item_selected[1] == -1:
        return

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
    
    #log (item_selected)

    # Default grid check
    if len(ui.gui_rows) <= 0:
        return
    
    # Move Up/down check limit
    if item_selected[1] < -1:
        item_selected[1] = -1
    if item_selected[1] > ui.getVisibleRow() - 1:
        item_selected[1] = ui.getVisibleRow() - 1
    
    if item_selected[1] == -1:
        return
        
    # Move Left/right check limit
    if item_selected[0] < 0:
        item_selected[0] = 0
    if item_selected[0] > len(ui.data[item_selected[1]]) - 1:
        item_selected[0] = len(ui.data[item_selected[1]]) - 1
    
    # List selection
    if item_sel > item_selected[0]:
        item_sel = item_selected[0]
        
    focused_row = (item_selected[1]) * 10 + 10
    if item_sel < 0:
        item_sel = 0
    
    if item_sel > 2:
        item_sel = 2

    #for i in range(0, ui.getVisibleRow() - 1):
    #    xbmc.executebuiltin('Control.SetFocus('+ str(i * 10 + 10) + ', ' + str(item_sel) + ')')
    # Set focus (sync way)
    #    if ui.gui_rows[i].isVisible():
    #        ui.setFocus(ui.gui_rows[i], 1)

    xbmc.executebuiltin('Control.SetFocus('+ str(focused_row) + ', ' + str(item_sel) + ')')
    
    pass

def load_quads():
    t1 = threading.Thread(target=load_quads_backgroundWorker)
    #Background thread will finish with the main program
    t1.setDaemon(True)
    t1.start()
    pass
   

#Routine that processes whatever you want as background
def load_quads_backgroundWorker(): 
    # Wait for gui init
    xbmc.sleep(2000)

    #splash.close()
    draw_page()
    pass

def draw_page():
    global ui
    global splash
    global filter
    global data_rows
    # ADD TO GUI the quads
    row = 0
    for r in data_rows:
        # Draw filtered content
        if filter == 'all':
            for i in r:
                ui.addQuad(row, i)
            row = row + 1
        elif filter in r[0].getLeagueName().lower():
            for i in r:
                ui.addQuad(row, i)
            row = row + 1
    
    # Find, if exist, the first focusable row and focus it
    for i in range(0, 10):
        if ui.gui_rows[i].isVisible():
            ui.setFocus(ui.gui_rows[i])
            item_selected[1] = i
            break
    #log(filter)

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

def get_events(url):  # 5
    #xbmc.log('%s: {}'.format(url))
    #xbmc.log(url, xbmc.LOGERROR)
    global soccer_data
    global id_row

    data_r = []

    id_row = 0

    data = client.request(url)
    data = six.ensure_text(data, encoding='utf-8', errors='ignore')
    data = re.sub('\t', '', data)
    # xbmc.log('@#@EDATAAA: {}'.format(data))
    events = list(zip(client.parseDOM(data, 'li', attrs={'class': "item itemhov"}),
                      client.parseDOM(data, 'li', attrs={'class': "bahamas"})))
                      # re.findall(r'class="bahamas">(.+?)</span> </div> </li>', str(data), re.DOTALL)))
    # addDir('[COLORwhite]Time in GMT+2[/COLOR]', '', 'BUG', ICON, FANART, '')
    for event, streams in events:
        log(event)
        # xbmc.log('@#@EVENTTTTT:%s' % event)
        # xbmc.log('@#@STREAMS:%s' % streams)
        watch = '[COLORlime]*[/COLOR]' if '>Live<' in event else '[COLORred]*[/COLOR]'
        home = ''
        away  = ''
        try:
            teams = client.parseDOM(event, 'td')
            # xbmc.log('@#@TEAMSSSS:%s' % str(teams))
            home, away = re.sub(r'\s*(<img.+?>)\s*', '', client.replaceHTMLCodes(teams[0])),\
                re.sub(r'\s*(<img.+?>)\s*', '', client.replaceHTMLCodes(teams[2]))
            if six.PY2:
                home = home.strip().encode('utf-8')
                away = away.strip().encode('utf-8')
            teams = '[B]{0} - {1}[/B]'.format(home, away)
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
        dta = client.parseDOM(event, 'span', attrs={'class': 'gmt_m_time'}, ret = "mtime")[0]
        #log(dta)
        ffff = dt.fromtimestamp(int(dta)/1000)
        ddate = ffff.strftime('%Y-%m-%d')
        #log(ddate)
        time = time.split('GMT')[0].strip()
        #log(time)
        cov_time = convDateUtil(time, 'default', 'GMT+2')#.format(str(control.setting('timezone'))))
        ftime = '{}'.format(cov_time)
        name = '{0}{1} [COLORgold]{2}[/COLOR] - [I]{3}[/I]'.format(watch, ftime, teams, lname)

        # links = re.findall(r'<a href="(.+?)".+?>( Link.+? )</a>', event, re.DOTALL)
        streams = str(quote(base64.b64encode(six.ensure_binary(streams))))

        icon = client.parseDOM(event, 'img', ret='src')[0]
        icon = urljoin(BASEURL, icon)
 
        logo_league = icon
        
        #addDir(name, streams, 4, icon, FANART, name)
        appended = False      
        for r in data_r:
            if r[0].getLeagueName() == lname:
                r.append( EventData(r[0].getIdRow(), teams, home, away, ftime,  lname, streams, logo_league, ddate) )
                appended = True
                break
        if appended == False:
            new_r = []
            new_r.append( EventData(id_row, teams, home, away, ftime,  lname, streams, logo_league, ddate) )
            data_r.append(new_r)
            id_row = id_row + 1
                
    #log(len(data_r)) 
    return data_r

def log(strng):
    xbmc.log(str(strng), xbmc.LOGERROR)

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

def get_stream(url):  # 4
    
    if url == '':
        control.infoDialog("[COLOR green]No Links available ATM.\n [COLOR lime]Try Again Later![/COLOR]", NAME,
                   iconimage, 5000)
        return

    data = six.ensure_text(base64.b64decode(unquote(url))).strip('\n')
    # xbmc.log('@#@DATAAAA: {}'.format(data))
    if 'info_outline' in data:
        control.infoDialog("[COLOR green]No Links available ATM.\n [COLOR lime]Try Again Later![/COLOR]", NAME,
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
                
        # Append link to event gui
        event = EVENT('event.xml', ADDON_PATH, 'default', '720p', optional1=titles)
        #event.appendList(titles)
        
        event.doModal()
        del event
        return
        
#        if len(streams) > 1:
#            dialog = xbmcgui.Dialog()
#            ret = dialog.select('[COLORgold][B]Choose Stream[/B][/COLOR]', titles)
#            if ret == -1:
#                return
#            elif ret > -1:
#                host = streams[ret]
#                # xbmc.log('@#@STREAMMMMM:%s' % host)
#                return resolve(host, name)
#            else:
#                return False
#        else:
#            link = links[0][0]
#            return resolve(link, name)
    pass

def resolve(url, name):
    global ui
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
        #quit()
        #ui.hide()

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
    #quit()
    #ui.hide()

    #log(sys.argv[1])
    #xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, liz)

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
    for r in range(0,1):
        row = []
        for i in range(0,1):
            row.append( EventData(r * 10 + i, "teams", "home", "away", "ftime",  "spain segunda", "streams", 'www.dummy.com/getpagedummy/football/football.png' ) )
        data_rows.append(row)
    pass
    
def postEvents(): 
    global ui
    #xbmc.executebuiltin('Dialog.Close(busydialog)')
    
    #global base
    #base.close()
    #del base
    
    ui = GUI('main.xml', ADDON_PATH, 'default', '720p', False, optional1='some data')

    #ui.addQuad(0)
    #refresh_selection()
    
    load_quads()
    
    # now open your window. the window will be shown until you close your addon
    ui.doModal()
    
    splash.close()
    
    # window closed, now cleanup a bit: delete your window before the script fully exits
    del ui
    pass

def refresh(_type):
    global ui
    global data_rows
    global filter
    
    # Clear the page
    id = 0
    for r in data_rows:
        ui.gui_rows[id].reset()
        ui.gui_rows[id].setVisible(False)
        id = id + 1
    item_selected = [0, -1]
    
    # Apply the filter
    if _type == 'update':
        data_rows.clear()
        data_rows = []
        get_events(Live_url)
        filter = 'all'
    else:
        filter = _type
    
    load_quads()
    pass

def save_events_data():
    global data_rows

    json_string = []
    for r in data_rows:
        j_s = []          
        for i in r:
            j_s.append(json.dumps(i.toJson()))
        json_string.append(json.dumps(j_s))
            
    with closing(xbmcvfs.File(profile_dir + '/data.dat','wb')) as fn:
        fn.write(bytearray(json.dumps(json_string).encode('utf-8')))
    pass

def integrate_data_rows_with(_data_rws, update_streams = True):
    global data_rows
    for r in _data_rws:
        for event in r:
            found = False
            # For every event, search inside data_rows event
            for dr in data_rows:
                for d_event in dr:
                    if event.getHome() in d_event.getHome():
                        # update streams
                        if update_streams:
                            d_event.setStreams(event.getStreams())
                        found = True
                        break
                if found == True:
                    break
            if found == False:
                # Add it to the appropriate row
                for adr in data_rows:
                    if len(adr) > 0 and adr[0].getLeagueName() in event.getLeagueName():
                        adr.insert(0, event)
                        found = True
                        break
            if found == False:
                # Add a new row with this event
                new_r = []
                new_r.append(event)
                data_rows.append(new_r)
    pass

def purge_data_rows():
    global data_rows

    # Draw data
    ri = 0
    now = dt.now() - timedelta(hours=3)
    #log(now)
    d_r = []

    for r in data_rows:
        sr = []
        for i in r:
            datetime_str = i.getDate() + ' ' + i.getFtime() #['datee'] + ' ' + d['ftime']
            # log(datetime_str)
            #datetime_object = dt.strptime(str(datetime_str), "%Y-%m-%d %H:%M")
            try:
                datetime_object = dt.strptime(datetime_str, "%Y-%m-%d %H:%M")
            except TypeError:
                datetime_object = dt(*(time.strptime(datetime_str, "%Y-%m-%d %H:%M")[0:6]))

            if datetime_object > now:
                #"teams": "Hellas Verona - Napoli", "ftime": "15:00", "lname": "italy serie a", "streams": "not available yet", "logo_league": "serie a", "onlyleague": "", "datee": "2023-10-21"}
                # id_row, _teams, _home, _away, _ftime, _lname, _streams, _logo_league, _date
                i.setIdRow(ri)
                sr.append(i) #EventData(ri, d['teams'], d['home'], d['away'], d['ftime'], d['lname'], d['streams'], d['logo_league'], d['datee'],d['event_image'],d['logoImage']))
                ri = ri + 1
            else:
                # delete the associated data
                try:
                    os.remove(profile_dir + i.getEventImage()) # d['event_image'])
                except:
                    log(i.getEventImage() + ' not found')    
        if len(sr):
            d_r.append(sr)

        data_rows = d_r
    pass

def get_calendar_events():
    data_r = []

    id_row = 0
    # Initialize with next week games for major leagues
    #xbmc.log(str(soccer_data.serie_a_next_turn()), xbmc.LOGERROR)
    if len(data_r) == 0:
        r = []
        for game in soccer_data.serie_a_next_turn():
            r.append( EventData(id_row, '', game['home'], game['away'], game['time'], 'italy serie a', '', 'serie a', game['date']) )
        data_r.append(r)
        id_row = id_row + 1
        r = []
        for game in soccer_data.premier_league_next_turn():
            r.append( EventData(id_row, '', game['home'], game['away'], game['time'], 'england premier league', '', 'premier league', game['date']) )
        data_r.append(r)
        id_row = id_row + 1
        r = []
        for game in soccer_data.la_liga_next_turn():
            r.append( EventData(id_row, '', game['home'], game['away'], game['time'], 'spain la liga', '', 'la liga', game['date']) )
        data_r.append(r)
        id_row = id_row + 1
    
    return data_r

def sort_data_events(data_r):   
    # SORT data_row
    #re.search(sort_priority[i_sort], r[0].getLeagueName().lower())
    data_r2 = []
    for a in accepted_league:
        filtered_row = []
        accepted = False
        for r in data_r:
            i_i = 0
            accepted = False
            for i in r:
                # Accept only selected events
                if a in i.getLeagueName().lower():
                    accepted = True
                if accepted:
                    filtered_row.append(i)
            if accepted:
                break
        if accepted:
            # Order each row by date
            filtered_row.reverse()
            data_r2.append(filtered_row)
        
    return data_r2

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
    
    #try:
    if mode == None:
        # Splash
        splash.show()

        # Init data rows
        data_rows.clear()

        # Get calendar data
        calendar_rows = get_calendar_events()

        # Get new event data
        data_rws = get_events(Live_url)

        # Addon data dir
        profile_dir = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
     
        # Check if data exist
        text = ''
        with closing(xbmcvfs.File(profile_dir + '/data.dat','r')) as fo:
            text = fo.read()

        if text != '':
            # Load json data
            d_r = []
            d_r = json.loads(text)
            ri = 0
            for r in d_r:
                ss = json.loads(r)
                sr = []
                for i in ss:
                    ed = json.loads(i)
                    #log(ed)
                    d =  json.loads(ed)
                    # id_row, _teams, _home, _away, _ftime, _lname, _streams, _logo_league, _date
                    sr.append(EventData(ri, d['teams'], d['home'], d['away'], d['ftime'], d['lname'], d['streams'], d['logo_league'], d['datee'],d['event_image'],d['logoImage']))
                ri = ri + 1
                data_rows.append(sr)

        # Is data up to date? Part 1
        purge_data_rows()

        # Integrate with new events from calendar
        integrate_data_rows_with(calendar_rows, False)

        # Integrate with new available events
        integrate_data_rows_with(data_rws, True)

        # Is data up to date? Part 2 
        purge_data_rows()

        data_rows = sort_data_events(data_rows)
            
        # Save events
        save_events_data()

        postEvents()
        mode = 21
#    elif mode == 4:
#        get_stream(url)
    elif mode == 10:
        Open_settings()
    elif mode == 100:
        resolve(url, name)
    #except:
    #    control.infoDialog("[COLOR red]Generic error. Please check the connection. Try Again Later![/COLOR]", NAME,


# the end!
