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

ADDON = xbmcaddon.Addon()
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

vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

BASEURL = 'https://my.livesoccer.sx/'
Live_url = 'https://my.livesoccer.sx/'
Alt_url = 'https://liveon.sx/program'#'https://1.livesoccer.sx/program'
headers = {'User-Agent': client.agent(),
           'Referer': BASEURL}

from dateutil.parser import parse
from dateutil.tz import gettz
from dateutil.tz import tzlocal

# reload(sys)
# sys.setdefaultencoding("utf-8")

accepted_league = ['italy','england','spain','germany','france','nederlands']

STATE = 'close'
addon_handle = int(sys.argv[1])
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

# Page grid
offset_page_top = 140
offset_page_left = 80
page_blur = 130
alpa = '0x75FFFFFF'

# Item
width = 370
height = 220
offset_w = 5
offset_h = 5

rows_item_count = []

item_selected = [0, 0]
rows = []
data_rows = []

row_items_count = []
id_row = 0

base = xbmcgui.Window(xbmcgui.getCurrentWindowId())

gui_images = []
gui_images_used = 0
def get_available_gui_image(x, y, width, height, filename=ART+'empty.png', aspectRatio=1, colorDiffuse='0xFFFFFFFF'):
    global gui_images_used
    global gui_images
    gui_images_used = gui_images_used + 1
    ret = gui_images[gui_images_used]
    ret.setPosition(x,y)
    ret.setWidth(width)
    ret.setHeight(height)
    ret.setImage(filename)
    ret.setColorDiffuse(colorDiffuse)
    #ret.setAspectRatio(aspectRatio)
    return ret

gui_labels_s = []
gui_labels_s_used = 0
def get_available_gui_label_s(x, y, width, height, text, font='font10', textColor='0xFF000000'):
    global gui_labels_s_used
    global gui_labels_s
    gui_labels_s_used = gui_labels_s_used + 1
    ret = gui_labels_s[gui_labels_s_used]
    ret.setPosition(x,y)
    ret.setWidth(width)
    ret.setHeight(height)
    ret.setLabel(text)
    return ret
 
gui_labels_w = []
gui_labels_w_used = 0
def get_available_gui_label_w(x, y, width, height, text, font='font10', textColor='0xFF000000'):
    global gui_labels_w_used
    global gui_labels_w
    gui_labels_w_used = gui_labels_w_used + 1
    ret = gui_labels_w[gui_labels_w_used]
    ret.setPosition(x,y)
    ret.setWidth(width)
    ret.setHeight(height)
    ret.setLabel(text)
    return ret
  
# Main code
class Main(pyxbmct.BlankFullWindow):
    def __init__( self):
        # Call the base class' constructor.
        super(Main, self).__init__()

        global base
        global gui_images
        
        base = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        
        self.setGeometry(1280, 720, 1, 1)

        self.main_bg = xbmcgui.ControlImage(0, 0, 1280, 720, ART + 'bg.png')
        self.addControl(self.main_bg)
        
        for x in range(0, 150):
            dummy = xbmcgui.ControlImage(0, 0, 2, 2, filename=ART+'empty.png') #, aspectRatio=1)
            gui_images.append(dummy)
            self.addControl(dummy)

        for x in range(0, 150):
            dummy = xbmcgui.ControlLabel(0, 0, 2, 2, '', textColor='0xFF000000', font='font10')
            gui_labels_s.append(dummy)
            self.addControl(dummy)

        for x in range(0, 150):
            dummy = xbmcgui.ControlLabel(0, 0, 2, 2, '', textColor='0xFFFFFFFF', font='font10')
            gui_labels_w.append(dummy)
            self.addControl(dummy)
            
        #self.setFocus(self.main_bg)
    #def onInit(self):
    #    xbmc.log('do Modal', xbmc.LOGERROR)

    def onAction(self, action):
        super(Main, self).onAction(action)
        #xbmc.log('foc', xbmc.LOGERROR)
        #pyxbmct.BlankFullWindow.onAction(self, action)

        if action.getId() == 107:
#            self.close()
            closeAddon()     
        if action.getId() == ACTION_PREVIOUS_MENU:
#            self.close()
            closeAddon()     
        if action.getId() == ACTION_PREVIOUS_MENU:
#            self.close()
            closeAddon()   
        elif action.getId() == ACTION_BACK_MENU:
#            self.close()
            closeAddon()   
        elif action.getId() == pyxbmct.ACTION_NAV_BACK:
#            self.close()
            closeAddon()   
        elif action.getId() in (ADDON_ACTION_MOUSE_LEFT_CLICK, ADDON_ACTION_MOUSE_MIDDLE_CLICK, ADDON_ACTION_MOUSE_RIGHT_CLICK, ACTION_SELECT_ITEM, ACTION_MOUSE_DOUBLE_CLICK, ADDON_ACTION_TOUCH_TAP):
            get_stream(rows[item_selected[1]][item_selected[0]].getEventData().getStreams())   
        #else:
        #    pyxbmct.BlankFullWindow.onAction(self, action)

    def onClick(self, control_id):
        get_stream(rows[item_selected[1]][item_selected[0]].getEventData().getStreams())   

    
class Quad():
    def __init__( self, x, y, event_data):
        
        # Init GUI quad
        global mydisplay
        self.data = event_data
        self.row_offset = 0

        self.g_items = []
        logoChampSize = 64
        logoLeague = 56
        wBarHeight = 30
        
        self.bg = get_available_gui_image(x, y, width, height, filename=ART+'b1.png', aspectRatio=1)# xbmcgui.ControlImage(x, y, width, height, filename=ART+'b1.png', aspectRatio=1)
        #mydisplay.addControl(self.bg)
        self.g_items.append(self.bg)

        self.selected = xbmcgui.ControlImage(x, y, width, height, filename=ART+'b2.png')
        self.selected.setVisible(False)
        mydisplay.addControl(self.selected)
        self.g_items.append(self.selected)

        whiteBar = get_available_gui_image(x, y + height - wBarHeight, width - logoChampSize, wBarHeight, filename=ART+'bw.png')
        #mydisplay.addControl(whiteBar)
        self.g_items.append(whiteBar)

        blackBack = get_available_gui_image(x, y + height - wBarHeight - 60, width, 60, filename=ART+'bw.png', colorDiffuse='0xBB000000')
        #mydisplay.addControl(blackBack)
        self.g_items.append(blackBack)

        whiteBack = get_available_gui_image(x + width - logoChampSize, y + height - logoChampSize, logoChampSize, logoChampSize, filename=ART+'bw.png')
        #mydisplay.addControl(whiteBack)
        self.g_items.append(whiteBack)

        matchShadow = get_available_gui_label_s(x + 10 - 1, y + height - 87 + 1, width - 20, 30, event_data.getTeams().upper(), font='font10', textColor='0xFF000000') #xbmcgui.ControlLabel(x + 10 - 1, y + height - 87 + 1, width - 20, 30, event_data.getTeams().upper(), font='font10', textColor='0xFF000000')
        #mydisplay.addControl(matchShadow)
        self.g_items.append(matchShadow)
        
        match = get_available_gui_label_w(x + 10, y + height - 87, width - 20, 30, event_data.getTeams().upper(), font='font10')
        #mydisplay.addControl(match)
        self.g_items.append(match)

        hour = get_available_gui_label_w(x + 10, y + height - 60, width - 20, 30, event_data.getFtime().upper(), font='font10')
        #mydisplay.addControl(hour)
        self.g_items.append(hour)

        league = get_available_gui_label_s(x + 10, y + height - 27, width - 20, 30, '', font='font10', textColor='0xFF000000')
        self.onlyleague = event_data.getLname()
        for r in accepted_league:
            self.onlyleague = self.onlyleague.lower().replace(r, '')
        league.setLabel(self.onlyleague.strip().upper())
        #mydisplay.addControl(league)
        self.g_items.append(league)
                
        self.logo = get_available_gui_image(x + width - int(logoChampSize/2 + logoLeague/2), y + height - int(logoChampSize/2 + logoLeague/2), logoLeague, logoLeague, filename= event_data.getLogo_league(), colorDiffuse='0xFF000000', aspectRatio=2) #ART+'bundesliga.png')
        #mydisplay.addControl(self.logo)
        self.g_items.append(self.logo)
 
    def applyContextualImages(self):
        # Apply contextual image if present
        urls = []
        
        a = urlparse(self.data.getLogo_league())
        #xbmc.log(str(a.path), xbmc.LOGERROR)
        if 'football' in a.path:
            urls = searchImageByDesc(self.data.getTeams() + ' ' + self.data.getLname() + ' site:goal.com')
        else:
            urls = searchImageByDesc(self.data.getTeams() + ' ' + self.data.getLname())
        if urls != None and len(urls) > 0:
            if is_url_image(urls[0]):
                self.bg.setImage(urls[0])
            #elif is_url_image(urls[1]):    
            #    self.bg.setImage(urls[1])

        # Apply contextual image if present
        urls = searchImageByDesc(self.onlyleague + ' logo png',True)
        if urls != None and len(urls) > 0:
            self.logo.setImage(urls[0])
            self.logo.setColorDiffuse('0xFFFFFFFF')
        pass

    def getEventData(self):
        return self.data
        
    def setSelected(self, state):
        self.selected.setVisible(state)
        
    def moveRight(self):
        for i in self.g_items:
            i.setPosition(i.getX() + width + offset_w, i.getY())

    def moveLeft(self):
        for i in self.g_items:
            i.setPosition(i.getX() - width - offset_w, i.getY())

    def moveUp(self):
        for i in self.g_items:
            i.setPosition(i.getX(), i.getY() - (height + offset_h))

    def moveDown(self):
        for i in self.g_items:
            i.setPosition(i.getX(), i.getY() + (height + offset_h))
    
    def getX(self):
        return self.bg.getX()

    def getY(self):
        return self.bg.getY()

    def getH(self):
        return self.bg.getHeight()
         
    def getW(self):
        return self.bg.getWidth()


class EventData():
    def __init__( self, id_row, _teams, _ftime, _lname, _streams, _logo_league):
        self.teams = _teams
        self.ftime = _ftime
        self.lname = _lname
        self.streams = _streams
        self.logo_league = _logo_league
        
    def getTeams(self):
        return self.teams
    def getFtime(self):
        return self.ftime
    def getLname(self):
        return self.lname
    def getStreams(self):
        return self.streams
    def getLogo_league(self):
        return self.logo_league

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
                    'device': 'desktop'
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
    item_selected[0] = item_selected[0] - 1 #new_r_offset# - old_r_offset

    refresh_selection()
    pass

def move_right():
    # Get the row offset (if row is shifted to center content)
    #new_r_offset = rows[item_selected[1]][0].row_offset # Use the first item of the list to get the row offset
    item_selected[0] = item_selected[0] + 1 #new_r_offset# - old_r_offset

##    # Get the row offset (if row is shifted to center content)
##    old_r_offset = rows[item_selected[1]][0].row_offset # Use the first item of the list to get the row offset
##    # Get the row offset (if row is shifted to center content)
##    n_r_offset = rows[item_selected[1]][0].row_offset # Use the first item of the list to get the row offset
    
    refresh_selection()
    pass

def move_up():
    old_r_offset = rows[item_selected[1]][0].row_offset # Use the first item of the list to get the row offset

    item_selected[1] = item_selected[1] - 1
    if item_selected[1] < 0:
        item_selected[1] = 0

    new_r_offset = rows[item_selected[1]][0].row_offset # Use the first item of the list to get the row offset

    item_selected[0] = item_selected[0] + new_r_offset - old_r_offset

    refresh_selection()
    pass

def move_down():
    old_r_offset = rows[item_selected[1]][0].row_offset # Use the first item of the list to get the row offset

    item_selected[1] = item_selected[1] + 1
    if item_selected[1] > len(rows) - 1:
        item_selected[1] = len(rows) - 1

    new_r_offset = rows[item_selected[1]][0].row_offset # Use the first item of the list to get the row offset

    item_selected[0] = item_selected[0] + new_r_offset - old_r_offset
    
    refresh_selection()
    pass
    
def initializeGUI():
    global mydisplay
    mydisplay = Main()

    pass

def refresh_selection():
    if len(rows) <= 0:
        return
        
    if item_selected[1] < 0:
        item_selected[1] = 0
    if item_selected[1] > len(rows) - 1:
        item_selected[1] = len(rows) - 1

    if item_selected[0] < 0:
        item_selected[0] = 0

    #xbmc.log(str(row_items_count[item_selected[1]]), xbmc.LOGERROR)
    #xbmc.log(str(item_selected[0]), xbmc.LOGERROR)
    if item_selected[0] > row_items_count[item_selected[1]] - 1:
        item_selected[0] = row_items_count[item_selected[1]] - 1

    # Reset selection
    for r in rows:
        for x in r:
            x.setSelected(False)

    rows[item_selected[1]][item_selected[0]].setSelected(True)

    if rows[item_selected[1]][item_selected[0]].getX() + rows[item_selected[1]][item_selected[0]].getW() > 1280:
        # Update the row offset
        rows[item_selected[1]][0].row_offset = rows[item_selected[1]][0].row_offset + 1 # Use the first item of the list to get the row offset
        # Move the row
        for r in rows[item_selected[1]]:
            r.moveLeft()

    if rows[item_selected[1]][item_selected[0]].getX() < 0:
        # Update the row offset
        rows[item_selected[1]][0].row_offset = rows[item_selected[1]][0].row_offset - 1 # Use the first item of the list to get the row offset
        # Move the row
        for r in rows[item_selected[1]]:
            r.moveRight()
            
    # Page scroll needed?
    if rows[item_selected[1]][item_selected[0]].getY() + rows[item_selected[1]][item_selected[0]].getH() > 720:
        # Move the row
        for rr in rows:
            for r in rr:
                r.moveUp()

    # Page scroll needed?
    if rows[item_selected[1]][item_selected[0]].getY() < 0:
        # Move the row
        for rr in rows:
            for r in rr:
                r.moveDown()

    pass

def closeAddon():
    global mydisplay
    mydisplay.close()
    
    #del mydisplay
    
    #xbmc.executebuiltin('Dialog.Close(all)')
    pass

logo = 0
    
def postEvents():
    global mydisplay
    global logo
      
    addTopBar()
    
    mydisplay.connect(pyxbmct.ACTION_MOVE_RIGHT, move_right)
    mydisplay.connect(pyxbmct.ACTION_MOVE_LEFT, move_left)
    mydisplay.connect(pyxbmct.ACTION_MOVE_UP, move_up)
    mydisplay.connect(pyxbmct.ACTION_MOVE_DOWN, move_down)

    mydisplay.connect(ACTION_GESTURE_SWIPE_RIGHT, move_right)
    mydisplay.connect(ACTION_GESTURE_SWIPE_LEFT, move_left)
    mydisplay.connect(ACTION_GESTURE_SWIPE_UP, move_up)
    mydisplay.connect(ACTION_GESTURE_SWIPE_DOWN, move_down)

    #mydisplay.connect(pyxbmct.ACTION_NAV_BACK, mydisplay.close)
    refresh_selection()
    
    start_mouse_handler()
    
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    #xbmc.executebuiltin("Dialog.Close(all)")
    
    global base
    base.close()
    del base
    
    mydisplay.doModal()
    pass

barItems = []    
def addTopBar():
    global mydisplay
    # BAR
    # Add border above GUI
    barItems.append(xbmcgui.ControlImage(0, 0, page_blur, 720, filename=ART+'left.png', colorDiffuse=alpa))
    barItems.append(xbmcgui.ControlImage(1280 - page_blur, 0, page_blur, 720, filename=ART+'right.png', colorDiffuse=alpa))
    barItems.append(xbmcgui.ControlImage(0, 720 - page_blur, 1280, page_blur, filename=ART+'down.png', colorDiffuse=alpa))
    barItems.append(xbmcgui.ControlImage(0, 0, 1280, 160, filename=ART+'toph.png'))
    
    barItems.append(xbmcgui.ControlImage(70, 25, 190, 70, filename=ART+'logo.png', colorDiffuse='0xFFFFFFFF'))
    
    # Icons BAR
    icon_size = 64
    barItems.append(xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 4, 30, icon_size, icon_size, filename=ART+'icon-live.png', colorDiffuse='0xFFFFFFFF'))

    selected_0 = xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 4, 30 + icon_size, icon_size, 8, filename=ART+'b3.png', colorDiffuse='0xFFFFFFFF')
    selected_0.setVisible(True)
    mydisplay.addControl(selected_0)

    barItems.append(xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 3, 30, icon_size, icon_size, filename=ART+'icon-serie-a.png', colorDiffuse='0xFFFFFFFF'))

    selected_1 = xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 3, 30 + icon_size, icon_size, 8, filename=ART+'b3.png', colorDiffuse='0xFFFFFFFF')
    selected_1.setVisible(False)
    mydisplay.addControl(selected_1)

    barItems.append(xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 2, 30, icon_size, icon_size, filename=ART+'icon-champions-league.png', colorDiffuse='0xFFFFFFFF'))

    selected_2 = xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 2, 30 + icon_size, icon_size, 8, filename=ART+'b3.png', colorDiffuse='0xFFFFFFFF')
    selected_2.setVisible(False)
    mydisplay.addControl(selected_2)

    barItems.append(xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 1, 30, icon_size, icon_size, filename=ART+'icon-europa-league.png', colorDiffuse='0xFFFFFFFF'))

    selected_3 = xbmcgui.ControlImage(1280 - 100 - (icon_size + 10) * 1, 30 + icon_size, icon_size, 8, filename=ART+'b3.png', colorDiffuse='0xFFFFFFFF')
    selected_3.setVisible(False)
    mydisplay.addControl(selected_3)

    for b in barItems:
        mydisplay.addControl(b)
    pass

def removeTopBar():
    global barItems
    global mydisplay
    for b in barItems:
        mydisplay.removeControl(b)
    pass
 
import threading
import time

#Routine that processes whatever you want as background
def YourLedRoutine():    
    # ADD TO GUI
    i_r = 0
    for r in data_rows:
        gui_row = []
        i_i = 0
        for i in r:
            # Accept only selected events
            accepted = False
            for a in accepted_league:
                if a in i.getLname().lower() and 'football' in i.getLogo_league().lower():
                    accepted = True
                    break
            if accepted:
                gui_row.append( Quad(offset_page_left + (width + offset_w) * (i_i), offset_page_top + (height + offset_h) * i_r, i) )
                i_i = i_i + 1
        if (len(gui_row) > 0):
            rows.append(gui_row)
            row_items_count.append((i_i))
            i_r = i_r + 1
    
    #removeTopBar()
    #addTopBar()
    
    for r in rows:
        for i in r:
            i.applyContextualImages()

#    global logo
#    logo.setIndex(0)

#    while 1:
#        #print 'tick'
#        #pos = xbmcgui.getMousePosition()
#        for r in rows:
#            for i in r:
#                if pos.X > i.getX() and pos.X < i.getX() + i.getW() and pos.Y > i.getY() and pos.Y < i.getY() + i.getH():
#                    i.setSelected(True)
#                    refresh_selection()
#        time.sleep(1)

def start_mouse_handler():
    t1 = threading.Thread(target=YourLedRoutine)
    #Background thread will finish with the main program
    t1.setDaemon(True)
    #Start YourLedRoutine() in a separate thread
    t1.start()
    #You main program imitated by sleep
    #time.sleep(5)
    pass
   
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
    global rows
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
    paramstring = sys.argv[2]
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
    initializeGUI()
    get_events(Live_url)
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
#           iconimage, 5000)

