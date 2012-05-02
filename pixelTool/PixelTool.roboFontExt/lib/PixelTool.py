from AppKit import *
from math import floor
import vanilla
import os

from mojo.events import BaseEventTool, installTool
from mojo.roboFont import CreateCursor

from mojo.extensions import getExtensionDefault, setExtensionDefault, ExtensionBundle

from lib.tools.notifications import PostNotification
from lib.tools import bezierTools
from lib.tools.defaults import getDefault, setDefault

from settings import *

from generateImages import AddPixelToolRepresentationFactory

AddPixelToolRepresentationFactory()

pixelBundle = ExtensionBundle("PixelTool")
pixelCursor = CreateCursor(pixelBundle.get("pixelCursor"), hotSpot=(9, 9))

def _roundPoint(x, y):
    return int(round(x)), int(round(y))

class GridSettingsMenu(object):
    
    def __init__(self, tool, event, view):
        self.tool = tool
        
        self.drawingChoices = [RECT_MODE, OVAL_MODE, COMPONENT_MODE]
                
        self.view = vanilla.Group((0, 0, 0, 0))
        
        
        self.view.gridText = vanilla.TextBox((10, 12, 100, 22), "Pixel Size:")
        self.view.gridInput = vanilla.EditText((120, 10, -10, 22), self.tool.size, callback=self.gridInputCallback)
        
        self.view.drawingMode = vanilla.RadioGroup((10, 40, -10, 100), self.drawingChoices, isVertical=True, callback=self.drawingModeCallback)
        if self.tool.drawingMode in self.drawingChoices:
            self.view.drawingMode.set(self.drawingChoices.index(self.tool.drawingMode))
        
        self.view.componentName = vanilla.EditText((120, 113, -10, 22), self.tool.componentName, callback=self.drawingModeCallback)
        
        self.view.componentName.show(self.tool.drawingMode == COMPONENT_MODE)
        
        
        self.view.useGrid = vanilla.CheckBox((11, 145, -10, 22), "Use Grid", value=self.tool.useGrid, callback=self.drawingModeCallback)
        
        nsView = self.view.getNSView()
        nsView.setFrame_(NSMakeRect(0, 0, 195, 175))
        
        menu = NSMenu.alloc().init()
        settingsItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("doodle.guideView", None, "")
        settingsItem.setView_(nsView)
        menu.addItem_(settingsItem)
        
        NSMenu.popUpContextMenu_withEvent_forView_(menu, event, view)        
        
    def gridInputCallback(self, sender):
        value = sender.get()
        ## must be int
        try:
            value = int(value)
        except:
            value = -1
            
        if value <= 0:
            value = self.tool.size
            sender.set(value)    
            return
        
        self.tool.size = value
        setExtensionDefault(GRID_DEFAULTS_KEY, value)
    
    def drawingModeCallback(self, sender):
        i = self.view.drawingMode.get()
        
        value = self.drawingChoices[i]
        
        self.tool.drawingMode = value
        setExtensionDefault(DRAWING_DEFAULTS_KEY, value)
        componentName = ""
        if value == COMPONENT_MODE:
            self.view.componentName.show(True)
            componentName = str(self.view.componentName.get())
        else:
            self.view.componentName.show(False)
            self.view.componentName.set("")
        self.tool.componentName = componentName
        setExtensionDefault(COMPONENT_DEFAULT_KEY, componentName)
        
        useGrid = self.view.useGrid.get()
        self.tool.useGrid = useGrid
        setExtensionDefault(USEGRID_DEFAULT_KEY, useGrid)

class PixelTool(BaseEventTool):
    
    def _get_size(self):
        return self._size
    
    def _set_size(self, value):
        self._size = value
        setDefault("glyphViewGridx", value)
        setDefault("glyphViewGridy", value)
        PostNotification("doodle.preferencesChanged")
    
    size = property(_get_size, _set_size)
    
    def setup(self):
        self.size = int(getExtensionDefault(GRID_DEFAULTS_KEY, 50))
        self.actionMode = ADD_ACTION_MODE
        self.drawingMode = getExtensionDefault(DRAWING_DEFAULTS_KEY, RECT_MODE)
        self.componentName = getExtensionDefault(COMPONENT_DEFAULT_KEY, "")
        self.useGrid = getExtensionDefault(USEGRID_DEFAULT_KEY, True)

    def mouseDown(self, point, offset):
        
        glyph = self.getGlyph()
        
        found = self.findObjectInGlyphForPoint(glyph, point)
        
        glyph.prepareUndo("%s Shapes" %self.actionMode)
        if found is not None:
            ## remove contour if we found one
            self.actionMode = REMOVE_ACTION_MODE
            if self.drawingMode == COMPONENT_MODE:
                glyph.removeComponent(found)
            else:
                glyph.removeContour(found)
        
        else:
            ## add a square around a point
            self.actionMode = ADD_ACTION_MODE
            self.addShapeInGlyphForPoint(glyph, point)
        
    def rightMouseDown(self, point, event):
        GridSettingsMenu(self, event, self.getNSView())
        
    def mouseDragged(self, point, delta):
        glyph = self.getGlyph()
        found = self.findObjectInGlyphForPoint(glyph, point)
        
        if self.actionMode == REMOVE_ACTION_MODE and found is not None:
            if self.drawingMode == COMPONENT_MODE:
                glyph.removeComponent(found)
            else:
                glyph.removeContour(found)
        
        elif self.actionMode == ADD_ACTION_MODE and found is None:
            self.addShapeInGlyphForPoint(glyph, point)
        
    
    def mouseUp(self, point):
        glyph = self.getGlyph()
        glyph.performUndo()
        glyph.update()
        self.actionMode = ADD_ACTION_MODE
        
    def findObjectInGlyphForPoint(self, glyph, point):
        found = None
        if self.drawingMode == COMPONENT_MODE:
            size = self.size
            halfSize = size * .5
            for component in glyph.components:
                x, y = component.offset
                if bezierTools.distanceFromPointToPoint((x+halfSize, y+halfSize), point) < size:
                    found = component
                    break
        else:
            for contour in glyph:
                if contour.pointInside(point):
                    found = contour
                    break
        return found
        
    def addShapeInGlyphForPoint(self, glyph, point):
        w = h = self.size
        
        if self.useGrid:
            x = int(floor(point.x / float(w))) * w
            y = int(floor(point.y / float(h))) * h
        else:
            x = point.x - w*.5
            y = point.y - h*.5
        
        pen = glyph.getPen()
        
        if self.drawingMode == RECT_MODE:
    
            pen.moveTo((x, y))
            pen.lineTo((x + w, y))
            pen.lineTo((x + w, y + h))
            pen.lineTo((x, y + h))
            pen.closePath()
        
        elif self.drawingMode == OVAL_MODE:

            hw = w/2.
            hh = h/2.

            r = .55
            penMethod = pen.curveTo
            if glyph.preferedSegmentType == "qcurve":
                r = .42
                penMethod = pen.qCurveTo
            
            
            pen.moveTo(_roundPoint(x + hw, y))

            penMethod(_roundPoint(x + hw + hw*r, y), 
                        _roundPoint(x + w, y + hh - hh*r), 
                        _roundPoint(x + w, y + hh))

            penMethod(_roundPoint(x + w, y + hh + hh*r), 
                        _roundPoint(x + hw + hw*r, y + h), 
                        _roundPoint(x + hw, y + h))

            penMethod(_roundPoint(x + hw - hw*r, y + h), 
                        _roundPoint(x, y + hh + hh*r), 
                        _roundPoint(x, y + hh))

            penMethod(_roundPoint(x, y + hh - hh*r), 
                        _roundPoint(x + hw - hw*r, y), 
                        _roundPoint(x + hw, y))
            

            pen.closePath()
        
        elif self.drawingMode == COMPONENT_MODE and self.componentName and self.componentName != glyph.name:
            pen.addComponent(self.componentName, [1, 0, 0, 1, x, y])
            
        
    def getDefaultCursor(self):
        return pixelCursor
    
    def getToolbarIcon(self):
        return pixelCursor.image()
    
    def getToolbarTip(self):
        return "Pixel Tool"
    
        
installTool(PixelTool())