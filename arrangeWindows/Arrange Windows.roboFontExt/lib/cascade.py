## cascade windows
from AppKit import *

def cascade():

    windows = [w for w in NSApp().orderedWindows() if w.isVisible()]

    screen = NSScreen.mainScreen()
    (x, y), (w, h) = screen.visibleFrame()

    altDown = NSEvent.modifierFlags() & NSAlternateKeyMask

    NSApp().arrangeInFront_(None)

    leftTop = (x, y+h)
    for window in reversed(windows):
        window.setFrameTopLeftPoint_(leftTop)
        leftTop = window.cascadeTopLeftFromPoint_(leftTop)
