from vanilla import *
from AppKit import NSColor

from defconAppKit.windows.baseWindow import BaseWindowController

from glyphLayerPreview import GlyphLayerPreview
from mojo.events import addObserver, removeObserver

from mojo.roboFont import *

class LayerWindow(BaseWindowController):
    
    def __init__(self):
                
        self.w = Window((400, 400), "Layer Preview", minSize=(400, 300))
        
        self.w.preview = GlyphLayerPreview((0, 0, -0, -30))
        self.currentGlyphChanged()
        
        self.w.useColor = CheckBox((10, -30, 100, 22), "Use Color:", callback=self.useColorCallback)
        
        self.w.color = ColorWell((120, -35, 40, 30), color=NSColor.blackColor(), callback=self.colorCallback)
        
        self.w.testInstall = Button((-170, -30, -10, 22), "Test Install Layers", callback=self.testInstallCallback)
        
        addObserver(self, "currentGlyphChanged", "currentGlyphChanged")
        
        self.setUpBaseWindowBehavior()
        self.w.open()
        
    def currentGlyphChanged(self, notification=None):
        self.w.preview.setGlyph(CurrentGlyph())
    
    def windowCloseCallback(self, sender):
        removeObserver(self, "currentGlyphChanged")
        super(LayerWindow, self).windowCloseCallback(sender)
    
    def useColorCallback(self, sender):
        value = sender.get()
        self.w.color.enable(value)
        if value:
            color = self.w.color.get()
        else:
            color = None
        self.w.preview.setColor(color)
    
    def colorCallback(self, sender):
        self.useColorCallback(self.w.useColor)
    
    
    def testInstallCallback(self, sender):
        font = CurrentFont()
        
        familyName = font.info.familyName
        styleName = font.info.styleName
        if familyName is None or styleName is None:
            self.showMessage("Font needs a family name and style name.", "Please name it correctly")
            return  
        
        font.testInstall()
        
        for layerName in font.layerOrder:
            layerFont = NewFont(font.info.familyName, "%s %s" %(font.info.styleName, layerName), showUI=True)
            
            for glyph in font:
                layerGlyph = glyph.getLayer(layerName)
                layerFont[glyph.name] = layerGlyph.copy()
                                                
            layerFont.testInstall()
                
            
        
    
LayerWindow()