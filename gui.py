import Tkinter as tk
import tkFont
import grid
class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.grid()
        self.createWidgets()
    def createWidgets(self):
        self.length = 10
        self.width = 10
        self.cells = [[None for col in range(self.width)] for row in range(self.length)]
        self.textids = [[1 for col in range(self.width)] for row in range(self.length)]
        self.board = grid.Grid(self.length, self.width);
        for row in range(self.length):
            for col in range(self.width):
                bg = '#000000'
                self.cells[row][col] = tk.Canvas(self, height = 50, width = 50, bg = bg, bd = 0)
                self.cells[row][col].grid(column = col, row = row)
        self.master.title("Intelligent Design")
        self.drawThings()
        self.nextButton = tk.Button(self, text = "Next", command = self.updateBoard)
        self.nextButton.grid(column = self.width, row = 0, sticky = tk.N)
    def updateBoard(self):
        self.board.step()
        self.drawThings()
    def drawThings(self):
        font = tkFont.Font(size=30)
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
