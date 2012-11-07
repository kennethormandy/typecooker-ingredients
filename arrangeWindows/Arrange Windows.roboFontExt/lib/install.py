from AppKit import *
from lib.doodleMenus import BaseMenu
from tile import tile
from cascade import cascade


class ArrangeWindows(object):
    
    def __init__(self):
        
        menuBar = NSApp().mainMenu()
        
        windowMenu = menuBar.itemWithTitle_("Window")
        
        menu = windowMenu.submenu()
        
        self.menuController = BaseMenu()
        
        menuItems = [
            ("Tile", self.tileCallback),
            ("Cascade", self.cascadeCallback)
            ]
        for title, callback in menuItems:
            if menu.itemWithTitle_(title):
                return
        
        self.menuController.buildAdditionContectualMenuItems(menu, menuItems, insert=7)
        
    def tileCallback(self, sender):
        tile()
    
    def cascadeCallback(self, sender):
        cascade()
        
ArrangeWindows()