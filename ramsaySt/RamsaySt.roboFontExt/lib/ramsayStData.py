from AppKit import NSColor, NSObject
from mojo.extensions import getExtensionDefault, setExtensionDefault, getExtensionDefaultColor, setExtensionDefaultColor

_baseDefaultKey = "com.typemytype.ramsaySt"
_fillColorDefaultKey = "%s.fillColor" % _baseDefaultKey
_strokeColorDefaultKey = "%s.strokeColor" %_baseDefaultKey
_showPreviewDefaultKey = "%s.showPreview" %_baseDefaultKey
_dataDefaultKey = "%s.data" % _baseDefaultKey

class RamsayStDataItem(NSObject):
    
    def __new__(cls, *args, **kwargs):
        return cls.alloc().init()
    
    def __init__(self, glyphName, value):
        self._glyphName = glyphName
        self._value = list(value)
    
    def getRamsaySt(self):
        return self._value
    
    def glyphName(self):
        return self._glyphName
    
    def setGlyphName_(self, value):
        if value is None:
            return
        self._glyphName = value
    
    def left(self):
        return self._value[0]
    
    def setLeft_(self, value):
        if value is None:
            value = " "
        self._value[0] = value
        
    def right(self):
        return self._value[1]
    
    def setRight_(self, value):
        if value is None:
            value = " "
        self._value[1] = value

class RamsayStDataCollection(object):
    
    _fallBackFillColor = NSColor.colorWithCalibratedRed_green_blue_alpha_(.34, .54, .92, .7)
    _fallBackStrokeColor = NSColor.blackColor()
    _fallbackData = {'-': ('n', 'H'), 'A': ('H', 'V'), 'C': ('c', 'G'), 'B': ('P', 'D'), 'E': ('B', 'F'), 'D': ('B', 'P'), 'G': ('C', 'O'), 'F': ('P', 'E'), 'I': ('J', 'H'), 'H': ('I', 'P'), 'K': ('k', 'I'), 'J': ('j', 'I'), 'M': ('H', 'N'), 'L': ('I', 'H'), 'O': ('C', 'o'), 'N': ('M', 'V'), 'Q': ('O', 'G'), 'P': ('R', 'p'), 'S': ('C', 's'), 'R': ('B', 'P'), 'U': ('u', 'H'), 'T': ('I', 'H'), 'W': ('w', 'V'), 'V': ('v', 'W'), 'Y': ('y', 'V'), 'X': ('x', 'Y'), 'Z': ('z', 'X'), 'a': ('n', 'e'), 'c': ('e', 'C'), 'b': ('d', 'p'), 'e': ('o', 'c'), 'd': ('q', 'b'), 'g': ('o', 'q'), 'f': ('i', 't'), 'i': ('period', 'j'), 'h': ('l', 'n'), 'k': ('h', 'K'), 'j': ('i', 'period'), 'm': ('n', 'w'), 'l': ('h', 'k'), 'o': ('c', 'O'), 'n': ('h', 'm'), 'q': ('d', 'p'), 'p': ('q', 'P'), 's': ('e', 'S'), 'r': ('s', 'n'), 'u': ('v', 'n'), 't': ('s', 'f'), 'w': ('v', 'W'), 'v': ('u', 'w'), 'y': ('v', 'Y'), 'x': ('y', 'X'), 'z': ('x', 'Z')}
    _fallbackShowPreview = True

    def __init__(self): 
        self.load()

    def load(self):
        self.fillColor = getExtensionDefaultColor(_fillColorDefaultKey, self._fallBackFillColor)
        self.strokeColor = getExtensionDefaultColor(_strokeColorDefaultKey, self._fallBackStrokeColor)
        self.showPreview = getExtensionDefault(_showPreviewDefaultKey, self._fallbackShowPreview)
        self.data = getExtensionDefault(_dataDefaultKey, self._fallbackData)

    def save(self):
        setExtensionDefaultColor(_fillColorDefaultKey, self.fillColor)
        setExtensionDefaultColor(_strokeColorDefaultKey, self.strokeColor)
        setExtensionDefault(_showPreviewDefaultKey, self.showPreview)
        setExtensionDefault(_dataDefaultKey, self.data)
    
    def keys(self):
        return self.data.keys()
    
    def __contains__(self, key):
        return key in self.data
    
    def get(self, value, fallback=("n", "n")):
        return self.data.get(value, fallback)
    
    def set(self, item):
        key = item.glyphName()
        if key is None:
            return
        self.data[key] = item.getRamsaySt()
    
    def setItems(self, data):
        self.data = dict()
        for item in data:
            self.data[item.glyphName()] = item.getRamsaySt()
        self.save()
        
    def getItems(self):
        keys = list(self.data.keys())
        keys.sort()
        return [RamsayStDataItem(key, self.data[key]) for key in keys]
    
    def newItem(self, glyphName):
        return RamsayStDataItem(glyphName, (" ", " "))

RamsayStData = RamsayStDataCollection()