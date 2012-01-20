from AppKit import *
from random import choice
from datetime import datetime
from vanilla import *

from defconAppKit.windows.baseWindow import BaseWindowController
from typeCookerData import stylesData, parametersData

from mojo.roboFont import OpenWindow

def generateTypeCooker(data, level):
    
    result = []
    
    for key in data["keys"]:
        pool = []
        item = data[key]
    
        for index, pick in enumerate(item):
            if pick["level"] > level:
                continue
            for weightCount in range(pick["weight"]):
                pool.append(pick)
        if pool:
            randomPick = choice(pool)
            result.append((key, randomPick))
    return result

class TypeCookerWindow(BaseWindowController):
    
    title = "TypeCooker.com"
    
    def __init__(self):
        self.w = Window((600, 300), self.title, minSize=(600, 250), maxSize=(600, 1000000))
        
        self.w.levels = RadioGroup((10, 10, -10, 22), ["starter", "easy", "class", "experienced", "pro"], isVertical=False, callback=self.generate)
        self.w.levels.set(1)
        self.w.recipe = RadioGroup((10, 40, 250, 22), ["by parameter", "by style"], isVertical=False, callback=self.generate)
        self.w.recipe.set(0)
        self.w.output = TextEditor((10, 70, -10, -30), readOnly=True)
        
        fontSize = 15
        
        f = NSFont.fontWithName_size_("Menlo", fontSize)
        if not f:
            f = NSFont.fontWithName_size_("Monaco", fontSize)
            
        self.w.output.getNSTextView().setFont_(f)
        
        self.generate()
        self.w.open()
    
    def generate(self, sender=None):
        data = None
        print self.w.recipe.get(), self.w.levels.get()
        if self.w.recipe.get() == 0:
            data = parametersData
        elif self.w.recipe.get() == 1:
            data = stylesData
        level = self.w.levels.get()
        
        if data is None or level is None:
            return
        
        level += 1
        
        result = generateTypeCooker(data, level)
        
        txt = ""
        maxLenght = 25
        for name, pick in result:
            whiteSpace = maxLenght-len(name)
            txt += "%s%s%s\n" %(name, " "*whiteSpace, pick["name"])
        
        now = datetime.now()
        txt += "\n\n%s" %(now.strftime("%A %d, %B %Y %H:%M"))
        
        txt += "\n%s" %self.title
        self.w.output.set(txt)
        
        textView = self.w.output.getNSTextView()
        textStorage = textView.textStorage()
        
        for name, pick in result:
            url = pick.get("url")
            if url:
                r = (txt.find(name)+maxLenght, len(pick["name"]))
                if not url.startswith("http://"):
                    url = "http://typecooker.com/" + url
                textStorage.addAttribute_value_range_(NSLinkAttributeName, url, r)
        
        url = "http://typecooker.com/"
        r = (len(txt)-len(self.title), len(self.title))
        
        textStorage.addAttribute_value_range_(NSLinkAttributeName, url, r)

OpenWindow(TypeCookerWindow)