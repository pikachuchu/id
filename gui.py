import Tkinter as tk
import tkFont
import grid
import time
from PIL import Image
from PIL import ImageTk
class Application(tk.Frame):
    def changePhoto(self,size,loc):
        # updates image and photo
        if (size,loc) in self.images:
            self.image = self.images[(size,loc)]
            self.photoimage = self.photos[(size,loc)]
        else:
            self.image = Image.open(loc)
            # TODO distort
            self.image.thumbnail(size, Image.ANTIALIAS)
            self.photoimage = ImageTk.PhotoImage(self.image)
            self.images[(size,loc)] = self.image
            self.photos[(size,loc)] = self.photoimage
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        self.images = dict()
        self.photos = dict()
        self.changePhoto((300,300),"assets/tornado.gif")
        self.info = ""
        # TODO reset back to "" on successful user actions
        self.createWidgets()
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
    def createWidgets(self):
        top = self.winfo_toplevel()
        self.height = 15
        self.width = 15
        self.cells = [[None for col in range(self.width)] for row in range(self.height)]
        self.cell_locations = dict()
        self.text_ids = [[1 for col in range(self.width)] for row in range(self.height)]
        def empty():
            return []
        self.spec_ids = [[empty() for col in range(self.width)] for row in range(self.height)]
        self.select_ids = [[None for col in range(self.width)] for row in range(self.height)]
        # TODO team prompt
        self.board = grid.Grid(self.height, self.width);
        self.player_team = self.board.teams[0]
        self.cell_height = 50
        self.cell_width = 50
        self.master.bind('<Key>', self.key)
        self.bind('<Configure>', self.configure)
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
        self.specialization_menu = tk.LabelFrame(self, text='Specialize', bg = '#000000', fg = '#FFFFFF')
        self.specializations = ['Warrior','Medic','Cleric','Scientist','Farmer','Hunter']
        hotkeys = ['Q','E','A','D','Z','C']
        self.specialization_colors = ['#8F3E45', '#00FFFF', '#FA8072', '#B57EDC', '#2FE277', '#FFA500']
        self.specialization_buttons = []
        self.button_width = 9 # letters
        self.button_height = 1 # letters
        x = -1
        y = 0
        for option,color,hotkey in zip(self.specializations, self.specialization_colors, hotkeys):
            x += 1
            if x > 1:
                x = 0
                y += 1
            self.specialization_buttons.append(tk.Button(self.specialization_menu, text = option + ' (' + hotkey + ')', command = getattr(self,'spec'+option), width = self.button_width, height = self.button_height, bg = color))
            self.specialization_buttons[-1].grid(column = x, row = y)
        self.next_button = tk.Button(self, text = "Next", command = self.updateBoard, width = self.button_width, height = self.button_height)
        self.next_button.grid(column = self.width, row = self.height - 3, columnspan = 2, sticky = tk.N)
        self.reset_button = tk.Button(self, text = "Reset", command = self.resetBoard, width = self.button_width, height = self.button_height)
        self.reset_button.grid(column = self.width, row = self.height - 2, columnspan = 2, sticky = tk.N)
        self.sparta_button = tk.Button(self, text = "300", command = self.step300, width = self.button_width, height = self.button_height)
        self.sparta_button.grid(column = self.width, row = self.height - 1, columnspan = 2, sticky = tk.N)
        self.buttons = [self.next_button, self.reset_button, self.sparta_button]
        self.info_panel_span = 5
        self.info_panel = tk.Frame(self, width = self.cell_width * self.info_panel_span, height = self.cell_height * (self.height - len(self.buttons)))
        self.info_panel.grid(row = 0, column = self.width, rowspan = (self.height - len(self.buttons)), columnspan = self.info_panel_span)
        self.panel_widgets = dict()
        for team in self.board.teams:
            self.panel_widgets[team+"Points"] = tk.Label()
        for spec in self.specializations:
            self.panel_widgets[spec+"Info"] = tk.Label()
            self.panel_widgets[spec+"Pic"] = tk.Label()
        self.panel_widgets["Title"] = tk.Label()
        self.panel_widgets["Strength"] = tk.Label()
        for row in range(self.height):
            top.rowconfigure(row, weight = 1)
            self.rowconfigure(row, weight = 1)
        for col in range(self.width + self.info_panel_span):
            top.columnconfigure(col, weight = 1)
            self.columnconfigure(col, weight = 1)
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
        ret = None
        if event.char == 'q':
            if self.specialization_menu.place_info():
                self.specWarrior()
            else:
                ret = self.board.move((-1,-1), self.player_team)
        elif event.char == 'w':
            if self.specialization_menu.place_info():
                pass
            else:
                ret = self.board.move((-1,0), self.player_team)
        elif event.char == 'e':
            if self.specialization_menu.place_info():
                self.specMedic()
            else:
                ret = self.board.move((-1,1), self.player_team)
        elif event.char == 'a':
            if self.specialization_menu.place_info():
                self.specCleric()
            else:
                self.board.move((0,-1), self.player_team) 
        elif event.char == 'd':
            if self.specialization_menu.place_info():
                self.specScientist()
            else:
                ret = self.board.move((0,1), self.player_team) 
        elif event.char == 'z':
            if self.specialization_menu.place_info():
                self.specFarmer()
            else:
                ret = self.board.move((1,-1), self.player_team) 
        elif event.char == 'x':
            if self.specialization_menu.place_info():
                pass
            else:
                ret = self.board.move((1,0), self.player_team)
        elif event.char == 'c':
            if self.specialization_menu.place_info():
                self.specHunter()
            else:
                ret = self.board.move((1,1), self.player_team)
        elif event.char == 's':
            if self.specialization_menu.place_info():
                # if exists
                self.specialization_menu.place_forget()
            else:
                if self.board.selected[self.player_team]:
                    top = self.winfo_toplevel()
                    if self.specialization_menu.winfo_width() == 1:
                        # only once
                        self.specialization_menu.place(x=event.x, y=event.y,anchor='center')
                        self.update()
                    x = max(event.x, self.specialization_menu.winfo_width() / 2)
                    x = min(x, top.winfo_width() - self.specialization_menu.winfo_width() / 2)
                    x = min(x, self.board_width - self.specialization_menu.winfo_width() / 2)
                    y = max(event.y, self.specialization_menu.winfo_height() / 2)
                    y = min(y, top.winfo_height() - self.specialization_menu.winfo_height() / 2)
                    board_height = sum([self.cells[i][0].winfo_height() for i in range(self.height)])
                    y = min(y, board_height - self.specialization_menu.winfo_height() / 2)
                    self.specialization_menu.place(x=x, y=y,anchor='center')
                else:
                    return
        if ret != None:
            self.info = ret
        else:
            self.info = ""
        self.drawThings()
    def kill(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.kill(brow,bcol,self.player_team):
            self.drawThings()
    def specialize(self,specialization):
        ret = self.board.specialize(specialization, self.player_team)
        if ret != None:
            self.info = ret
        self.specialization_menu.place_forget()
        self.drawThings()
    def select(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            if self.player_team == self.board.cells[brow][bcol].team:
                self.board.select(brow,bcol,self.player_team)
                self.drawThings()
        else:
            self.board.clearSelection(self.player_team)
            self.drawThings()
    def selectAll(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.board.cells[brow][bcol].team not in grid.neutral_teams:
            if self.player_team == self.board.cells[brow][bcol].team:
                self.board.selectAll(brow,bcol,self.player_team)
                self.drawThings()
        else:
            self.board.clearSelection(self.player_team)
            self.drawThings()
    def toggle(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.player_team == self.board.cells[brow][bcol].team:
            self.board.toggle(brow,bcol,self.player_team)
            self.drawThings()
    def addAll(self, event):
        brow,bcol = self.cell_locations[event.widget]
        if self.player_team == self.board.cells[brow][bcol].team:
            self.board.addAll(brow,bcol,self.player_team)
            self.drawThings()
    def configure(self, event):
        self.update() # set winfo stuff
        self.cell_height=self.cells[0][0].winfo_height()
        self.cell_width=self.cells[0][0].winfo_width()
        self.drawThings()
    def outlineIfSelected(self, row,col):
        if self.select_ids[row][col] != None:
            self.cells[row][col].delete(self.select_ids[row][col])
            self.select_ids[row][col] = None
        if (row,col) in self.board.selected[self.player_team]:
            width = self.cells[row][col].winfo_width()
            height = self.cells[row][col].winfo_height()
            self.select_ids[row][col] = self.cells[row][col].create_rectangle(1,1,width-2,height-2,outline='#000000',width=1)
    def drawThings(self):
        self.cell_font = tkFont.Font(size=2 * min(self.cell_height,self.cell_width) / 5)
        for row in range(self.height):
            for col in range(self.width):
                self.drawCell(row,col)
        for widget in self.panel_widgets:
            self.panel_widgets[widget].place_forget()
        self.board_width = sum([self.cells[i][i].winfo_width() for i in range(self.width)])
        for index, (team, points) in enumerate(self.board.points.items()):
            if team not in grid.neutral_teams:
                self.panel_widgets[team+"Points"].configure(text = team + ": " + str(points), font = self.cell_font)
                self.panel_widgets[team+"Points"].place(x = self.board_width, y = self.info_panel.winfo_height() * 9 / 10 - index * self.cell_height * 4 / 5, anchor = tk.NW)
        # populate info_panel based on selection
        if len(self.board.selected[self.player_team]) == 1:
            row,col = list(self.board.selected[self.player_team])[0]
            cell = self.board.cells[row][col]
            img_height = self.cell_height * self.height / 5
            img_width = self.cell_width * self.info_panel_span / 3
            img_size = min(img_width, img_height)
            self.desc_font = tkFont.Font(size = img_size / 8)
            if self.board.cells[row][col].isWarrior():
                self.changePhoto((img_size,img_size), "assets/sword.gif")
                self.panel_widgets["WarriorPic"].configure(image=self.photoimage, height = img_size, width = img_size)
                self.panel_widgets["WarriorPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = "center")
                description = "Level: " + str(self.board.cells[row][col].warriorLevel())
                self.panel_widgets["WarriorInfo"].configure(text = description, font = self.desc_font)
                self.panel_widgets["WarriorInfo"].place(x=self.board_width + 3 * img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = "center")
            elif self.board.cells[row][col].isMedic():
                self.changePhoto((img_size,img_size), "assets/bandage.gif")
                self.panel_widgets["MedicPic"].configure(image=self.photoimage, height = img_size, width = img_size)
                self.panel_widgets["MedicPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = "center")
                description = "Level: " + str(self.board.cells[row][col].medicLevel())
                self.panel_widgets["MedicInfo"].configure(text = description, font = self.desc_font)
                self.panel_widgets["MedicInfo"].place(x=self.board_width + 3 * img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = "center")
            if self.board.cells[row][col].isCleric():
                self.changePhoto((img_size,img_size), "assets/candle.gif")
                self.panel_widgets["ClericPic"].configure(image=self.photoimage, height = img_size, width = img_size)
                self.panel_widgets["ClericPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = "center")
                description = "Level: " + str(self.board.cells[row][col].clericLevel())
                self.panel_widgets["ClericInfo"].configure(text = description, font = self.desc_font)
                self.panel_widgets["ClericInfo"].place(x=self.board_width + 3 * img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = "center")
            elif self.board.cells[row][col].isScientist():
                self.changePhoto((img_size,img_size), "assets/testTube.gif")
                self.panel_widgets["ScientistPic"].configure(image=self.photoimage, height = img_size, width = img_size)
                self.panel_widgets["ScientistPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = "center")
                description = "Level: " + str(self.board.cells[row][col].scientistLevel())
                self.panel_widgets["ScientistInfo"].configure(text = description, font = self.desc_font)
                self.panel_widgets["ScientistInfo"].place(x=self.board_width + 3 * img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = "center")
            if self.board.cells[row][col].isFarmer():
                self.changePhoto((img_size,img_size), "assets/pitchfork.gif")
                self.panel_widgets["FarmerPic"].configure(image=self.photoimage, height = img_size, width = img_size)
                self.panel_widgets["FarmerPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = "center")
                description = "Level: " + str(self.board.cells[row][col].farmerLevel())
                self.panel_widgets["FarmerInfo"].configure(text = description, font = self.desc_font)
                self.panel_widgets["FarmerInfo"].place(x=self.board_width + 3 * img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = "center")
            elif self.board.cells[row][col].isHunter():
                self.changePhoto((img_size,img_size), "assets/bow.gif")
                self.panel_widgets["HunterPic"].configure(image=self.photoimage, height = img_size, width = img_size)
                self.panel_widgets["HunterPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = "center")
                description = "Level: " + str(self.board.cells[row][col].hunterLevel())
                self.panel_widgets["HunterInfo"].configure(text = description, font = self.desc_font)
                self.panel_widgets["HunterInfo"].place(x=self.board_width + 3 * img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = "center")
            self.team_font = tkFont.Font(size = img_size / 2) 
            self.panel_widgets["Title"].configure(text = self.board.cells[row][col].team, font = self.team_font)
            self.panel_widgets["Title"].place(x=self.board_width + self.cell_width * 2.4, y = self.cell_height, anchor = "center")
            self.strength_font = tkFont.Font(size = img_size / 4)
            self.panel_widgets["Strength"].configure(text = "Strength: " + str(self.board.cells[row][col].strength), font = self.strength_font)
            self.panel_widgets["Strength"].place(x=self.board_width + self.cell_width * 2.4, y = self.cell_height * 2, anchor = "center")
    def drawCell(self, row, col):
        self.cells[row][col].delete(self.text_ids[row][col])
        for spec_id in self.spec_ids[row][col]:
            self.cells[row][col].delete(spec_id)
        self.spec_ids[row][col] = []
        self.cells[row][col].configure(bg = self.board.color(row, col))
        team = self.board.cells[row][col].team
        strength = self.board.cells[row][col].strength
        if team == self.board.teams[0]:
            color = '#FF0000'
        elif team == self.board.teams[1]:
            color = '#0000FF'
        elif team in grid.neutral_teams:
            color = '#e4e4e4'
        if team != grid.neutral_str:
            if team == grid.tornado_str:
                self.changePhoto((self.cell_width,self.cell_height),"assets/tornado.gif")
                self.text_ids[row][col] = self.cells[row][col].create_image(self.cell_width/2,self.cell_height/2,image=self.photoimage)
            else:
                text = self.board.cells[row][col].strength
                self.text_ids[row][col] = self.cells[row][col].create_text(self.cell_width/2,self.cell_height/2,text=text, fill=color, font = self.cell_font)
                if self.board.cells[row][col].isWarrior():
                    self.changePhoto((self.cell_width/3,self.cell_height/3), "assets/sword.gif")
                    self.spec_ids[row][col].append(self.cells[row][col].create_image(self.cell_width/6,self.cell_height/6,image=self.photoimage))
                elif self.board.cells[row][col].isMedic():
                    self.changePhoto((self.cell_width/3,self.cell_height/3), "assets/bandage.gif")
                    self.spec_ids[row][col].append(self.cells[row][col].create_image(5*self.cell_width/6,self.cell_height/6,image=self.photoimage))
                if self.board.cells[row][col].isCleric():
                    self.changePhoto((self.cell_width/3,self.cell_height/3), "assets/candle.gif")
                    self.spec_ids[row][col].append(self.cells[row][col].create_image(self.cell_width/6,self.cell_height / 3 + self.cell_height / 6,image=self.photoimage))
                elif self.board.cells[row][col].isScientist():
                    self.changePhoto((self.cell_width/3,self.cell_height/3), "assets/testTube.gif")
                    self.spec_ids[row][col].append(self.cells[row][col].create_image(5*self.cell_width/6,self.cell_height / 3 + self.cell_height / 6,image=self.photoimage))
                if self.board.cells[row][col].isFarmer():
                    self.changePhoto((self.cell_width/3,self.cell_height - 2 * self.cell_height/3), "assets/pitchfork.gif")
                    self.spec_ids[row][col].append(self.cells[row][col].create_image(self.cell_width/6,self.cell_height - (self.cell_height - 2 * self.cell_height/3) / 2,image=self.photoimage))
                elif self.board.cells[row][col].isHunter():
                    self.changePhoto((self.cell_width/3,self.cell_height - 2 * self.cell_height/3), "assets/bow.gif")
                    self.spec_ids[row][col].append(self.cells[row][col].create_image(5*self.cell_width/6,self.cell_height - (self.cell_height - 2 * self.cell_height/3) / 2,image=self.photoimage))
            self.cells[row][col].grid(column = col, row = row)
        self.outlineIfSelected(row,col)

       
#def reportEvent(event):
#    print 'keysym=%s, keysym_num=%s' % (event.keysym, event.keysym_num)
root = Application()
root.mainloop()
