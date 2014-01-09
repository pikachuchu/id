import Tkinter as tk
import tkFont
import grid
import time
import Image
import ImageTk
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.configure_count = 0
        self.tornado_image = Image.open("assets/tornado.gif")
        self.tornado_photoimage = ImageTk.PhotoImage(self.tornado_image)
        self.tornado_width = 300
        self.tornado_height = 300
        self.createWidgets()
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
    def createWidgets(self):
        top = self.winfo_toplevel()
        self.height = 15
        self.width = 15
        self.cells = [[None for col in range(self.width)] for row in range(self.height)]
        self.cell_locations = dict()
        self.text_ids = [[1 for col in range(self.width)] for row in range(self.height)]
        self.select_ids = [[None for col in range(self.width)] for row in range(self.height)]
        self.board = grid.Grid(self.height, self.width);
        self.cell_height = 50 
        self.cell_width = 50 
        self.master.bind('<Key>', self.key)
        for col in range(self.width):
            top.columnconfigure(col, weight = 1)
            self.columnconfigure(col, weight = 1)
        for row in range(self.height):
            top.rowconfigure(row, weight = 1)
            self.rowconfigure(row, weight = 1)
        for row in range(self.height):
            for col in range(self.width):
                bg = '#000000'
                self.cells[row][col] = tk.Canvas(self, height = self.cell_height, width = self.cell_width, bg = bg, bd = 0)
                self.cell_locations[self.cells[row][col]] = (row,col)
                self.cells[row][col].board_row = row
                self.cells[row][col].board_col = col
                # TODO <Configure> http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
                self.cells[row][col].bind('<Configure>', self.configureCell)
                self.cells[row][col].bind('<Button-3>', self.kill)
                self.cells[row][col].bind('<Button-1>', self.select)
                self.cells[row][col].bind('<Control-Button-1>', self.toggle)
                self.cells[row][col].grid(sticky = tk.N+tk.S+tk.E+tk.W, column = col, row = row)
        self.master.title("Intelligent Design")
        self.drawThings()
        self.nextButton = tk.Button(self, text = "Next", command = self.updateBoard)
        self.nextButton.grid(column = self.width, row = 0, sticky = tk.N)
        self.resetButton = tk.Button(self, text = "Reset", command = self.resetBoard)
        self.resetButton.grid(column = self.width, row = 1, sticky = tk.N)
    def updateBoard(self):
        if self.board.external():
            self.drawThings()
            self.update()
            time.sleep(0.3)
        self.board.internal()
        self.drawThings()
    def resetBoard(self):
        self.board.reset()
        self.drawThings()
    def key(self, event):
        if event.char == 'q':
            self.board.move((-1,-1))
        elif event.char == 'w':
            self.board.move((-1,0)) 
        elif event.char == 'e':
            self.board.move((-1,1)) 
        elif event.char == 'a':
            self.board.move((0,-1)) 
        elif event.char == 'd':
            self.board.move((0,1)) 
        elif event.char == 'z':
            self.board.move((1,-1)) 
        elif event.char == 'x':
            self.board.move((1,0))
        elif event.char == 'c':
            self.board.move((1,1))
        else:
            return
        self.drawThings()
    def kill(self, event):
        brow,bcol = self.cell_locations[event.widget]
        change = False
        if (brow,bcol) in self.board.selected:
            for row, col in self.board.selected:
                change = self.board.kill(row,col) or change
            change = self.board.clearSelection() or change 
        else:
            change = self.board.kill(brow,bcol) or change
            change = self.board.clearSelection() or change
        if change:
            self.drawThings()
    def select(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            self.board.select(brow,bcol)
            self.drawThings()
        else:
            self.board.clearSelection()
            self.drawThings()
    def toggle(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            self.board.toggle(brow,bcol)
            self.drawThings()
    def configureCell(self, event):
        # FIXME creates n^2 events when ideally only use one
        self.configure_count+=1
        if (self.configure_count == self.height * self.width):
            # have we received all of these events?
            self.cell_height=event.height
            self.cell_width=event.height
            self.drawThings()
            self.configure_count = 0
    def outlineIfSelected(self, row,col):
        if self.select_ids[row][col] != None:
            self.cells[row][col].delete(self.select_ids[row][col])
            self.select_ids[row][col] = None
        if (row,col) in self.board.selected:
            self.select_ids[row][col] = self.cells[row][col].create_rectangle(0,0,self.cell_width,self.cell_height,outline='#FFFF33',width=10)
    def drawThings(self):
        font = tkFont.Font(size=3 * min(self.cell_height,self.cell_width) / 5)
        for row in range(self.height):
            for col in range(self.width):
                self.cells[row][col].delete(self.text_ids[row][col])
                team = self.board.cells[row][col].team
                strength = self.board.cells[row][col].strength
                self.outlineIfSelected(row,col)
                if team == "R":
                    color = '#FF0000'
                elif team == "B":
                    color = '#0000FF'
                elif team in grid.neutral_teams:
                    color = '#e4e4e4'
                if team != grid.neutral_str:
                    if team == grid.tornado_str:
                        if self.tornado_width != self.cell_width or self.tornado_height != self.cell_height:
                            self.tornado_image.thumbnail((self.cell_width,self.cell_height), Image.ANTIALIAS)
                            self.tornado_photoimage = ImageTk.PhotoImage(self.tornado_image)
                            self.tornado_width = self.cell_width
                            self.tornado_height = self.cell_height
                        self.text_ids[row][col] = self.cells[row][col].create_image(self.cell_height/2,self.cell_width/2,image=self.tornado_photoimage)
                    else:
                        self.text_ids[row][col] = self.cells[row][col].create_text(self.cell_height/2,self.cell_width/2,text=str(strength), fill=color, font = font)
                    self.cells[row][col].grid(column = col, row = row)
       
#def reportEvent(event):
#    print 'keysym=%s, keysym_num=%s' % (event.keysym, event.keysym_num)
root = Application()
root.mainloop()
