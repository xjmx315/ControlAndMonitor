"""
2024-07-20
jmtui.py

Basic input and output functions for tui
Block by Block tui system
Handling events
"""
import curses

class Box:
    def __init__(self, title = '', size_y = 7, size_x = 20, loc_y = 0, loc_x = 0):
        self.title = title
        self.size_y = size_y
        self.size_x = size_x
        self.loc_y =  loc_y
        self.loc_x = loc_x
        self.box = curses.newwin(self.size_y, self.size_x, self.loc_y, self.loc_x)
        self.window = self.box.derwin(self.size_y-2, self.size_x-2, 1, 1)
        self.boxColor = 0
        self.titleLoc = -1
        
    def draw(self):
        self.box.attrset(curses.color_pair(self.boxColor))
        self.box.box()
        if self.titleLoc == 1:
            self.box.addstr(0, (self.size_x-len(self.title))-2, self.title)
        elif self.titleLoc == 0:
            self.box.addstr(0, (self.size_x-len(self.title))//2, self.title)
        else:
            self.box.addstr(0, 2, self.title)
        #self.box.refresh()

    def refresh(self):
        self.box.refresh()
        
    def moveTo(self, newy, newx):
        self.loc_y = newy
        self.loc_x = newx
        self.window.mvwin(newy+1, newx+1)
        self.box.mvwin(newy, newx)
     
    def getyx(self):
        return self.loc_y, self.loc_x
        
    def setBoxcolor(self, color):
        self.boxColor = color
        
    def setTitleLoc(self, loc = -1):
        if loc == 'center':
            loc = 0
        elif loc == 'right':
            loc = 1
        else:
            loc = -1
        self.titleLoc = loc