from AppKit import NSImage
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController

from lib.features.featureEditor import DoodleFeatureTextEditor
from lib.settings import ufoApps
from mojo.roboFont import OpenWindow

def insertFeatureToolbarImage():
    im = NSImage.imageNamed_("toolbarFeatures")
    return ufoApps.createToolbarIcon(im)

class GroupsToFeatureText(BaseWindowController):
    
    def __init__(self):
        self.font = CurrentFont()
        if self.font is None:
            from vanilla.dialogs import message
            message("No Font is open.", "Open or create a font to convert groups to feature syntax groups.")
            return
        
        groupsNames = self.font.groups.keys()
        groupsNames.sort()
        
        self.w = Window((400, 400), "Feature Group Converter", minSize=(300, 300))
        
        toolbarItems = [
            dict(itemIdentifier="insert",
                label="Insert In Font",
                imageObject=insertFeatureToolbarImage(),
                callback=self.toolbarInsert,
                ),
            ]
        toolbar = self.w.addToolbar(toolbarIdentifier="GroupsToFeatureTextToolbar", toolbarItems=toolbarItems, addStandardItems=False)
        
        self.w.groupList = List((0, 0, 150, -0), groupsNames, selectionCallback=self.groupListSelectionCallback)
        self.w.feaText = DoodleFeatureTextEditor((150, 0, -0, -0), "")
        self.w.groupList.setSelection([])
                
        self.w.assignToDocument(self.font.document())
        
        self.w.open()
    
    def _selectedGroupNames(self):
        groupList = self.w.groupList
        sel = groupList.getSelection()
        if not sel:
            return []
        return [groupList[i] for i in sel]
    
    def _feaText(self):
        return self._feaTextForGroupNames(self._selectedGroupNames())
        
    def _feaTextForGroupNames(self, groupNames):
        feaText = []
        for groupName in groupNames:
            groupGlyphs = self.font.groups.get(groupName, [])
            t = "@%s = [%s];" %(groupName, " ".join(groupGlyphs))
            ## replace the '
            t = t.replace("'", "")
            feaText.append(t)
        return "\n".join(feaText)
        
    def groupListSelectionCallback(self, sender):
        feaText = self._feaText()
        self.w.feaText.set(feaText)
    
    def toolbarInsert(self, sender):
        existingText = self.font.features.text
        spaceLessText = existingText.replace("\n", "").replace(" ", "")
        groupNames = self._selectedGroupNames()
        
        validGroupNames = []
        invalidText = []
        for groupName in groupNames:
            if "@%s=[" % groupName in spaceLessText:
                invalidText.append("Group '%s' already in feature." %groupName)
            else:
                validGroupNames.append(groupName)

        feaText = self._feaTextForGroupNames(validGroupNames)
        if feaText:
            feaText += "\n" + existingText
            self.font.features.text = feaText
        
        if invalidText:
            self.showMessage("Groups names already in Feature", "Edit the feature file and try to insert them again.\n\nSee output window for dublicated groupnames.")
            print "-" * 30
            print "Some group names are already created in the feature file." 
            print "Those will not be added to prevent dublication and compiling errors."
            print 
            print "\n".join(invalidText)
            print "-" * 30
        
OpenWindow(GroupsToFeatureText)