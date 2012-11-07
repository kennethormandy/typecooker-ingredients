# tile windows

from AppKit import *


def tile():

    windows = [w for w in NSApp().orderedWindows() if w.isVisible()]

    screen = NSScreen.mainScreen()
    (x, y), (w, h) = screen.visibleFrame()

    altDown = NSEvent.modifierFlags() & NSAlternateKeyMask

    NSApp().arrangeInFront_(None)

    prefWindow = None
    for window in windows:
        if hasattr(window, "windowName") and window.windowName() == "PreferencesWindow":
            prefWindow = window
            break

    if prefWindow is not None:
        windows.remove(prefWindow)

    scriptingWindow = None
    for window in windows:
        if hasattr(window, "windowName") and window.windowName() == "ScriptingWindow":
            scriptingWindow = window
            break

    if scriptingWindow is not None:
        scriptinWindowWidth = w/5.
        w -= scriptinWindowWidth
        scriptingWindow.setFrame_display_animate_(NSMakeRect(x+w, y, scriptinWindowWidth, h), True,  altDown)
        windows.remove(scriptingWindow)

    tileInfo = {
                1 : [[1]],
                2 : [[1], [1]],
                3 : [[1], [1, 1]],
                4 : [[1, 1], [1, 1]],
                5 : [[1, 1], [1, 1, 1]],
                }

    windowsToTile = windows[:5]
    windowsToHide = windows[5:]

    if windowsToTile:
        arrangement = tileInfo[len(windowsToTile)]
        maxHeight = len(arrangement)
        diffx = x
        diffy = y
        c = 0
        for i in arrangement:
            maxWidth = len(i)        
            for j in i:
                window = windows[c]
                window.setFrame_display_animate_(NSMakeRect(diffx, diffy, w/float(maxWidth), h/float(maxHeight)), True, altDown)
                c += 1
            
                diffx += w/float(maxWidth)
            diffx = x
            diffy += h/float(maxHeight)

    for window in windowsToHide:
        window.miniaturize_(None)