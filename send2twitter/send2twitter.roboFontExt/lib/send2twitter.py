from AppKit import *
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController

from mojo.UI import CurrentGlyphWindow, CurrentSpaceCenter
from mojo.roboFont import OpenWindow
from mojo.extensions import getExtensionDefault, setExtensionDefault

from twitpic import TwitPicAPI

defaultKey = "com.typemytype.send2twitter"

class Post2Twitter(BaseWindowController):
    
    hashTag = "#robofont"
    twitLength = 80
    
    def __init__(self):
        self.w = FloatingWindow((220, 240),  "2 Twitter")

        left = 100
        y = 10
        
        userName = getExtensionDefault("%s.%s" %(defaultKey, "userName"), "")
        password = getExtensionDefault("%s.%s" %(defaultKey, "password"), "")
        
        self.w.userNameText = TextBox((10, y, left, 22), "User name:")
        self.w.userName = EditText((left, y, -10, 22), userName)
        y += 30
        
        self.w.passwordText = TextBox((10, y, left, 22), "Password:")
        self.w.password = SecureEditText((left, y, -10, 22), password)   
        y += 30
        
        self.w.message = TextEditor((10, y, -10, 70), callback=self._textEditorCallback)
        y += 80
        
        self._viewNames = ["Glyph View", "Space Center"]
        self.w.view = RadioGroup((10, y, -10, -40), self._viewNames)
        self.w.view.set(0)     
        
        self.w.okButton = Button((-70, -30, -15, 20), "Post", callback=self.okCallback, sizeStyle="small")
        self.w.setDefaultButton(self.w.okButton)
        
        self.w.closeButton = Button((-140, -30, -80, 20), "Cancel", callback=self.closeCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(unichr(27), [])
        
        self.w.open()
    
    def _textEditorCallback(self, sender):
        txt = sender.get()
        length = self.twitLength - len(self.hashTag)
        if len(txt) > length:
            sender.set(txt[:length])
    
    def closeCallback(self, sender):
        self.w.close()
    
    def okCallback(self, sender):
        userName = self.w.userName.get()
        password = self.w.password.get()
        twit = TwitPicAPI(userName, password)
        
        i = self.w.view.get()
        viewName = self._viewNames[i]
        image = self.getImageForView(viewName)
        if image is None:
            self.showMessage("Oeps!", "Open a glyph window or space center window")
            return
        
        message = self.w.message.get()
        status = twit.upload(image, "%s #robofont" %message, post_to_twitter=True)
        if status == 1001:
            self.showMessage("Oeps!", "Invalid user or password") 
        elif status in [1002, 1003, 1004]:
            self.showMessage("Oeps!", "An error occured 'somewhere', try again")
        else:
            self.showMessage("Send to Twitter", "%s" %status)
        
        setExtensionDefault("%s.%s" %(defaultKey, "userName"), userName)
        setExtensionDefault("%s.%s" %(defaultKey, "password"), password)
    
    def getImageForView(self, viewName):
        if viewName == "Glyph View":
            window = CurrentGlyphWindow()
            if window is None:
                return None
            view = window.getGlyphView().enclosingScrollView()
        elif viewName == "Space Center":
            window = CurrentSpaceCenter()
            if window is None:
                return None
            view = window.glyphLineView.getNSScrollView()
        
        data = self._getImageForView(view)        
        data  = data.bytes()
        if isinstance(data, memoryview):
            data = data.tobytes()
        return data 
    
    def _getImageForView(self, view):
        rect = view.bounds()

        rep = view.bitmapImageRepForCachingDisplayInRect_(rect)
        view.cacheDisplayInRect_toBitmapImageRep_(rect, rep)
        
        scrollbarSizeX = scrollbarSizeY = 0
        if view.hasHorizontalScroller():
            scrollbarSizeX = 16
        
        if view.hasVerticalScroller():
            scrollbarSizeY = 16
        
        width, height = rect.size
        im = NSImage.alloc().initWithSize_((width-scrollbarSizeX, height-scrollbarSizeY))
        (x, y), (w, h) = rect
        im.lockFocus()
        rep.drawAtPoint_((-x, -rect.size.height+y+h-scrollbarSizeY))
        im.unlockFocus()
        rep = NSBitmapImageRep.imageRepWithData_(im.TIFFRepresentation())

        return rep.representationUsingType_properties_(NSPNGFileType, None)
        
OpenWindow(Post2Twitter)