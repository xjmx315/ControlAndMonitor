# -*- coding: utf-8 -*-
import curses
import random
import time
import jmtui

class Com(jmtui.Box):
    def __init__(self, num = 0):
        self.num = num
        super().__init__(f"Com {num}")
        self.condition = "Fine"
        self.todo = 21
        self.done = 0
        
    def progrese(self):
        return self.done*100//self.todo
    
    def setBoxcolor(self):
        if self.condition == "Done":
            super().setBoxcolor(3)
        elif self.condition == "Fine":
            super().setBoxcolor(2)
        elif self.condition == "Erorr":
            super().setBoxcolor(1)
        else:
            super().setBoxcolor(4)
                
    def draw(self):
        super().draw()
        self.setBoxcolor()
        self.window.move(0, 0)
        self.window.addstr(f"condition: {self.condition}\n")
        self.window.addstr(f"done/todo: {self.done}/{self.todo}\n")
        self.window.addstr(f"{self.done*100//self.todo}%\n", curses.A_REVERSE)
        
        self.window.refresh()

        
class StateBox(jmtui.Box):
    def __init__(self, y, x, loc_y, loc_x):
        super().__init__("STATE", y, x, loc_y, loc_x)
        self.fineCom = 0
        self.errorCom = 0
        self.awaitCom = 0
        self.complitCom = 0
        self.totalCom = lambda: self.fineCom + self.errorCom + self.awaitCom + self.complitCom
        self.setTitleLoc("center")
        
    def drawComState(self, startX = 0):
        self.window.move(0, startX + 0)
        self.window.addstr(f"Awate: {self.awaitCom}")
        self.window.move(0, startX + 13)
        self.window.addstr(f"Fine: {self.fineCom}", curses.color_pair(2))
        self.window.move(1, startX + 0)
        self.window.addstr(f"Error: {self.errorCom}", curses.color_pair(1))
        self.window.move(1, startX + 13)
        self.window.addstr(f"Done: {self.complitCom}", curses.color_pair(3))
        self.window.move(2, startX + 6)
        self.window.addstr(f"Total: {self.totalCom()}", curses.A_BOLD | curses.A_REVERSE)
        
    def drawTime(self, startY = 1, startX = 30):
        self.window.move(startY, startX)
        self.window.addstr(f"{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}")
        
    def draw(self):
        super().draw()
        self.drawComState()
        self.drawTime()
        


class ConsolManager:
    def __init__(self, stdscr):
        self.window = stdscr
        self.count = 0
        self.coms = []
        self.page = 0
        self.comsize = (7, 20)
        
        self._updateMaxyx()
        self._getCenter = lambda whole, thing: (whole - thing)//2
        self.grid = self._getGrid()
        self.state = StateBox(5, self.maxx, 0, 0)

        
    def _getGrid(self):
        yStart = 5
        xStart = self._getCenter(self.maxx, self.comsize[1]*((self.maxx-1)//self.comsize[1]))
        
        grid = [(yStart, xStart)]
        y, x = self._getNextLoction(yStart, xStart, yStart, xStart)
        
        while (y, x) != grid[0]:
            grid.append((y, x))
            y, x = self._getNextLoction(y, x, yStart, xStart)
            
        return grid
        
    def _updateMaxyx(self):
        self.maxy, self.maxx = self.window.getmaxyx()
        
    def _getNextLoction(self, y, x, yStart = 0, xStart = 0):
        x += self.comsize[1]
        if x >= self.maxx - self.comsize[1]:
            x = xStart
            y += self.comsize[0]
        if y >= self.maxy - self.comsize[0]:
            y = yStart
        return y, x
        
    def _updatePosition(self, n):
        for i in range(len(self.grid)):
            if len(self.coms) > i:
                self.coms[i].moveTo(*self.grid[i])
            else:
                break
            
    def _getDrawAbleInOnePage(self): #ToDo: can make faster with mathic operation
        num = 1
        y, x = self._getNextLoction(0, 0)
        while (y, x) != (0, 0):
            y, x = self._getNextLoction(y, x)
            num += 1
        return num
    
    def _updatePages(self):
        maxrear = self._getDrawAbleInOnePage()
        new = len(self.coms)//maxrear + (1 if len(self.coms)%maxrear else 0)
        if self.page[1] != new:
            self.page[1] = new
            self.page[0] = max(self.page[0], self.page[1])

    def newCom(self): #To do
        com = Com(self.count)
        self.count += 1
        
        #y, x = self._getNextLoction(*self.coms[-1].getyx()) if self.coms else (0, 0)
        #com.moveTo(y, x)
        self.coms.append(com)
        
        #self._updatePages()
        
    def delCom(self, n):# sucess -> 0 / not -> 1
        for i in range(len(self.coms)):
            if self.coms[i].num == n:
                del self.coms[i]
                self._updatePosition()
                self._updatePages()
                return 0
        return 1
        
    def do(self):
        #st = (self.page[0]-1)*self._getDrawAbleInOnePage()
        #en = min(len(self.coms)-st, self._getDrawAbleInOnePage()+st)
        self.state.draw()
        for i in range(len(self.grid)):
            if len(self.coms) > i+self.page:
                self.coms[i+self.page].moveTo(*self.grid[i])
                self.coms[i+self.page].draw()
            else:
                break
            
    def pageTurn(self, n):
        self.page += n*((self.maxx-1) // self.comsize[1])
        self.page = min(self.page, len(self.coms)//(self.maxx // self.comsize[1]))
        self.page = max(self.page, 0)
        

class Manager:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        stdscr.nodelay(1)
        self.consolMeneger = ConsolManager(stdscr)
        self.keyInputs = []
        self.logs = []
        self.logs.append(self.consolMeneger.grid)
        
    def _getKeyInputs(self):
        key = self.stdscr.getch()
        while key != -1:
            self.keyInputs.append(key)
            key = self.stdscr.getch()
            
    def updateKey(self):
        self.logs.extend(self.keyInputs)
        self.keyInputs = []
        self._getKeyInputs()

    def doCommand(self, command):
        if command == ord('a'):
            self.consolMeneger.newCom()
            return 0
        if command == ord('q'):
            return -1
        if command == ord('n'):
            self.consolMeneger.pageTurn(1)
        if command == ord('b'):
            self.consolMeneger.pageTurn(-1)
            

    def start(self):
        while 1:
            self.updateKey()
            for com in self.keyInputs:
                if self.doCommand(com) == -1:
                    return self.logs
            self.consolMeneger.do()
        

def setConsol():
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(1)
    curses.curs_set(0)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)
    
def unsetConsol(log = 'No Logs'):
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    print(log)
    input("\npress Enter key to exit...")
    
if __name__ == "__main__":
    stdscr = curses.initscr()

    setConsol()
    
    manager = Manager(stdscr)
    logs = manager.start()
    
    
    unsetConsol(logs)
else:
    stdscr = curses.initscr()

    setConsol()
    
    logs = []
    manager = ConsolManager(stdscr)
    
    manager.newCom()
    manager.newCom()
    #manager.newCom()
    manager.do()
    time.sleep(1)
    logs.append(manager.coms[-1].getyx())
    
    
    unsetConsol(logs)