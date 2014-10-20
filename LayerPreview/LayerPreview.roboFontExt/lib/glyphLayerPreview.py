from AppKit import *
from mojo.glyphPreview import GlyphPreview, GlyphPreviewView

class GlyphLayerPreviewView(GlyphPreviewView):

    def init(self):
        super(GlyphLayerPreviewView, self).init()
        self._color = None
        return self

    def setColor_(self, color):
        self._color = color
        self.refresh()

    def drawRect_(self, rect):
        if self.inLiveResize():
            self.calculateScale()

        if self._glyph is None:
            return

        transform = NSAffineTransform.transform()
        transform.translateXBy_yBy_(0, self._buffer)
        transform.concat()

        transform = NSAffineTransform.transform()
        transform.scaleBy_(self._scale)
        transform.translateXBy_yBy_(0, self._descender)
        transform.concat()

        flipTransform = NSAffineTransform.transform()
        flipTransform.translateXBy_yBy_(self._shift, self._upm)
        flipTransform.scaleXBy_yBy_(1.0, -1.0)
        flipTransform.concat()


        glyph = self._glyph
        if glyph.isLayer():
            glyph = glyph.getBaseGlyph()

        font = glyph.getParent()

        if self._color is not None:
            self._color.set()

        for layerName in reversed(["foreground"] + font.layerOrder):
            layer = glyph.getLayer(layerName)
            if self._color is None:
                color = font.getLayerColor(layerName)
                color.set()
            path = layer.getRepresentation("defconAppKit.NSBezierPath")
            path.fill()

        if self._selection:
            selectionPath = NSBezierPath.bezierPath()
            radius = 3/self._scale
            for x, y in self._selection:
                selectionPath.appendBezierPathWithOvalInRect_(NSMakeRect(x-radius, y-radius, radius*2, radius*2))

            NSColor.redColor().set()
            selectionPath.fill()

class GlyphLayerPreview(GlyphPreview):

    nsViewClass = GlyphLayerPreviewView

    def setColor(self, color):
        self.getNSView().setColor_(color)