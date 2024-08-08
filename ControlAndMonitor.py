# -*- coding: utf-8 -*-
import curses
import random
import time
import jmtui

class Com(jmtui.Box):
    def __init__(self, num = 0):
        self.num = num
        super().__init__(f"Com {num}")
        self.condition = "Await"
        self.todo = 21
        self.done = 0
        
        self.selected = 0
        
    def __str__(self):
        return self.title
        
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
        if self.selected:
            self.window.bkgd(' ', curses.color_pair(6))
        else:
            self.window.bkgd(' ', curses.color_pair(4))
        self.window.move(0, 0)
        self.window.addstr(f"condition: {self.condition}\n")
        self.window.addstr(f"done/todo: {self.done}/{self.todo}\n")
        self.window.addstr(f"{self.done*100//self.todo}%\n", curses.A_REVERSE)
        
        self.refresh()
        
    def select(self):
        self.selected = 1
        
    def unselect(self):
        self.selected = 0

        
class StateBox(jmtui.Box):
    def __init__(self, y, x, loc_y, loc_x):
        super().__init__("STATE", y, x, loc_y, loc_x)
        self.fineCom = 0
        self.errorCom = 0
        self.awaitCom = 0
        self.doneCom = 0
        self.totalCom = lambda: self.fineCom + self.errorCom + self.awaitCom + self.doneCom
        self.setTitleLoc("center")
        self.logData = ''
        
    def drawComState(self, startX = 0):
        self.window.move(0, startX + 0)
        self.window.addstr(f"Await: {self.awaitCom}")
        self.window.move(0, startX + 13)
        self.window.addstr(f"Fine: {self.fineCom}", curses.color_pair(2))
        self.window.move(1, startX + 0)
        self.window.addstr(f"Error: {self.errorCom}", curses.color_pair(1))
        self.window.move(1, startX + 13)
        self.window.addstr(f"Done: {self.doneCom}", curses.color_pair(3))
        self.window.move(2, startX + 6)
        self.window.addstr(f"Total: {self.totalCom()}", curses.A_BOLD | curses.A_REVERSE)
        
    def drawTime(self, startY = 1, startX = 30):
        self.window.move(startY, startX)
        self.window.addstr(f"{time.localtime()[3]}:{time.localtime()[4]}:{time.localtime()[5]}")
        
    def drawLog(self, startX = 50):
        self.window.move(1, startX)
        self.window.addstr(self.logData)
        
    def draw(self):
        super().draw()
        self.drawComState()
        self.drawTime()
        self.drawLog()
        self.refresh()
        
    def updateCom(self, await_ = 0, fine = 0, done = 0, error = 0):
        self.awaitCom += await_
        self.fineCom += fine
        self.doneCom += done
        self.errorCom += error
        
    def log(self, data):
        self.logData = data
        


class ConsolManager:
    def __init__(self, stdscr):
        self.window = stdscr
        self.count = 0
        self.coms = []
        self.page = 0
        self.comsize = (7, 20)
        self.selectedCom = None
        
        self._updateMaxyx()
        self._getCenter = lambda whole, thing: (whole - thing)//2
        self.grid = self._getGrid()
        self.state = StateBox(5, self.maxx, 0, 0)
        self.emptyCom = curses.newwin(self.comsize[0], self.comsize[1], 0, 0)
        
    def _clearComLoc(self, y, x):
        for i in range(y, y + self.comsize[0]):
            self.window.move(i, x)
            self.window.addstr(" "*self.comsize[1])
        self.window.refresh()
        
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
        
        self.state.updateCom(1)        
        #y, x = self._getNextLoction(*self.coms[-1].getyx()) if self.coms else (0, 0)
        #com.moveTo(y, x)
        self.coms.append(com)
        
        #self._updatePages()
        
    def delCom(self):
        if self.selectedCom:
            for i in range(len(self.coms)):
                if self.coms[i] is self.selectedCom:
                    del self.coms[i]
                    break
        
    def do(self):
        #st = (self.page[0]-1)*self._getDrawAbleInOnePage()
        #en = min(len(self.coms)-st, self._getDrawAbleInOnePage()+st)
        self.state.draw()
        for i in range(len(self.grid)):
            if len(self.coms) > i + self.page:
                self.coms[i+self.page].moveTo(*self.grid[i])
                self.coms[i+self.page].draw()
            else:
                self.emptyCom.mvwin(*self.grid[i])
                self.emptyCom.clear()
                self.emptyCom.refresh()
        #self.window.refresh()
                
    def pageTurn(self, n):
        row = ((self.maxx-1) // self.comsize[1])
        self.page += n*row
        self.page = min(self.page, (len(self.coms)//row-1)*row)
        self.page = max(self.page, 0)
        
    def log(self, data):
        self.state.log(data)
        
    def _isInComArea(self, y, x, sty, stx):
        if sty < y < self.comsize[0] + sty and stx < x < self.comsize[1] + stx:
            return 1
        return 0
        
    def _getIndexMouseClicked(self, y, x): #Todo: can make faster
        for i in range(len(self.grid)):
            if self._isInComArea(y, x, *self.grid[i]):
                return i
        return -1
    
    def _getComWithGridIndex(self, index):
        if len(self.coms) > index + self.page:
            return self.coms[index + self.page]
        return None
    
    def mouse(self, y, x):
        index = self._getIndexMouseClicked(y, x)
        com = self._getComWithGridIndex(index) if index != -1 else None
        self.selectCom(com)

    def selectCom(self, com):
        if self.selectedCom:
            self.selectedCom.unselect()
        self.selectedCom = com
        if self.selectedCom:
            self.selectedCom.select()
        

class Manager:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        stdscr.nodelay(1)
        self.consolMeneger = ConsolManager(stdscr)
        self.keyInputs = []
        self.logs = []
        self.logs.append(self.consolMeneger.grid)
        
    def _getKeyInputs(self):
        key = self.stdscr.getch() #this code clean stdscr for farst run. 
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
        elif command == ord('q'):
            return -1
        elif command == ord('n'):
            self.consolMeneger.pageTurn(1)
        elif command == ord('b'):
            self.consolMeneger.pageTurn(-1)
        elif command == curses.KEY_MOUSE:
            self.mouseEvent(*curses.getmouse())
        elif command == ord('d'):
            self.consolMeneger.delCom()
            
    def mouseEvent(self, id, x, y, z, data):
        #self.consolMeneger.log(f"{id} {x} {y} {z} {data}")
        self.consolMeneger.mouse(y, x)
        
    def start(self):
        self.updateKey()
        self.consolMeneger.do()
        while 1:
            self.updateKey()
            for command in self.keyInputs:
                if self.doCommand(command) == -1:
                    return self.logs
            if self.keyInputs:
                self.consolMeneger.do()
            else: 
                time.sleep(0.1)
        

def setConsol():
    curses.cbreak()
    curses.noecho()
    stdscr.keypad(1)
    curses.curs_set(0)
    curses.mousemask(1)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)
    curses.init_pair(2, curses.COLOR_GREEN, -1)
    curses.init_pair(3, curses.COLOR_BLUE, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)
    curses.init_pair(5, curses.COLOR_BLACK, -1)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_YELLOW)
    
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