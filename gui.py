import Tkinter as tk
import tkFont
import board
import time
import ai
import cell
import Queue
import random
import sys
import thread
import threading
from PIL import Image
from PIL import ImageTk
class Application(tk.Frame):
    def runTODO(self):
        while self.eventq.qsize():
            func, args = self.eventq.get()
            if func == self.drawThings:
                try:
                    while True:
                        func2, arg2 = self.eventq.get_nowait()
                        if func2 == func:
                            func,args = func2, arg2
                        else:
                            func(*args)
                            func,args = func2, arg2
                            break
                except Queue.Empty:
                    pass
            func(*args)
        self.update()
        self.after(100,self.runTODO)
    def changePhoto(self,size,loc):
        # updates image and photo
        if (size,loc) in self.images:
            self.image = self.images[(size,loc)]
            self.photoimage = self.photos[(size,loc)]
        else:
            for dim in size:
                if dim <= 0:
                    return False
            self.image = Image.open(loc)
            # TODO distort
            self.image.thumbnail(size, Image.ANTIALIAS)
            self.photoimage = ImageTk.PhotoImage(self.image)
            self.images[(size,loc)] = self.image
            self.photos[(size,loc)] = self.photoimage
        return True 
    def __init__(self, master=None):
        tk.Frame.__init__(self,master)
        ai.app = self
        self.images = dict()
        self.photos = dict()
        self.doFlash = False
        self.changePhoto((300,300),"assets/tornado.gif")
        self.info = ""
        # TODO reset back to "" on successful user actions
        self.createWidgets()
        #self.board_width = sum([self.cells[i][i].winfo_width() for i in range(self.width)])
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
        self.cell_height = 52
        self.cell_width = 52
        self.board_width = self.cell_width * self.width
        self.board_height = self.cell_height * self.height
        self.cells = tk.Canvas(self, height = self.board_height, width = self.board_width, bg = '#FFFFFF', bd=0)
        self.rect_ids = [[-1 for col in range(self.width)] for row in range(self.height)]
        self.text_ids = [[-1 for col in range(self.width)] for row in range(self.height)]
        def empty():
            return []
        self.spec_ids = [[empty() for col in range(self.width)] for row in range(self.height)]
        # TODO team prompt
        self.board = board.Board(self.height, self.width);
        self.player_team = self.board.teams[0]
        self.ai_team = self.board.teams[1]
        self.master.bind('<Key>', self.key)
        self.bind('<Configure>', self.configure)
        for row in range(self.height):
            for col in range(self.width):
                self.rect_ids[row][col] = self.cells.create_rectangle(col * self.cell_width + 1, row * self.cell_height + 1, (col + 1) * self.cell_width - 2, (row + 1) * self.cell_height - 2, width = 1)
        if sys.platform == 'darwin':
            self.cells.bind('<Button-2>', self.kill)
        else:
            self.cells.bind('<Button-3>', self.kill)
        self.cells.bind('<Button-1>', self.select)
        self.cells.bind('<Shift-Button-1>', self.selectAll)
        self.cells.bind('<Double-Button-1>', self.selectAll)
        self.cells.bind('<Control-Button-1>', self.toggle)
        self.cells.bind('<Control-Double-Button-1>', self.addAll)
        self.cells.bind('<Control-Shift-Button-1>', self.addAll)
        self.cells.grid(sticky = tk.W, column = 0, row = 0, columnspan = self.width, rowspan = self.height)
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
        self.panel_widgets["Tornado"] = tk.Button(self, text="Tornado", command = self.tornado, width = self.button_width, height = self.button_height, state=tk.DISABLED)
        for row in range(self.height):
            top.rowconfigure(row, weight = 1)
            self.rowconfigure(row, weight = 1)
        for col in range(self.width + self.info_panel_span):
            top.columnconfigure(col, weight = 1)
            self.columnconfigure(col, weight = 1)
        self.panel_widgets["AddLeft"] = tk.Button(self, command = self.addLeft)
        self.panel_widgets["AddRight"] = tk.Button(self, command = self.addRight)
        self.win_width = self.info_panel_span + self.width
        # settingsPanel
        self.settings_vars = []
        # TODO reset doesn't apply changes to settings until confirm
        self.panel_widgets["Confirm"] = tk.Button(self, text="Confirm", command = self.confirm, width = self.button_width, height = self.button_height)
        # TODO cancel undoes changes to settings since opening panel
        self.panel_widgets["Cancel"] = tk.Button(self, text="Cancel", command = self.cancel, width = self.button_width, height = self.button_height)
        self.include_tornado = tk.IntVar()
        self.settings_vars.append(self.include_tornado)
        self.panel_widgets["TornadoCheck"] = tk.Checkbutton(text="Tornado", variable=self.include_tornado)
        self.panel_widgets["TornadoCheck"].select()
        self.vers_ai_str = "Versus AI"
        self.testing_str = "Testing"
        self.mode = tk.StringVar()
        self.settings_vars.append(self.mode)
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
        self.settings_vars.append(self.difficulty)
        self.difficulty.set("Medium")
        self.panel_widgets["Mode"] = tk.OptionMenu(self, self.mode, *self.modes, command=self.changeMode)
        self.panel_widgets["Difficulty"] = tk.OptionMenu(self, self.difficulty, *self.ai_levels)
        self.updateSettingsVals()
        self.configure(update=False)
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
            self.endFlash()
            if self.board.external():
                self.drawThings()
                self.update()
                self.after(300,self.endStep)
            else:
                self.endStep()
    def endStep(self):
        if self.board.warning_cells:
            self.startFlash()
        self.board.internal()
        self.drawThings()
        self.updateAI()
    def resetBoard(self):
        self.undoSettingsVals()
        self.testing = self.mode.get() == self.testing_str
        self.board.reset(self.include_tornado.get() > 0, testing = self.testing)
        self.endFlash()
        self.createAI()
        self.drawThings()
    def step300(self):
        self.endFlash()
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
                    if self.board.cells[r][c].team == self.player_team or self.testing and self.board.cells[r][c].team not in cell.neutral_teams:
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
                        y = min(y, self.board_height - self.specialization_menu.winfo_height() / 2)
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
    def cellOf(self, x,y):
        # return the (row,col) of this x,y
        return (y / self.cell_height, x / self.cell_width)
    def kill(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            self.specialization_menu.place_info()
            brow,bcol = self.cellOf(event.x,event.y)
            changed = self.board.kill(brow,bcol,self.player_team)
            for row, col in changed:
                self.drawCell(row,col)
            self.clearPanel()
    def addLeft(self):
        self.add(self.player_team)
    def addRight(self):
        self.add(self.ai_team)
    def add(self, team):
        changed = self.board.addCell(self.player_team, team)
        if type(changed) == type(set()):
            for row,col in changed:
                self.drawCell(row,col)
            self.drawPanel()
    def tornado(self):
        changed = self.board.createTornado(self.player_team)
        for row, col in changed:
            self.drawCell(row,col)
        self.drawScore()
        self.drawPanel()
    def volcano(self):
        changed = self.board.createVolcano(self.player_team)
        if self.doFlash == False:
            self.startFlash()
        for row, col in changed:
            self.drawCell(row,col)
        self.drawScore()
        self.drawPanel()
    def specialize(self,specialization):
        ret = self.board.specialize(specialization, self.player_team)
        if type(ret) == type(""):
            self.info = ret
        else:
            for r,c in ret:
                self.drawCell(r,c)
        self.specialization_menu.place_forget()
        self.drawScore()
        self.drawPanel()
    def select(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cellOf(event.x,event.y)
            changed = self.board.select(brow,bcol,self.player_team)
            for row, col in changed:
                self.outlineIfSelected(row,col)
            self.clearPanel()
            if len(self.board.selected[self.player_team]) == 1:
                self.drawSelectedInfo()
    def selectAll(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cellOf(event.x,event.y)
            self.board.selectAll(brow,bcol,self.player_team)
            self.drawThings()
    def toggle(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cellOf(event.x, event.y)
            self.board.toggle(brow,bcol,self.player_team)
            self.drawThings()
    def addAll(self, event):
        if self.specialization_menu.place_info():
            # if exists
            self.specialization_menu.place_forget()
        else:
            brow,bcol = self.cellOf(event.x, event.y)
            self.board.addAll(brow,bcol,self.player_team)
            self.drawThings()
    def configure(self, event=None, update=True):
        # TODO
        if update:
            self.update() # set winfo stuff
        if event:
            old_width = self.cell_width
            old_height = self.cell_height
            self.board_width = self.cells.winfo_width()
            self.cell_width = self.board_width / self.width
            self.board_height = self.cells.winfo_height()
            self.cell_height = self.board_height / self.height
            for row in range(self.height):
                for col in range(self.width):
                    self.cells.delete(self.rect_ids[row][col])
                    self.rect_ids[row][col] = self.cells.create_rectangle(col * self.cell_width + 1, row * self.cell_height + 1, (col + 1) * self.cell_width - 2, (row + 1) * self.cell_height - 2, width = 1)
        self.img_height = self.cell_height * self.height / 8
        self.img_width = self.cell_width * self.info_panel_span / 4
        self.txt_width = (self.info_panel_span * self.cell_width - self.img_width) * 9 / 10
        self.img_size = min(self.img_width, self.img_height)
        self.desc_font = tkFont.Font(size = self.img_size / 10)
        self.team_font = tkFont.Font(size = self.img_size * 2/3) 
        self.panel_button_font = tkFont.Font(size = self.img_height / 8)
        self.strength_font = tkFont.Font(size = self.img_size / 4)
        self.land_font = tkFont.Font(size = self.img_size / 6)
        self.cell_font = tkFont.Font(size=2 * min(self.cell_height,self.cell_width) / 5)
        self.panel_widgets["Volcano"].configure(font=self.panel_button_font)
        self.panel_widgets["Tornado"].configure(font=self.panel_button_font)
        self.panel_widgets["Land"].configure(font = self.land_font)
        self.panel_widgets["Title"].configure(font = self.team_font)
        self.panel_widgets["Strength"].configure(font = self.strength_font)
        if self.board_width > self.width:
            # avoid drawing score alone before board
            for index, team in enumerate(self.board.teams):
                self.score_widgets[team+"Points"].configure(font = self.land_font)
                self.score_widgets[team+"Points"].place(x = self.board_width, y = self.info_panel.winfo_height() - (index + 1) * self.cell_height * 3 / 5 + self.cell_height, anchor = tk.SW)
        # Pictures and info
        if self.changePhoto((self.img_size,self.img_size), "assets/sword.gif"):
            self.panel_widgets["WarriorPic"].configure(image=self.photoimage, height = self.img_size, width = self.img_size)
        self.panel_widgets["WarriorInfo"].configure(font = self.desc_font, wraplength = self.txt_width)
        if self.changePhoto((self.img_size,self.img_size), "assets/bandage.gif"):
            self.panel_widgets["MedicPic"].configure(image=self.photoimage, height = self.img_size, width = self.img_size)
        self.panel_widgets["MedicInfo"].configure(font = self.desc_font, wraplength = self.txt_width)
        if self.changePhoto((self.img_size,self.img_size), "assets/candle.gif"):
            self.panel_widgets["ClericPic"].configure(image=self.photoimage, height = self.img_size, width = self.img_size)
        self.panel_widgets["ClericInfo"].configure(font = self.desc_font, wraplength = self.txt_width)
        if self.changePhoto((self.img_size,self.img_size), "assets/testTube.gif"):
            self.panel_widgets["ScientistPic"].configure(image=self.photoimage, height = self.img_size, width = self.img_size)
        self.panel_widgets["ScientistInfo"].configure(font = self.desc_font, wraplength = self.txt_width)
        if self.changePhoto((self.img_size,self.img_size), "assets/pitchfork.gif"):
            self.panel_widgets["FarmerPic"].configure(image=self.photoimage, height = self.img_size, width = self.img_size)
        self.panel_widgets["FarmerInfo"].configure(font = self.desc_font, wraplength = self.txt_width)
        if self.changePhoto((self.img_size,self.img_size), "assets/bow.gif"):
            self.panel_widgets["HunterPic"].configure(image=self.photoimage, height = self.img_size, width = self.img_size)
        self.panel_widgets["HunterInfo"].configure(font = self.desc_font, wraplength = self.txt_width)
        self.drawThings()
    def changeMode(self, mode):
        self.clearPanel()
        self.settings()
    def updateSettingsVals(self):
        self.settings_vals = []
        for var in self.settings_vars:
            self.settings_vals.append((var, var.get()))
    def undoSettingsVals(self):
        for (var, val) in self.settings_vals:
            var.set(val)
    def settings(self):
        if self.panel_widgets["TornadoCheck"].place_info():
            # if already exists
            self.drawPanel()
        else:
            self.clearPanel()
            self.settingsPanel()
            self.settings_button.configure(text="Hide")
    def confirm(self):
        self.updateSettingsVals()
        self.resetBoard()
        pass
    def cancel(self):
        self.undoSettingsVals()
        self.settings()
        pass
    def startFlash(self):
        self.doFlash = True
        self.flash()
    def endFlash(self):
        self.doFlash = False
    def flash(self):
        if self.doFlash:
            row, col = self.board.warning_cells.keys()[0]
            if self.cells.itemcget(self.rect_ids[row][col],"fill") == self.board.color(row,col):
                for (r,c), color in self.board.warning_cells.iteritems():
                    self.cells.itemconfigure(self.rect_ids[r][c],fill = color)
            else:
                for r,c in self.board.warning_cells.iterkeys():
                    self.cells.itemconfigure(self.rect_ids[r][c],fill = self.board.color(r,c))
            self.after(300, self.flash)
    def outlineIfSelected(self, row,col):
        if (row,col) in self.board.selected[self.player_team]:
            color = self.board.land[row][col].outlineColor()
            self.cells.itemconfigure(self.rect_ids[row][col], outline=color)
        else:
            self.cells.itemconfigure(self.rect_ids[row][col],outline='#FFFFFF')
    def drawThings(self):
        with self.board.lock:
            self.drawCells();
            self.drawScore()
            self.drawPanel()
    def clearPanel(self):
        for widget in self.panel_widgets:
            if self.panel_widgets[widget].place_info():
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
        if self.board.cells[row][col].isWarrior():
            self.panel_widgets["WarriorPic"].place(x=self.board_width + self.img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = tk.CENTER)
            warrior_level = self.board.cells[row][col].warriorLevel()
            description = "Level " + str(warrior_level) + " Warrior"
            description += "\nGrants " + str(warrior_level) + " permanent bonus strength distributed among random allied neighbors."
            if warrior_level >= 2:
                description += "\nIncludes its own strength in combat survival."
            self.panel_widgets["WarriorInfo"].configure(text = description)
            self.panel_widgets["WarriorInfo"].place(x=self.board_width + self.img_size, y=self.cell_height * self.height * 3 / 10, anchor = tk.W)
        elif self.board.cells[row][col].isMedic():
            self.panel_widgets["MedicPic"].place(x=self.board_width + self.img_size / 2, y=self.cell_height * self.height * 3 / 10, anchor = tk.CENTER)
            medic_level = self.board.cells[row][col].medicLevel()
            description = "Level " + str(medic_level) + " Medic"
            approx_odds = 1 - .75 ** medic_level
            approx_odds *= 100
            approx_odds = int(round(approx_odds))
            description += "\n" + "Has " + str(approx_odds) + "% chance to save allied neighbors from combat."
            self.panel_widgets["MedicInfo"].configure(text = description)
            self.panel_widgets["MedicInfo"].place(x=self.board_width + self.img_size, y=self.cell_height * self.height * 3 / 10, anchor = tk.W)
        if self.board.cells[row][col].isCleric():
            self.panel_widgets["ClericPic"].place(x=self.board_width + self.img_size / 2, y=self.cell_height * self.height * 3 / 10 + self.img_size, anchor = tk.CENTER)
            cleric_level = self.board.cells[row][col].clericLevel()
            description = "Level " + str(cleric_level) + " Cleric"
            approx_odds = 1 - .9 ** cleric_level
            approx_odds *= 100
            approx_odds = int(round(approx_odds))
            description += "\nSteals a point from the enemy for every enemy in a " + str(cleric_level) + "-cell radius."
            description += "\nHas " + str(approx_odds) + "% chance to convert enemy neighboring cells."
            description += "\nCannot be converted by enemy Clerics."
            self.panel_widgets["ClericInfo"].configure(text = description)
            self.panel_widgets["ClericInfo"].place(x=self.board_width + self.img_size, y=self.cell_height * self.height * 3 / 10 + self.img_size, anchor = tk.W)
        elif self.board.cells[row][col].isScientist():
            self.panel_widgets["ScientistPic"].place(x=self.board_width + self.img_size / 2, y=self.cell_height * self.height * 3 / 10 + self.img_size, anchor = tk.CENTER)
            scientist_level = self.board.cells[row][col].scientistLevel()
            description = "Level " + str(scientist_level) + " Scientist"
            description += "\nGrants " + str(scientist_level) + " points per turn."
            self.panel_widgets["ScientistInfo"].configure(text = description)
            self.panel_widgets["ScientistInfo"].place(x=self.board_width + self.img_size, y=self.cell_height * self.height * 3 / 10 + self.img_size, anchor = tk.W)
        elif self.testing and self.board.cells[row][col].team is cell.neutral_str:
            self.drawAddLeft()
        if self.board.cells[row][col].isFarmer():
            self.panel_widgets["FarmerPic"].place(x=self.board_width + self.img_size / 2, y=self.cell_height * self.height * 3 / 10 + self.img_size * 2, anchor = tk.CENTER)
            description = "Level " + str(self.board.cells[row][col].farmerLevel()) + " Farmer"
            description += "\nImproves adjacent land proportional to level."
            self.panel_widgets["FarmerInfo"].configure(text=description)
            self.panel_widgets["FarmerInfo"].place(x=self.board_width + self.img_size, y=self.cell_height * self.height * 3 / 10 + self.img_size * 2, anchor = tk.W)
        elif self.board.cells[row][col].isHunter():
            self.panel_widgets["HunterPic"].place(x=self.board_width + self.img_size / 2, y=self.cell_height * self.height * 3 / 10 + self.img_size * 2, anchor = tk.CENTER)
            description = "Level " + str(self.board.cells[row][col].hunterLevel()) + " Hunter"
            description += "\nVastly improves land proportional to level when neighbors die."
            self.panel_widgets["HunterInfo"].configure(text=description)
            self.panel_widgets["HunterInfo"].place(x=self.board_width + self.img_size, y=self.cell_height * self.height * 3 / 10 + self.img_size * 2, anchor = tk.W)
        elif self.testing and self.board.cells[row][col].team is cell.neutral_str:
            self.drawAddRight()
        self.drawPanelButtons()
        self.panel_widgets["Title"].configure(text = self.board.cells[row][col].team)
        self.panel_widgets["Title"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = 0, anchor = tk.N)
        self.panel_widgets["Land"].configure(text = "Land Quality: " + self.board.land[row][col].description())
        if self.board.cells[row][col].team not in cell.neutral_teams:
            self.panel_widgets["Strength"].configure(text = "Strength: " + str(self.board.cells[row][col].strength))
            self.panel_widgets["Strength"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = self.cell_height * 2, anchor = tk.CENTER)
            self.panel_widgets["Land"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = self.cell_height * 2.75, anchor = tk.CENTER)
        else:
            self.panel_widgets["Land"].place(x=self.board_width + self.cell_width * self.info_panel_span * 2.38 / 5, y = self.cell_height * 2, anchor = tk.CENTER)
    def drawPanelButtons(self):
        can_volcano = (self.board.points[self.player_team] >= board.volcano_cost or self.testing)
        for (row,col) in self.board.selected[self.player_team]:
            can_volcano = can_volcano and ((row,col) not in self.board.volcanoes or 1 not in self.board.volcanoes[(row,col)])
        if can_volcano:
            volc_button_state = tk.NORMAL
        else:
            volc_button_state = tk.DISABLED
        can_tornado = self.testing or (self.board.points[self.player_team] >= board.tornado_cost and self.board.cells[row][col].team is cell.neutral_str)
        if can_tornado:
            tornado_button_state = tk.NORMAL
        else:
            tornado_button_state = tk.DISABLED
        self.panel_widgets["Volcano"].configure(state = volc_button_state)
        self.panel_widgets["Volcano"].place(x=self.board_width, y=self.info_panel.winfo_height() - (len(self.board.teams)-.5) * self.cell_height * 4 / 5, anchor=tk.W)
        self.panel_widgets["Tornado"].configure(state = tornado_button_state)
        self.panel_widgets["Tornado"].place(x=self.board_width + self.cell_width * self.info_panel_span / 2, y=self.info_panel.winfo_height() - (len(self.board.teams)-.5) * self.cell_height * 4 / 5, anchor=tk.CENTER)
    def drawAddLeft(self):
        self.panel_widgets["AddLeft"].configure(text="Add Red")
        self.panel_widgets["AddLeft"].place(x=self.board_width + self.img_size, y=self.cell_height * self.height * 3 / 10 + self.img_size, anchor = tk.W)
    def drawAddRight(self):
        self.panel_widgets["AddRight"].configure(text="Add Blue")
        self.panel_widgets["AddRight"].place(x=self.board_width + self.img_size, y = self.cell_height * self.height * 3 / 10 + self.img_size * 2, anchor = tk.W)
    def settingsPanel(self):
        self.panel_widgets["TornadoCheck"].place(x=self.board_width + self.cell_width, y = self.cell_height / 2, anchor = tk.CENTER)
        self.panel_widgets["Mode"].place(x=self.board_width + self.cell_width, y = self.cell_height, anchor = tk.N)
        if self.mode.get() == self.vers_ai_str:
            self.panel_widgets["Difficulty"].place(x=self.board_width + self.cell_width * 3, y = self.cell_height, anchor = tk.N)
        self.panel_widgets["Confirm"].place(x = self.board_width + self.cell_width * self.info_panel_span / 3 * .95, y = self.info_panel.winfo_height() - self.cell_height, anchor = tk.S)
        self.panel_widgets["Cancel"].place(x = self.board_width + self.cell_width * 2 * self.info_panel_span / 3 * .95, y = self.info_panel.winfo_height() - self.cell_height, anchor = tk.S)
    def drawPanel(self):
        self.clearPanel()
        if len(self.board.selected[self.player_team]) == 1:
            self.drawSelectedInfo()
        elif self.testing and len(self.board.selected[self.player_team]) >= 2:
            r,c = iter(self.board.selected[self.player_team]).next()
            if self.board.cells[r][c].team is cell.neutral_str:
                self.drawAddLeft()
                self.drawAddRight()
            self.drawPanelButtons()
        self.settings_button.configure(text="Settings")
    def drawCells(self):
        with self.board.lock:
            for row in range(self.height):
                for col in range(self.width):
                    self.drawCell(row,col)
    def drawCell(self, row, col):
        with self.board.lock:
            self.cells.delete(self.text_ids[row][col])
            for spec_id in self.spec_ids[row][col]:
                self.cells.delete(spec_id)
            self.spec_ids[row][col] = []
            if (row,col) in self.board.lava_cells:
                self.cells.itemconfigure(self.rect_ids[row][col],fill = '#FF0000')
                self.board.lava_cells.remove((row,col))
            elif (row,col) not in self.board.warning_cells:
                self.cells.itemconfigure(self.rect_ids[row][col],fill = self.board.color(row,col))
            else:
                self.cells.itemconfigure(self.rect_ids[row][col], fill = self.board.warning_cells[(row,col)])
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
                    if self.changePhoto((self.cell_width - 3,self.cell_height - 3),"assets/tornado.gif"):
                        self.text_ids[row][col] = self.cells.create_image(self.cell_width * col + self.cell_width/2 - 1, self.cell_height * row + self.cell_height/2 - 1,image=self.photoimage)
                else:
                    text = str(len(self.board.friendlyAdj(row,col)))
                    self.text_ids[row][col] = self.cells.create_text(self.cell_width * col + self.cell_width/2 - 1,self.cell_height * row + self.cell_height/2 - 1,text=text, fill=color, font = self.cell_font)
                    if self.board.cells[row][col].isWarrior():
                        if self.changePhoto((self.cell_width/3 - 1,self.cell_height/3), "assets/sword.gif"):
                            self.spec_ids[row][col].append(self.cells.create_image(self.cell_width * col + 2,self.cell_height * row + 2,image=self.photoimage, anchor=tk.NW))
                    elif self.board.cells[row][col].isMedic():
                        if self.changePhoto((self.cell_width/3 - 1,self.cell_height/3), "assets/bandage.gif"):
                            self.spec_ids[row][col].append(self.cells.create_image(self.cell_width * (col + 1) - 2,self.cell_height * row + 2,image=self.photoimage, anchor=tk.NE))
                    if self.board.cells[row][col].isCleric():
                        if self.changePhoto((self.cell_width/3 - 1,self.cell_height/3), "assets/candle.gif"):
                            self.spec_ids[row][col].append(self.cells.create_image(self.cell_width * col + 2,self.cell_height * row + 1 + self.cell_height / 3,image=self.photoimage, anchor=tk.NW))
                    elif self.board.cells[row][col].isScientist():
                        if self.changePhoto((self.cell_width/3 - 1,self.cell_height/3), "assets/testTube.gif"):
                            self.spec_ids[row][col].append(self.cells.create_image(self.cell_width * (col + 1) - 2,self.cell_height * row + 1 + self.cell_height / 3,image=self.photoimage, anchor=tk.NE))
                    if self.board.cells[row][col].isFarmer():
                        if self.changePhoto((self.cell_width/3 - 1,self.cell_height - 2 * self.cell_height/3 - 1), "assets/pitchfork.gif"):
                            self.spec_ids[row][col].append(self.cells.create_image(self.cell_width * col + 2,self.cell_height * (row + 1) - 2,image=self.photoimage, anchor=tk.SW))
                    elif self.board.cells[row][col].isHunter():
                        if self.changePhoto((self.cell_width/3 - 1,self.cell_height - 2 * self.cell_height/3 - 1), "assets/bow.gif"):
                            self.spec_ids[row][col].append(self.cells.create_image(self.cell_width * (col + 1) - 2,self.cell_height * (row + 1) - 2,image=self.photoimage, anchor=tk.SE))
            self.outlineIfSelected(row,col)

#def reportEvent(event):
#    print 'keysym=%s, keysym_num=%s' % (event.keysym, event.keysym_num)
