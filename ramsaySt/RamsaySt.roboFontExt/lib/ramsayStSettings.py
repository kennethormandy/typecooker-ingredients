import vanilla
from AppKit import NSSegmentStyleSmallSquare
from mojo.roboFont import OpenWindow
from mojo.UI import UpdateCurrentGlyphView
from lib.eventTools.eventManager import getActiveEventTool

from ramsayStData import RamsayStData

class AddGlyphNameSheet(object):
    
    def __init__(self, parentWindow, callback=None):
        self.callback = callback
        
        self.w = vanilla.Sheet((350, 90), parentWindow=parentWindow)
        
        self.w.glyphNameText = vanilla.TextBox((10, 17, 100, 22), "Glyph Name:")
        self.w.glyphName = vanilla.EditText((100, 17, -10, 22)) 
        
        self.w.addButton = vanilla.Button((-70, -30, -10, 20), "Add", callback=self.addCallback, sizeStyle="small")
        self.w.setDefaultButton(self.w.addButton)
        
        self.w.closeButton = vanilla.Button((-150, -30, -80, 20), "Cancel", callback=self.closeCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(unichr(27), [])
        
        self.w.open()
    
    def addCallback(self, sender):
        if self.callback:
            self.callback(self)
        self.closeCallback(sender)
    
    def closeCallback(self, sender):
        self.w.close()
        
    def get(self):
        return self.w.glyphName.get()


class RamsayStSettingsWindowController(object):
    
    def __init__(self):
        self.w = vanilla.FloatingWindow((250, 300), "Ramsay St. Settings", minSize=(250, 250), maxSize=(400, 700))
        
        self.w.showPreview = vanilla.CheckBox((10, 10, -10, 22), "Show Preview", value=RamsayStData.showPreview, callback=self.showPreviewCallback)

        self.w.fillColorText = vanilla.TextBox((10, 40, 110, 22), "Fill Color:")
        self.w.fillColor = vanilla.ColorWell((10, 60, 110, 40), color=RamsayStData.fillColor, callback=self.fillColorCallback)
        
        self.w.strokeColorText = vanilla.TextBox((130, 40, -10, 22), "Stroke Color:")
        self.w.strokeColor = vanilla.ColorWell((130, 60, -10, 40), color=RamsayStData.strokeColor, callback=self.strokeColorCallback)
        
        items = RamsayStData.getItems()
        columnDescriptions = [
                              dict(title="Glyph Name", key="glyphName"), 
                              dict(title="Left", key="left"), 
                              dict(title="Right", key="right"),
                              ]
        
        self.w.dataList = vanilla.List((10, 110, -10, -40), items, columnDescriptions=columnDescriptions, editCallback=self.dataListEditCallback)
        
        
        segmentDescriptions = [dict(title="+"), dict(title="-")]    
        self.w.addDel = vanilla.SegmentedButton((12, -30, 60, 20), segmentDescriptions, selectionStyle="momentary", callback=self.addDelCallback)
        self.w.addDel.getNSSegmentedButton().setSegmentStyle_(NSSegmentStyleSmallSquare)
        
        self.w.okButton = vanilla.Button((-70, -30, -15, 20), "Apply", callback=self.okCallback, sizeStyle="small")
        
        self.w.setDefaultButton(self.w.okButton)
        
        self.w.closeButton = vanilla.Button((-140, -30, -80, 20), "Cancel", callback=self.closeCallback, sizeStyle="small")
        self.w.closeButton.bind(".", ["command"])
        self.w.closeButton.bind(unichr(27), [])
        
        self.w.open()
    
    def showPreviewCallback(self, sender):
        RamsayStData.showPreview = sender.get()
        RamsayStData.save()
        self.updateView()

    def fillColorCallback(self, sender):
        RamsayStData.fillColor = sender.get()
        RamsayStData.save()
        self.updateView()
    
    def strokeColorCallback(self, sender):
        RamsayStData.strokeColor = sender.get()
        RamsayStData.save()
        self.updateView()
        
    
    def _addGlyphName(self, sender):
        glyphName = sender.get()
        if glyphName in RamsayStData.keys():
            index = 0
            for item in self.w.dataList:
                if glyphName == item.glyphName():
                    break
                index += 1
            self.w.dataList.setSelection([index])
            return
        self.w.dataList.append(RamsayStData.newItem(glyphName))
    
    def addGlyphName(self):
        AddGlyphNameSheet(self.w, self._addGlyphName)
        
    def delGlyphName(self):
        sel = self.w.dataList.getSelection()
        if sel:
            index = sel[0]
            del self.w.dataList[index]
    
    def addDelCallback(self, sender):
        if not sender.get():
            self.addGlyphName()
        else:
            self.delGlyphName()
    
    def okCallback(self, sender):
        RamsayStData.setItems(self.w.dataList)
        RamsayStData.save()
        self.updateView()
    
    def closeCallback(self, sender):
        self.w.close()
    
    def dataListEditCallback(self, sender):
        sel = sender.getSelection()
        for i in sel:
            item = sender[i]
            RamsayStData.set(item)
        
    def updateView(self):
        UpdateCurrentGlyphView()

OpenWindow(RamsayStSettingsWindowController)