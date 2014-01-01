import Tkinter as tk
import tkFont
import grid
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.createWidgets()
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
    def createWidgets(self):
        top = self.winfo_toplevel()
        self.length = 10
        self.width = 10
        self.cells = [[None for col in range(self.width)] for row in range(self.length)]
        self.textids = [[1 for col in range(self.width)] for row in range(self.length)]
        self.board = grid.Grid(self.length, self.width);
        self.cellheight = 50 
        self.cellwidth = 50 
        for col in range(self.width):
            top.columnconfigure(col, weight = 1)
            self.columnconfigure(col, weight = 1)
        for row in range(self.length):
            top.rowconfigure(row, weight = 1)
            self.rowconfigure(row, weight = 1)
        for row in range(self.length):
            for col in range(self.width):
                bg = '#000000'
                self.cells[row][col] = tk.Canvas(self, height = self.cellheight, width = self.cellwidth, bg = bg, bd = 0)
                self.cells[row][col].board_row = row
                self.cells[row][col].board_col = col
                # TODO <Configure> http://effbot.org/tkinterbook/tkinter-events-and-bindings.htm
                self.cells[row][col].bind('<Button-3>', self.kill)
                self.cells[row][col].grid(sticky = tk.N+tk.S+tk.E+tk.W, column = col, row = row)
        self.master.title("Intelligent Design")
        self.drawThings()
        self.nextButton = tk.Button(self, text = "Next", command = self.updateBoard)
        self.nextButton.grid(column = self.width, row = 0, sticky = tk.N)
    def updateBoard(self):
        self.board.step()
        self.drawThings()
    def kill(self, event):
        # FIXME inefficient
        for row in range(self.length):
            for col in range(self.width):
                if str(self.cells[row][col]) == str(event.widget):
                    brow = row
                    bcol = col
                    break
        self.board.kill(brow,bcol)
        self.drawThings()
    def drawThings(self):
        font = tkFont.Font(size=3 * self.cellheight / 5)
        for row in range(self.length):
            for col in range(self.width):
                self.cells[row][col].delete(self.textids[row][col])
                team = self.board.cells[row][col].team
                strength = self.board.cells[row][col].strength
                if team == "R":
                    color = '#FF0000'
                if team == "B":
                    color = '#0000FF'
                if team == grid.neutralstr:
                    color = '#e4e4e4'
                self.textids[row][col] = self.cells[row][col].create_text(25,25,text=str(strength), fill=color, font = font)
                self.cells[row][col].grid(column = col, row = row)
       
#def reportEvent(event):
#    print 'keysym=%s, keysym_num=%s' % (event.keysym, event.keysym_num)
root = Application()
root.mainloop()
