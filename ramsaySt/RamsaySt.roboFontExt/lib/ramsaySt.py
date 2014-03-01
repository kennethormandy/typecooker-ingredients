from AppKit import NSColor

from robofab.tools.toolsAll import readGlyphConstructions

from mojo.events import addObserver
from mojo.drawingTools import save, restore, translate
from mojo.UI import SetCurrentGlyphByName

from lib.tools.defaults import getDefaultColor
from lib.tools.drawing import strokePixelPath

from ramsayStData import RamsayStData


class RamsaySts(object):
    
    def __init__(self):        
        self.accentsContstruction = readGlyphConstructions()
        addObserver(self, "drawNeightbors", "drawBackground")
        addObserver(self, "drawPreviewNeighBors", "drawPreview")
        addObserver(self, "mouseDown", "mouseDown")
    
    def mouseDown(self, info):
        if not RamsayStData.showPreview:
            return
        glyph = info["glyph"]
        event = info["event"]
        if event.clickCount() == 3:
            x, y = info["point"]
            font = glyph.getParent()
            baseName = self.getBaseGlyph(glyph.name)
            left, right = RamsayStData.get(baseName, ("n", "n"))
            
            if left in font:
                leftGlyph = font[left]
                path = leftGlyph.naked().getRepresentation("defconAppKit.NSBezierPath")
                if path.containsPoint_((x+leftGlyph.width, y)):
                    SetCurrentGlyphByName(left)
                    return
            if right in font:
                rightGlyph = font[right]
                path = rightGlyph.naked().getRepresentation("defconAppKit.NSBezierPath")
                if path.containsPoint_((x-glyph.width, y)):
                    SetCurrentGlyphByName(right)
                    return
    
    def drawPreviewNeighBors(self, info):
        if not RamsayStData.showPreview:
            return
        fillColor = NSColor.blackColor()
        fillColor.set()
        self._drawNeightborsGlyphs(info["glyph"], stroke=False)
        
    def drawNeightbors(self, info):
        if not RamsayStData.showPreview:
            return
        RamsayStData.fillColor.setFill()
        RamsayStData.strokeColor.setStroke()
        self._drawNeightborsGlyphs(info["glyph"], scale=info["scale"])
        
    def _drawNeightborsGlyphs(self, glyph, stroke=True, scale=1):
        if glyph is None:
            return
        font = glyph.getParent()
        baseName = self.getBaseGlyph(glyph.name)
        left, right = RamsayStData.get(baseName, ("n", "n"))

        if left in font:
            leftGlyph = font[left]
            save()
            ## translate back the width of the glyph 
            translate(-leftGlyph.width, 0)
            ## performance tricks, the naked attr will return the defcon object
            ## and get the cached bezier path to draw
            path = leftGlyph.naked().getRepresentation("defconAppKit.NSBezierPath")
            ## fill the path
            path.fill()
            if stroke:
                path.setLineWidth_(scale)
                strokePixelPath(path)
            restore()
        
        ## do the same for the other glyph
        if right in font:
            rightGlyph = font[right]
            save()
            ## translate forward the width of the current glyph
            translate(glyph.width, 0)
            path = rightGlyph.naked().getRepresentation("defconAppKit.NSBezierPath")
            path.fill()
            if stroke:
                path.setLineWidth_(scale)
                strokePixelPath(path)
            restore()
        
    def getBaseGlyph(self, name):
        construction = self.accentsContstruction.get(name)
        if construction is None:
            return name
        return construction[0]
            
        
RamsaySts()