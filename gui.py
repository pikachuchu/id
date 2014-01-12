import Tkinter as tk
import tkFont
import grid
import time
from PIL import Image
from PIL import ImageTk
class Application(tk.Frame):
    def photo(self,size):
        if size in self.tornado_images:
            self.tornado_image = self.tornado_images[size]
            self.tornado_photo = self.tornado_photos[size]
        else:
            self.tornado_image = Image.open("assets/tornado.gif")
            self.tornado_image.thumbnail(size, Image.ANTIALIAS)
            self.tornado_photoimage = ImageTk.PhotoImage(self.tornado_image)
            self.tornado_images[size] = self.tornado_image
            self.tornado_photos[size] = self.tornado_photos
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.tornado_images = dict()
        self.tornado_photos = dict()
        self.tornado_width = 300
        self.tornado_height = 300
        self.photo((300,300))
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
        # TODO <Configure> http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
        self.bind('<Configure>', self.configure)
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
                self.cells[row][col].bind('<Button-3>', self.kill)
                self.cells[row][col].bind('<Button-1>', self.select)
                self.cells[row][col].bind('<Double-Button-1>', self.selectAll)
                self.cells[row][col].bind('<Control-Button-1>', self.toggle)
                self.cells[row][col].bind('<Control-Double-Button-1>', self.addAll)
                self.cells[row][col].grid(sticky = tk.N+tk.S+tk.E+tk.W, column = col, row = row)
        self.master.title("Intelligent Design")
        self.specialization_menu = tk.LabelFrame(self, text='Specialize')
        self.specializations = ['Warrior','Medic','Cleric','Scientist','Farmer','Hunter']
        self.specialization_buttons = []
        self.buttonWidth = 10 # letters
        self.buttonHeight = 1 # letters
        x = -1
        y = 0
        for option in self.specializations:
            x += 1
            if x > 1:
                x = 0
                y += 1
            self.specialization_buttons.append(tk.Button(self.specialization_menu, text = option, command = getattr(self,'spec'+option), width = self.buttonWidth, height = self.buttonHeight))
            self.specialization_buttons[-1].grid(column = x, row = y)
        self.nextButton = tk.Button(self, text = "Next", command = self.updateBoard, width = self.buttonWidth, height = self.buttonHeight)
        self.nextButton.grid(column = self.width, row = 0, sticky = tk.N)
        self.resetButton = tk.Button(self, text = "Reset", command = self.resetBoard, width = self.buttonWidth, height = self.buttonHeight)
        self.resetButton.grid(column = self.width, row = 1, sticky = tk.N)
        self.spartaButton = tk.Button(self, text = "300", command = self.step300, width = self.buttonWidth, height = self.buttonHeight)
        self.spartaButton.grid(column = self.width, row = 2, sticky = tk.N)
        self.drawThings()
    def specWarrior(self):
        self.specialize('Warrior')
    def specMedic(self):
        self.specialize('Medic')
    def specCleric(self):
        self.specialize('Cleric')
    def specScientist(self):
        self.specialize('Scientist')
    def specFarmer(self):
        self.specialize('Farmer')
    def specHunter(self):
        self.specialize('Hunter')
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
    def step300(self):
        for i in range(300):
            self.board.step()
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
        elif event.char == 's':
            if self.board.selected:
                top = self.winfo_toplevel()
                if self.specialization_menu.winfo_width() == 1:
                    self.specialization_menu.place(x=event.x, y=event.y,anchor='center')
                    self.update()
                x = max(event.x, self.specialization_menu.winfo_width() / 2)
                x = min(x, top.winfo_width() - self.specialization_menu.winfo_width() / 2)
                board_width = sum([self.cells[0][i].winfo_width() for i in range(self.width)])
                x = min(x, board_width - self.specialization_menu.winfo_width() / 2)
                y = max(event.y, self.specialization_menu.winfo_height() / 2)
                y = min(y, top.winfo_height() - self.specialization_menu.winfo_height() / 2)
                board_height = sum([self.cells[i][0].winfo_height() for i in range(self.height)])
                y = min(y, board_height - self.specialization_menu.winfo_height() / 2)
                self.specialization_menu.place(x=x, y=y,anchor='center')
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
    def specialize(self,specialization):
        self.board.specialize(specialization)
        self.specialization_menu.place_forget()
        self.drawThings()
    def select(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            self.board.select(brow,bcol)
            self.drawThings()
        else:
            self.board.clearSelection()
            self.drawThings()
    def selectAll(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            self.board.selectAll(brow,bcol)
            self.drawThings()
        else:
            self.board.clearSelection()
            self.drawThings()
    def toggle(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            self.board.toggle(brow,bcol)
            self.drawThings()
    def addAll(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            self.board.addAll(brow,bcol)
            self.drawThings()
    def configure(self, event):
        if self.cells[0][0].winfo_height() == 1:
            self.update()
        self.cell_height=self.cells[0][0].winfo_height()
        self.cell_width=self.cells[0][0].winfo_width()
        self.drawThings()
    def outlineIfSelected(self, row,col):
        if self.select_ids[row][col] != None:
            self.cells[row][col].delete(self.select_ids[row][col])
            self.select_ids[row][col] = None
        if (row,col) in self.board.selected:
            self.select_ids[row][col] = self.cells[row][col].create_rectangle(0,0,self.cell_width,self.cell_height,outline='#FFFF33',width=10)
    def drawThings(self):
        font = tkFont.Font(size=2 * min(self.cell_height,self.cell_width) / 5)
        for row in range(self.height):
            for col in range(self.width):
                self.cells[row][col].delete(self.text_ids[row][col])
                self.cells[row][col].configure(bg = self.board.color(row, col))
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
                            self.photo((self.cell_width,self.cell_height))
                            self.tornado_width = self.cell_width
                            self.tornado_height = self.cell_height
                        self.text_ids[row][col] = self.cells[row][col].create_image(self.cell_width/2,self.cell_height/2,image=self.tornado_photoimage)
                    else:
                        text = str(self.board.cells[row][col])
                        self.text_ids[row][col] = self.cells[row][col].create_text(self.cell_width/2,self.cell_height/2,text=text, fill=color, font = font)
                    self.cells[row][col].grid(column = col, row = row)
       
#def reportEvent(event):
#    print 'keysym=%s, keysym_num=%s' % (event.keysym, event.keysym_num)
root = Application()
root.mainloop()
