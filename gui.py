import Tkinter as tk
import tkFont
import board
import time
import ai
import cell
import random
import thread
import threading
import Queue
from PIL import Image
from PIL import ImageTk
class Application(tk.Frame):
    def runTODO(self):
        while self.eventq.qsize():
            func, args = self.eventq.get()
            func(*args)
        self.update()
        self.after(100,self.runTODO)
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
        ai.app = self
        self.images = dict()
        self.photos = dict()
        self.changePhoto((300,300),"assets/tornado.gif")
        self.info = ""
        # TODO reset back to "" on successful user actions
        self.createWidgets()
        self.board_width = sum([self.cells[i][i].winfo_width() for i in range(self.width)])
        self.grid(sticky=tk.N+tk.S+tk.E+tk.W)
        self.eventq = Queue.Queue()
        self.createAI()
        self.after(24,self.runTODO)
    def createAI(self):
        if self.mode.get() == self.vers_ai_str:
            self.ai = []
            self.ai_strat = [random.choice([cell.specializations[a], cell.specializations[a+1]]) for a in range(0,6,2)]
            self.ai.append(thread.start_new_thread(self.ai_levels[self.difficulty.get()], (self.board, self.ai_team, self.board.turn, self.ai_strat, [True])))
    def updateAI(self):
        if self.mode.get() == self.vers_ai_str:
            for i in range(len(self.ai)):
                self.ai[i] = thread.start_new_thread(self.ai_levels[self.difficulty.get()], (self.board, self.ai_team, self.board.turn, self.ai_strat, [True]))
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
        self.board = board.Board(self.height, self.width);
        self.player_team = self.board.teams[0]
        self.ai_team = self.board.teams[1]
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
        hotkeys = ['Q','E','A','D','Z','C']
        self.specialization_colors = ['#8F3E45', '#00FFFF', '#FA8072', '#B57EDC', '#2FE277', '#FFA500']
        self.specialization_buttons = []
        self.button_width = 9 # letters
        self.button_height = 1 # letters
        x = -1
        y = 0
        for option,color,hotkey in zip(cell.specializations, self.specialization_colors, hotkeys):
            x += 1
            if x > 1:
                x = 0
                y += 1
            self.specialization_buttons.append(tk.Button(self.specialization_menu, text = option + ' (' + hotkey + ')', command = getattr(self,'spec'+option), width = self.button_width, height = self.button_height, bg = color))
            self.specialization_buttons[-1].grid(column = x, row = y)
        self.next_button = tk.Button(self, text = "Next", command = self.stepBoard, width = self.button_width, height = self.button_height)
        self.next_button.grid(column = self.width, row = self.height - 3, columnspan = 2, sticky = tk.N)
        self.reset_button = tk.Button(self, text = "Reset", command = self.resetBoard, width = self.button_width, height = self.button_height)
        self.reset_button.grid(column = self.width, row = self.height - 2, columnspan = 2, sticky = tk.N)
        self.sparta_button = tk.Button(self, text = "300", command = self.step300, width = self.button_width, height = self.button_height)
        self.sparta_button.grid(column = self.width, row = self.height - 1, columnspan = 2, sticky = tk.N)
        self.settings_button = tk.Button(self, text = "Settings", command = self.settings, width = self.button_width, height = self.button_height)
        self.settings_button.grid(column = self.width + 2, row = self.height - 3, columnspan = 2, sticky = tk.N)
        self.buttons = [self.next_button, self.reset_button, self.sparta_button, self.settings_button]
        self.info_panel_span = 7
        self.info_panel = tk.Frame(self, width = self.cell_width * self.info_panel_span, height = self.cell_height * (self.height - len(self.buttons)))
        self.info_panel.grid(row = 0, column = self.width, rowspan = (self.height - len(self.buttons)), columnspan = self.info_panel_span)
        self.score_widgets = dict()
        self.last_score = dict()
        for team in self.board.teams:
            self.last_score[team] = -1
            self.score_widgets[team+"Points"] = tk.Label()
        self.panel_widgets = dict()
        for spec in cell.specializations:
            self.panel_widgets[spec+"Info"] = tk.Label(justify=tk.LEFT)
            self.panel_widgets[spec+"Pic"] = tk.Label()
        self.panel_widgets["Title"] = tk.Label()
        self.panel_widgets["Strength"] = tk.Label()
        self.panel_widgets["Land"] = tk.Label()
        self.panel_widgets["Volcano"] = tk.Button(self, text="Volcano", command = self.volcano, width = self.button_width, height = self.button_height, state=tk.DISABLED)
        for row in range(self.height):
            top.rowconfigure(row, weight = 1)
            self.rowconfigure(row, weight = 1)
        for col in range(self.width + self.info_panel_span):
            top.columnconfigure(col, weight = 1)
            self.columnconfigure(col, weight = 1)
        # settingsPanel
        # TODO reset doesn't apply changes to settings until confirm
        self.panel_widgets["Confirm"] = tk.Button(self, text="Confirm", command = self.resetBoard, width = self.button_width, height = self.button_height)
        # TODO cancel undoes changes to settings since opening panel
        self.panel_widgets["Cancel"] = tk.Button(self, text="Cancel", command = self.settings, width = self.button_width, height = self.button_height)
        self.include_tornado = tk.IntVar()
        self.panel_widgets["TornadoCheck"] = tk.Checkbutton(text="Tornado", variable=self.include_tornado)
        self.panel_widgets["TornadoCheck"].select()
        self.vers_ai_str = "Versus AI"
        self.testing_str = "Testing"
        self.mode = tk.StringVar()
        self.modes = (
            self.vers_ai_str,
            self.testing_str,
        )
        self.mode.set(self.modes[0])
        self.testing = self.mode.get() == self.testing_str
        self.ai_levels = {
            "Easy" : ai.easy,
            "Medium" : ai.medium
        }
        self.difficulty = tk.StringVar()
        self.difficulty.set("Medium")
        self.panel_widgets["Mode"] = tk.OptionMenu(self, self.mode, *self.modes, command=self.changeMode)
        self.panel_widgets["Difficulty"] = tk.OptionMenu(self, self.difficulty, *self.ai_levels)
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
    def stepBoard(self):
        with self.board.lock:
            if self.board.external():
                self.drawThings()
                self.update()
                time.sleep(0.3)
            self.board.internal()
            self.drawThings()
            self.updateAI()
    def resetBoard(self):
        self.testing = self.mode.get() == self.testing_str
        self.board.reset(self.include_tornado.get() > 0, testing = self.testing)
        self.createAI()
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
                ret = self.board.move((0,-1), self.player_team) 
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
                    r,c = iter(self.board.selected[self.player_team]).next()
                    if self.board.cells[r][c].team == self.player_team or self.testing:
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
        if type(ret) == type(""):
            self.info = ret
        elif type(ret) == type(set()):
            self.info = ""
            for r,c in ret:
                self.drawCell(r,c)
            self.drawScore()
    def kill(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            self.specialization_menu.place_info()
            brow,bcol = self.cell_locations[event.widget]
            changed = self.board.kill(brow,bcol,self.player_team)
            for row, col in changed:
                self.drawCell(row,col)
            self.clearPanel()
            self.drawScore()
    def volcano(self):
        changed = self.board.createVolcano(self.player_team)
        for row, col in changed:
            self.drawCell(row,col)
        self.drawPanel()
    def specialize(self,specialization):
        ret = self.board.specialize(specialization, self.player_team)
        if type(ret) == type(""):
            self.info = ret
        else:
            for r,c in ret:
                self.drawCell(r,c)
        self.specialization_menu.place_forget()
        self.drawPanel()
    def select(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cell_locations[event.widget]
            changed = self.board.select(brow,bcol,self.player_team)
            for row, col in changed:
                self.outlineIfSelected(row,col)
            self.clearPanel()
            self.drawScore()
            if len(self.board.selected[self.player_team]) == 1:
                self.drawSelectedInfo()
    def selectAll(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cell_locations[event.widget]
            self.board.selectAll(brow,bcol,self.player_team)
            self.drawThings()
    def toggle(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cell_locations[event.widget]
            self.board.toggle(brow,bcol,self.player_team)
            self.drawThings()
    def addAll(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cell_locations[event.widget]
            self.board.addAll(brow,bcol,self.player_team)
            self.drawThings()
    def configure(self, event):
        self.update() # set winfo stuff
        self.cell_height=self.cells[0][0].winfo_height()
        self.cell_width=self.cells[0][0].winfo_width()
        self.board_width = sum([self.cells[i][i].winfo_width() for i in range(self.width)])
        self.drawThings()
    def changeMode(self, mode):
        self.clearPanel()
        self.settings()
    def settings(self):
        if self.panel_widgets["TornadoCheck"].place_info():
            # if already exists
            self.clearPanel()
            self.drawPanel()
        else:
            self.clearPanel()
            self.settingsPanel()
            self.settings_button.configure(text="Hide")
    def outlineIfSelected(self, row,col):
        if self.select_ids[row][col] != None:
            self.cells[row][col].delete(self.select_ids[row][col])
            self.select_ids[row][col] = None
        if (row,col) in self.board.selected[self.player_team]:
            width = self.cells[row][col].winfo_width()
            height = self.cells[row][col].winfo_height()
            color = self.board.land[row][col].outlineColor()
            self.select_ids[row][col] = self.cells[row][col].create_rectangle(1,1,width-2,height-2,outline=color,width=1)
    def drawThings(self):
        with self.board.lock:
            self.cell_font = tkFont.Font(size=2 * min(self.cell_height,self.cell_width) / 5)
            for row in range(self.height):
                for col in range(self.width):
                    self.drawCell(row,col)
            self.drawPanel()
            if self.board_width > self.width:
                # avoid drawing score alone before board
                for index, team in enumerate(self.board.teams):
                    self.score_widgets[team+"Points"].configure(font = self.cell_font)
                    self.score_widgets[team+"Points"].place(x = self.board_width, y = self.info_panel.winfo_height() - index * self.cell_height * 4 / 5 + self.cell_height, anchor = tk.SW)
    def clearPanel(self):
        for widget in self.panel_widgets:
            self.panel_widgets[widget].place_forget()
    def drawScore(self):
         for index, team in enumerate(self.board.teams):
            points = self.board.points[team]
            if points is not self.last_score[team]:
                self.score_widgets[team+"Points"].configure(text = team + ": " + str(points))
                self.last_score[team] = points
    def drawSelectedInfo(self):
        # populate info_panel based on selection
        row,col = iter(self.board.selected[self.player_team]).next()
        img_height = self.cell_height * self.height / 8
        img_width = self.cell_width * self.info_panel_span / 4
        txt_width = (self.info_panel_span * self.cell_width - img_width) * 9 / 10
        img_size = min(img_width, img_height)
        self.desc_font = tkFont.Font(size = img_size / 10)
        self.panel_button_font = tkFont.Font(size = img_height / 8)
        if self.board.cells[row][col].isWarrior():
            self.changePhoto((img_size,img_size), "assets/sword.gif")
            self.panel_widgets["WarriorPic"].configure(image=self.photoimage, height = img_size, width = img_size)
            self.panel_widgets["WarriorPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = tk.CENTER)
            warrior_level = self.board.cells[row][col].warriorLevel()
            description = "Level " + str(warrior_level) + " Warrior"
            description += "\nGrants " + str(warrior_level) + " permanent bonus strength distributed among random allied neighbors."
            if warrior_level >= 2:
                description += "\nIncludes its own strength in combat survival."
            self.panel_widgets["WarriorInfo"].configure(text = description, font = self.desc_font, wraplength = txt_width)
            self.panel_widgets["WarriorInfo"].place(x=self.board_width + img_size, y=self.cell_height * self.height * 3 / 10, anchor = tk.W)
        elif self.board.cells[row][col].isMedic():
            self.changePhoto((img_size,img_size), "assets/bandage.gif")
            self.panel_widgets["MedicPic"].configure(image=self.photoimage, height = img_size, width = img_size)
            self.panel_widgets["MedicPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = tk.CENTER)
            medic_level = self.board.cells[row][col].medicLevel()
            description = "Level " + str(medic_level) + " Medic"
            approx_odds = 1 - .75 ** medic_level
            approx_odds *= 100
            approx_odds = int(round(approx_odds))
            description += "\n" + "Has " + str(approx_odds) + "% chance to save allied neighbors from combat."
            self.panel_widgets["MedicInfo"].configure(text = description, font = self.desc_font, wraplength = txt_width)
            self.panel_widgets["MedicInfo"].place(x=self.board_width + img_size, y=self.cell_height * self.height * 3 / 10, anchor = tk.W)
        if self.board.cells[row][col].isCleric():
            self.changePhoto((img_size,img_size), "assets/candle.gif")
            self.panel_widgets["ClericPic"].configure(image=self.photoimage, height = img_size, width = img_size)
            self.panel_widgets["ClericPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = tk.CENTER)
            cleric_level = self.board.cells[row][col].clericLevel()
            description = "Level " + str(cleric_level) + " Cleric"
            approx_odds = 1 - .9 ** cleric_level
            approx_odds *= 100
            approx_odds = int(round(approx_odds))
            description += "\nHas " + str(approx_odds) + "% chance to convert enemy neighboring cells."
            description += "\nCannot be converted by enemy Clerics."
            self.panel_widgets["ClericInfo"].configure(text = description, font = self.desc_font, wraplength = txt_width)
            self.panel_widgets["ClericInfo"].place(x=self.board_width + img_size, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = tk.W)
        elif self.board.cells[row][col].isScientist():
            self.changePhoto((img_size,img_size), "assets/testTube.gif")
            self.panel_widgets["ScientistPic"].configure(image=self.photoimage, height = img_size, width = img_size)
            self.panel_widgets["ScientistPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = tk.CENTER)
            scientist_level = self.board.cells[row][col].scientistLevel()
            description = "Level " + str(scientist_level) + " Scientist"
            description += "\nGrants " + str(scientist_level) + " points per turn."
            self.panel_widgets["ScientistInfo"].configure(text = description, font = self.desc_font, wraplength = txt_width)
            self.panel_widgets["ScientistInfo"].place(x=self.board_width + img_size, y=self.cell_height * self.height * 3 / 10 + img_size, anchor = tk.W)
        if self.board.cells[row][col].isFarmer():
            self.changePhoto((img_size,img_size), "assets/pitchfork.gif")
            self.panel_widgets["FarmerPic"].configure(image=self.photoimage, height = img_size, width = img_size)
            self.panel_widgets["FarmerPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = tk.CENTER)
            description = "Level " + str(self.board.cells[row][col].farmerLevel()) + " Farmer"
            description += "\nImproves adjacent land proportional to level."
            self.panel_widgets["FarmerInfo"].configure(text = description, font = self.desc_font, wraplength = txt_width)
            self.panel_widgets["FarmerInfo"].place(x=self.board_width + img_size, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = tk.W)
        elif self.board.cells[row][col].isHunter():
            self.changePhoto((img_size,img_size), "assets/bow.gif")
            self.panel_widgets["HunterPic"].configure(image=self.photoimage, height = img_size, width = img_size)
            self.panel_widgets["HunterPic"].place(x=self.board_width + img_size / 2, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = tk.CENTER)
            description = "Level " + str(self.board.cells[row][col].hunterLevel()) + " Hunter"
            description += "\nVastly improves land proportional to level when neighbors die."
            self.panel_widgets["HunterInfo"].configure(text = description, font = self.desc_font, wraplength = txt_width)
            self.panel_widgets["HunterInfo"].place(x=self.board_width + img_size, y=self.cell_height * self.height * 3 / 10 + img_size * 2, anchor = tk.W)
        can_volcano = self.board.points[self.player_team] >= board.volcano_cost
        if can_volcano:
            volc_button_state = tk.NORMAL
        else:
            volc_button_state = tk.DISABLED
        self.panel_widgets["Volcano"].configure(font=self.panel_button_font, state = volc_button_state)
        self.panel_widgets["Volcano"].place(x=self.board_width, y=self.info_panel.winfo_height() - (len(self.board.teams)-.5) * self.cell_height * 4 / 5, anchor=tk.W)
        self.team_font = tkFont.Font(size = img_size * 2/3) 
        self.panel_widgets["Title"].configure(text = self.board.cells[row][col].team, font = self.team_font)
        self.panel_widgets["Title"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = 0, anchor = tk.N)
        self.strength_font = tkFont.Font(size = img_size / 4)
        self.land_font = tkFont.Font(size = img_size / 6)
        self.panel_widgets["Land"].configure(text = "Land Quality: " + self.board.land[row][col].description(), font = self.land_font)
        if self.board.cells[row][col].team not in cell.neutral_teams:
            self.panel_widgets["Strength"].configure(text = "Strength: " + str(self.board.cells[row][col].strength), font = self.strength_font)
            self.panel_widgets["Strength"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = self.cell_height * 2, anchor = tk.CENTER)
            self.panel_widgets["Land"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = self.cell_height * 2.75, anchor = tk.CENTER)
        else:
            self.panel_widgets["Land"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = self.cell_height * 2, anchor = tk.CENTER)
    def settingsPanel(self):
        self.panel_widgets["TornadoCheck"].place(x=self.board_width + self.cell_width, y = self.cell_height / 2, anchor = tk.CENTER)
        self.panel_widgets["Mode"].place(x=self.board_width + self.cell_width, y = self.cell_height, anchor = tk.N)
        if self.mode.get() == self.vers_ai_str:
            self.panel_widgets["Difficulty"].place(x=self.board_width + self.cell_width * 3, y = self.cell_height, anchor = tk.N)
        self.panel_widgets["Confirm"].place(x = self.board_width + self.cell_width * self.info_panel_span / 3 * .95, y = self.info_panel.winfo_height(), anchor = tk.S)
        self.panel_widgets["Cancel"].place(x = self.board_width + self.cell_width * 2 * self.info_panel_span / 3 * .95, y = self.info_panel.winfo_height(), anchor = tk.S)
    def drawPanel(self):
        self.clearPanel()
        self.drawScore()
        if len(self.board.selected[self.player_team]) == 1:
            self.drawSelectedInfo()
        self.settings_button.configure(text="Settings")
    def drawCell(self, row, col):
        with self.board.lock:
            self.cells[row][col].delete(self.text_ids[row][col])
            for spec_id in self.spec_ids[row][col]:
                self.cells[row][col].delete(spec_id)
            self.spec_ids[row][col] = []
            if (row,col) in board.smoky_cells:
                self.cells[row][col].configure(bg = '#D3D3D3')
            elif (row,col) in board.lava_cells:
                self.cells[row][col].configure(bg = '#FF0000')
                board.lava_cells.remove((row,col))
            else:
                self.cells[row][col].configure(bg = self.board.color(row, col))
            team = self.board.cells[row][col].team
            strength = self.board.cells[row][col].strength
            if team == self.board.teams[0]:
                color = '#FF0000'
            elif team == self.board.teams[1]:
                color = '#0000FF'
            elif team in board.neutral_teams:
                color = '#e4e4e4'
            if team != board.neutral_str:
                if team == board.tornado_str:
                    self.changePhoto((self.cell_width,self.cell_height),"assets/tornado.gif")
                    self.text_ids[row][col] = self.cells[row][col].create_image(self.cell_width/2,self.cell_height/2,image=self.photoimage)
                else:
                    text = str(len(self.board.friendlyAdj(row,col)))
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
