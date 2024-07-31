

import curses
import time
import os
stdscr = curses.initscr()
curses.cbreak()
curses.noecho()
stdscr.keypad(1)

try:
# Run your code here
    for i in range(100):
        height,width = os.get_terminal_size()
        num = min(height,width)
        for x in range(num):
            stdscr.addch(x,x,'X')
        stdscr.refresh()
        time.sleep(0.2)
finally:
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()