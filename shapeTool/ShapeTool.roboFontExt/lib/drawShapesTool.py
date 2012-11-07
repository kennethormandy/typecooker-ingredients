from mojo.events import BaseEventTool, installTool
from AppKit import *
import os

from lib.tools.drawing import strokePixelPath

from dialogKit import ModalDialog, TextBox, EditText, PopUpButton
from vanilla import RadioGroup

from mojo.extensions import ExtensionBundle


## collecting the image data for building cursors and toolbar icons

shapeBundle = ExtensionBundle("ShapeTool")
_cursorOval = CreateCursor(shapeBundle.get("cursorOval"), hotSpot=(6, 6))

_cursorRect = CreateCursor(shapeBundle.get("cursorRect"), hotSpot=(6, 6))

toolbarIcon = shapeBundle.get("toolbarIcon")


class GeometricShapesWindow(object):
    """
    The Modal window that allows numbers input to draw basic geometric shapes.
    """
    
    def __init__(self, glyph, callback, x, y):
        self.glyph = glyph
        self.callback = callback
        ## create the modal dialog (from dialogKit)
        self.w = ModalDialog((200, 150), 
                            "Shapes Tool", 
                            okCallback=self.okCallback, 
                            cancelCallback=self.cancelCallback)
        
        ## add some text boxes
        self.w.xText = TextBox((10, 13, 100, 22), "x")
        self.w.yText = TextBox((10, 43, 100, 22), "y")
        self.w.wText = TextBox((100, 13, 100, 22), "w")
        self.w.hText = TextBox((100, 43, 100, 22), "h")
        
        ## adding input boxes
        self.w.xInput = EditText((30, 10, 50, 22), "%i" %x)
        self.w.yInput = EditText((30, 40, 50, 22), "%i" %y)
        self.w.wInput = EditText((120, 10, 50, 22))
        self.w.hInput = EditText((120, 40, 50, 22))
        
        ## a radio shape choice group 
        ## (the RadioGroup isn't standaard in dialogKit, this is a vanilla object)
        self.shapes = ["rect", "oval"]
        self.w.shape = RadioGroup((10, 70, -10, 22), self.shapes, isVertical=False)
        self.w.shape.set(0)
        
        self.w.open()
        
    def okCallback(self, sender):
        ## draw the shape in the glyph
        ## get the shape from the radio group
        shape = self.shapes[self.w.shape.get()]
        ## try to get some integers from the input fields
        try:
            x = int(self.w.xInput.get())
            y = int(self.w.yInput.get())
            w = int(self.w.wInput.get())
            h = int(self.w.hInput.get())
        ## if this fails just do nothing and print a tiny traceback
        except:
            print "Input wan't a number!" 
            return
        ## draw the shape with the callback given on init
        self.callback(shape, (x, y, w, h), self.glyph)
    
    def cancelCallback(self, sender):
        ## do nothing :)
        pass

def _roundPoint(x, y):
    return int(round(x)), int(round(y))
     
class DrawGeometricShapesTool(BaseEventTool):

    def setup(self):
        ## setup is called when the tool gets active
        ## use this to initialize some attributes
        self.minPoint = None
        self.maxPoint = None
        self.shape = "rect"
    
    def getRect(self):
        ## return the rect between mouse down and mouse up
        x = self.minPoint.x
        y = self.minPoint.y
        w = self.maxPoint.x - self.minPoint.x
        h = self.maxPoint.y - self.minPoint.y
        ## handle the shift down and equalize width and height
        if self.shiftDown:
            sign = 1
            if abs(w) > abs(h):
                if h < 0:
                    sign = -1
                h = abs(w) * sign
            else:
                if w < 0:
                    sign = -1
                w = abs(h) * sign
        return x, y, w, h
    
    def drawShapeWithRectInGlyph(self, shape, rect, glyph):
        ## draw the shape into the glyph
        ## tell the glyph something is going to happen (undo is going to be prepared)

        glyph.prepareUndo("Drawing Shapes")
        ## get the pen to draw with
        pen = glyph.getPen()
        
        x, y, w, h = rect
        
        ## draw with the pen a rect in the glyph
        if shape == "rect":
            pen.moveTo(_roundPoint(x, y))
            pen.lineTo(_roundPoint(x + w, y))
            pen.lineTo(_roundPoint(x + w, y + h))
            pen.lineTo(_roundPoint(x, y + h))
            pen.closePath()
        
        ## draw with the pen an oval inthe glyph
        elif shape == "oval":
            
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
        ## tell the glyph you are done with your actions so it can handle the undo properly
        glyph.performUndo()
    
    def mouseDown(self, point, offset):
        ## a mouse down, only save the mouse down point
        self.minPoint = point
        ## if command is down pop up an modal dialog with inputs
        if self.commandDown:
            ## create and open the modal dialog
            GeometricShapesWindow(self.getGlyph(), 
                            callback=self.drawShapeWithRectInGlyph, 
                            x=self.minPoint.x, 
                            y=self.minPoint.y)
        # getGLyph returns the current glyph as robofab object

    def mouseDragged(self, point, delta):
        ## record the draggin point
        self.maxPoint = point        

    def mouseUp(self, point):
        ## mouse up, if you have recorded the rect draw that into the glyph
        if self.minPoint and self.maxPoint:
            self.drawShapeWithRectInGlyph(self.shape, self.getRect(), self.getGlyph())
        ## reset the tool
        self.setup()
        
    def modifiersChanged(self):
        ## is been called when the modifiers changed (shift, alt, control, command)
        self.shape = "rect"
        ## change the shape when option is down
        if self.optionDown:
            self.shape = "oval"
        ## refresh the current glyph view
        self.getNSView().refresh()
        
    def draw(self, scale):
        ## draw stuff in the current glyph view
        if self.isDragging() and self.minPoint and self.maxPoint:
            ## draw only during drag and when recorded some rect
            ## make the rect
            x, y, w, h = self.getRect()
            rect = NSMakeRect(x, y, w, h)
            ## set the color
            NSColor.redColor().set()
            
            if self.shape == "rect":
                ## create a rect path
                path = NSBezierPath.bezierPathWithRect_(rect)
                
            elif self.shape == "oval":
                ## create a oval path
                path = NSBezierPath.bezierPathWithOvalInRect_(rect)
            ## set the line width
            path.setLineWidth_(scale)
            ## draw without anit-alias
            strokePixelPath(path)


    def getDefaultCursor(self):
        ## returns the cursor
        if self.shape == "rect":
            return _cursorRect
        else:
            return _cursorOval
            
    def getToolbarIcon(self):
        ## return the toolbar icon
        return toolbarIcon

    def getToolbarTip(self):
        ## return the toolbar tool tip
        return "Shape Tool"

## install the tool!!
installTool(DrawGeometricShapesTool())


