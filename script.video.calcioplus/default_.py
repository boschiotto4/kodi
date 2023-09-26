# Import PyXBMCt module.
import pyxbmct
import xbmcgui
import xbmcaddon
import xbmc

ADDON = xbmcaddon.Addon()
ADDON_DATA = ADDON.getAddonInfo('profile')
ADDON_PATH = ADDON.getAddonInfo('path')

ART = ADDON_PATH + "/resources/icons/"

ACTION_PREVIOUS_MENU = 10
ACTION_BACK_MENU = 92
ACTION_SELECT_ITEM = 7


# Main code
class Main(pyxbmct.BlankDialogWindow): #BlankFullWindow):
    def __init__( self):
        # Call the base class' constructor.
        super(Main, self).__init__()
        
        xbmc.log('init', xbmc.LOGERROR)

        #self.setGeometry(1280, 722, 1, 1)

        self.main_bg = xbmcgui.ControlImage(0, 0, 1280, 720, ART + 'bg.png')
        self.addControl(self.main_bg)
        #self.setFocus(self.main_bg)
    #def onInit(self):
    #    xbmc.log('do Modal', xbmc.LOGERROR)
    def onClick(self, controlId):
        xbmc.log('focaa', xbmc.LOGERROR)
    
    def onAction(self, action):
        super(Main, self).onAction(action)
        xbmc.log('foc', xbmc.LOGERROR)
        #pyxbmct.BlankFullWindow.onAction(self, action)

        if action.getId() == pyxbmct.ACTION_MOUSE_MOVE:
#            self.close()
            xbmc.log('mouser', xbmc.LOGERROR)
            closeAddon()          
#        elif action.getId() == ACTION_PREVIOUS_MENU:
#            self.close()
#            closeAddon()   
        elif action.getId() == ACTION_BACK_MENU:
#            self.close()
            closeAddon()   
        elif action.getId() == pyxbmct.ACTION_NAV_BACK:
#            self.close()
            closeAddon()   
        elif action.getId() == ACTION_SELECT_ITEM:
            get_stream(rows[item_selected[1]][item_selected[0]].getEventData().getStreams())   
        #else:
        pyxbmct.BlankFullWindow.onAction(self, action)

#window = pyxbmct.AddonDialogWindow('Hello, World!')

def onAction(action):
    xbmc.log('focsssssssssssss', xbmc.LOGERROR)
    
def closeAddon():
    window.close()

base = xbmcgui.Window(xbmcgui.getCurrentWindowId())

# Create a window instance.
window = Main()
# Set window width, height and grid resolution.
window.setGeometry(128, 720, 1, 1)

xbmc.executebuiltin('Dialog.Close(all)')

base.close()

def alive():
    xbmc.log('mmmmfoc', xbmc.LOGERROR)
    
window.connect(pyxbmct.ACTION_MOUSE_MOVE, alive)
# Show the created window.
window.doModal()
# Delete the window instance when it is no longer used.
del window

