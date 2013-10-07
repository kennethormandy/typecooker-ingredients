from AppKit import *
from vanilla import *
from defconAppKit.windows.baseWindow import BaseWindowController

from lib.scripting.codeEditor import OutPutEditor

from views import TinyDrawBotTextEditor, DrawView



def createSavePDFImage():
    im = NSImage.imageNamed_("toolbarScriptNew")
    pdfText = NSString.stringWithString_("PDF")

    shadow = NSShadow.alloc().init()
    shadow.setShadowOffset_((0, -1))
    shadow.setShadowColor_(NSColor.whiteColor())
    shadow.setShadowBlurRadius_(1)
                        
    attributes = {
                NSFontAttributeName : NSFont.boldSystemFontOfSize_(7),
                NSForegroundColorAttributeName : NSColor.darkGrayColor(),
                NSShadowAttributeName : shadow
                }
    
    pdfSaveImage = NSImage.alloc().initWithSize_(im.size())
    
    pdfSaveImage.lockFocus()
    im.drawAtPoint_fromRect_operation_fraction_((0, 0), NSZeroRect, NSCompositeSourceOver, 1)
    pdfText.drawAtPoint_withAttributes_((10, 10), attributes)
    pdfSaveImage.unlockFocus()
    
    return pdfSaveImage


class TinyDrawBot(BaseWindowController):
    def __init__(self):
        self.w = Window((800, 600), "Tiny Draw Bot", minSize=(200, 200))
        try:
            self.w.getNSWindow().setCollectionBehavior_(128) #NSWindowCollectionBehaviorFullScreenPrimary
        except:
            pass
        
        self.editor = TinyDrawBotTextEditor((0, 0, -0, -0))
        self.codeOutPut = OutPutEditor((0, 0, -0, -0))
        self.editor.setOutputView_(self.codeOutPut)
        
        self.drawView = DrawView(self.codeOutPut)
        self.drawScrollView = ScrollView((0, 0, -0, -0), self.drawView)
        
        self.editor.setDrawView(self.drawView)
        
        textPaneDescriptors = [
            dict(view=self.editor, identifier="codeTextView"),
            dict(view=self.codeOutPut, identifier="outputTextView", size=100),
        ]
        self.textSplit = SplitView((0, 0, -0, -0), textPaneDescriptors, isVertical=False)
        
        paneDescriptors = [
            dict(view=self.drawScrollView, identifier="codeView"),
            dict(view=self.textSplit, identifier="drawView"),
        ]
        self.w.split = SplitView((0, 0, -0, -0), paneDescriptors)
        
        
        toolbarItems = [
            dict(itemIdentifier="run",
                label="Run",
                imageNamed="toolbarRun",
                callback=self.toolbarRun,
                ),
            dict(itemIdentifier="comment",
                label="Comment",
                imageNamed="toolbarComment",
                callback=self.toolbarComment,
                ),
            dict(itemIdentifier="uncomment",
                label="Uncomment",
                imageNamed="toolbarUncomment",
                callback=self.toolbarUncomment,
                ),
            dict(itemIdentifier="indent",
                label="Indent",
                imageNamed="toolbarIndent",
                callback=self.toolbarIndent,
                ),
            dict(itemIdentifier="dedent",
                label="Dedent",
                imageNamed="toolbarDedent",
                callback=self.toolbarDedent,
                ),
            dict(itemIdentifier=NSToolbarFlexibleSpaceItemIdentifier),
            
            dict(itemIdentifier="save",
                label="Save",
                imageNamed="toolbarScriptSave",
                callback=self.toolbarSave,
                ),
            dict(itemIdentifier="savePDF",
                label="Save PDF",
                imageObject=createSavePDFImage(),
                callback=self.toolbarSavePDF,
                ),
            
            dict(itemIdentifier=NSToolbarSpaceItemIdentifier),
            
            dict(itemIdentifier="reload",
                label="Reload",
                imageNamed="toolbarScriptReload",
                callback=self.toolbarReload,
                ),
            dict(itemIdentifier="new",
                label="New",
                imageNamed="toolbarScriptNew",
                callback=self.toolbarNewScript,
                ),
            dict(itemIdentifier="open",
                label="Open",
                imageNamed="toolbarScriptOpen",
                callback=self.toolbarOpen,
                ),
            dict(itemIdentifier=NSToolbarFlexibleSpaceItemIdentifier),
            ]
        toolbar = self.w.addToolbar(toolbarIdentifier="tinyDrawBotScriptingToolbar", toolbarItems=toolbarItems, addStandardItems=False)
        
        self.setUpBaseWindowBehavior()
        
        documentController = NSDocumentController.sharedDocumentController()
        documentClass = documentController.documentClassForType_("Python Source File")
        self.document = documentClass.alloc().init()
        self.document.vanillaWindowController = self
        documentController.addDocument_(self.document)
        self.document.addWindowController_(self.w.getNSWindowController())
        
        self.w.open()
    
    def set(self, path, force=False):
        self.editor.openFile(path, force=force)
    
    def setTextInEditor(self, sender, item=None):
        if item is not None:
            self.set(item.path)
            
    def getText(self):
        return self.editor.get()
    
    def toolbarRun(self, sender):
        self.editor.run()
    
    def toolbarComment(self, sender):
        self.editor.comment()
        
    def toolbarUncomment(self, sender):
        self.editor.uncomment()
        
    def toolbarIndent(self, sender):
        self.editor.indent()
        
    def toolbarDedent(self, sender):
        self.editor.dedent()
        
    def toolbarShowLineNumbers(self, sender):
        self.editor.toggleLineNumbers()
    
    def toolbarReload(self, sender):
        self.editor.reload()
    
    def toolbarOpen(self, sender):
        self.editor.open()
    
    def toolbarNewScript(self, sender):
        self.editor.newScript()
    
    def _savePDF(self, path):
        self.drawView.savePDF_(path)
    
    def toolbarSavePDF(self, sender):
        self.showPutFile(["pdf"], self._savePDF)
    
    def toolbarSave(self, sender):
        if NSEvent.modifierFlags() & NSAlternateKeyMask:
            self.document.saveDocumentAs_(self)
        else:
            self.document.saveDocument_(self)
    
    def toolbarAddScriptToMenu(self, sender):
        self.editor.addScriptToMenu()
    
        
    
    
TinyDrawBot()