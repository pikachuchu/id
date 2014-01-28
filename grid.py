import random
import collections
from cell import Cell, neutral, initDna, tornado, neutral_str, tornado_str, neutral_teams, offspring, specializations
from land import baseLand
import threading
import ai
import copy
orderings = {
    (1,1): lambda x: -x[0],
    (0,1): lambda x: -x[1],
    (-1,1): lambda x: x[1],
    (-1,0): lambda x: x[0],
    (-1,-1): lambda x: x[0],
    (0,-1): lambda x: x[1],
    (1,-1): lambda x: -x[0],
    (1,0): lambda x: -x[0]
}
class Grid:
    def __init__(self, height = 8, width = 8, team1 = "Red", team2 = "Blue"):
        self.cells = [[neutral() for col in range(width)] for row in range(height)]
        self.rand = random.Random()
        self.width = width
        self.height = height 
        self.teams = [team1,team2]
        self.lock = threading.RLock()
        self.reset()
    def __str__(self):
        with self.lock:
            cat = ""
            for row in self.cells:
                for cell in row:
                    cat += str(cell) + "\t"
                cat += "\n"
            return cat
    def inGrid(self, row, col):
        with self.lock:
            return row >= 0 and col >= 0 and row < self.height and col < self.width
    def adj(self, row, col):
        with self.lock:
            # return list of valid adjacent cell indices (row, col)
            # counter clockwise
            ret = []
            for diff_x, diff_y in [(1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0)]:
                r = row +diff_x
                c = col + diff_y
                if self.inGrid(r,c):
                    ret.append((r,c))
            return ret
    def reset(self, include_tornado = True, testing = False):
        with self.lock:
            self.testing = testing
            self.turn = 0
            self.land = [[baseLand() for col in range(self.width)] for row in range(self.height)]
            self.selected = dict()
            for team in self.teams:
                self.selected[team] = set()
            self.points = collections.Counter()
            self.points[self.teams[0]] = 0
            self.points[self.teams[1]] = 0
            for row in range(self.height):
                for col in range((self.width + 1) / 2):
                    result = self.rand.random()
                    if result < .75 and col < self.width * 2 / 5:
                        # <   1000 10000
                        # .25 .265 .2927
                        # .35 .385
                        # .50 .469
                        # .55 .487 .4802
                        # .60 .518 .4972
                        # .65 .522 .5022
                        # .66      .4956
                        # .67 .509 .5052
                        # .68      .4987
                        # .70 .522 .5001
                        # .75 .488 .5182
                        # .76      .5012
                        # .77      .4969
                        # .80      .5126
                        # .85      .4758
                        self.cells[row][col] = Cell(self.teams[0], 3, initDna())
                        self.cells[row][self.width - col - 1] = Cell(self.teams[1], 3, initDna())
                    else:
                        self.cells[row][col] = neutral()
                        self.cells[row][self.width - col - 1] = neutral()
            if include_tornado:
                self.cells[self.width / 2][self.height / 2] = tornado()
    def color(self, row, col):
        with self.lock:
            return self.land[row][col].color()
    def step(self):
        with self.lock:
            self.external()
            self.internal()
    def external(self):
        ret = False # return whether anything was effected
        self.old_tornadoes = []
        self.tornadoes = []
        conversions = []
        with self.lock:
            for row in range(self.height):
                for col in range(self.width):
                    adjacents = self.adj(row, col)
                    if self.cells[row][col].team == tornado_str:
                        self.land[row][col].decimate(.65)
                        for i in range(len(adjacents)):
                            r,c = adjacents[i]
                            self.land[r][c].decimate(.85)
                        for i in reversed(range(len(adjacents) - 1)):
                            r1,c1 = adjacents[i]
                            r2,c2 = adjacents[(i + 1) % len(adjacents)]
                            if self.cells[r2][c2].team != neutral_str:
                                ret = True
                            if self.cells[r1][c1].team != neutral_str:
                                ret = True
                            self.cells[r1][c1], self.cells[r2][c2] = self.cells[r2][c2], self.cells[r1][c1]
                            for team in self.teams:
                                temp1 = (r1,c1) in self.selected[team]
                                temp2 = (r2,c2) in self.selected[team]
                                if temp2:
                                    self.selected[team].add((r1,c1))
                                elif temp1:
                                    self.selected[team].remove((r1,c1))
                                if temp1:
                                    self.selected[team].add((r2,c2))
                                elif temp2:
                                    self.selected[team].remove((r2,c2))
                        self.old_tornadoes.append((row,col))
                        # set new location
                        r, c = random.choice(adjacents)
                        self.tornadoes.append((r,c))
                    elif self.cells[row][col].isFarmer():
                        colors = []
                        for r,c in adjacents:
                            colors.append(self.land[r][c].color())
                        for i in range(self.cells[row][col].farmerLevel()):
                            for r,c in adjacents:
                                self.land[r][c].regen()
                        for (r,c), color in zip(adjacents, colors):
                            ret = ret or self.land[r][c].color() == color
                    if self.cells[row][col].isCleric():
                        for r,c in adjacents:
                            if self.cells[r][c].team not in neutral_teams and not self.cells[r][c].isCleric():
                                if self.cells[r][c].team != self.cells[row][col].team:
                                    for i in range(self.cells[row][col].clericLevel()):
                                        if self.rand.random() < .10:
                                            conversions.append((self.cells[row][col].team, r, c))
                                            ret = True
                                            break
                    elif self.cells[row][col].isScientist():
                        self.points[self.cells[row][col].team] += self.cells[row][col].scientistLevel()
                    if self.cells[row][col].isWarrior():
                        allies = filter(lambda (r,c): self.cells[row][col].team == self.cells[r][c].team, adjacents)
                        if allies:
                            for i in range(self.cells[row][col].warriorLevel()):
                                r,c = self.rand.choice(allies)
                                self.cells[r][c].strength += 1 #max at 9?
                                ret = True
            for dteam, r, c in conversions:
                self.cells[r][c].team = dteam
            return ret
    def internal(self):
        self.turn += 1
        step = [[neutral() for col in range(self.width)] for row in range(self.height)]
        with self.lock:
            for row in range(self.height):
                for col in range(self.width):
                    self.land[row][col].deplete(self.cells[row][col])
                    self.land[row][col].regen()
                    counts = collections.Counter() 
                    strengths = collections.Counter()
                    adjacents = self.adj(row, col)
                    team = self.cells[row][col].team
                    for (r,c) in adjacents:
                        counts[self.cells[r][c].team] += 1
                        strengths[self.cells[r][c].team] += self.cells[r][c].strength
                    if team not in neutral_teams:
                        friendly = counts[team]
                        if self.cells[row][col].isWarrior2():
                            friendly += self.cells[row][col].strength
                        sum_enemy = 0
                        for str_team, strength in strengths.items():
                            if str_team != team:
                                sum_enemy += strength
                        is_dead = True 
                        if self.land[row][col].canSupport(friendly):
                            if sum_enemy < strengths[team]:
                                step[row][col] = self.cells[row][col]
                                is_dead = False
                            else:
                                for r,c in adjacents:
                                    if self.cells[r][c].team == team and self.cells[r][c].isMedic():
                                        for i in range(self.cells[r][c].medicLevel()):
                                            if self.rand.random() < .25:
                                                step[row][col] = self.cells[row][col]
                                                is_dead = False
                                                break
                                        else:
                                            # Medic did not save
                                            continue
                                        # Medic saved
                                        break
                                else:
                                    # killed in combat
                                    for str_team, strength in strengths.items():
                                        if str_team != team and str_team not in neutral_teams:
                                            self.points[str_team] += 1
                        if is_dead:
                            for k_team in self.selected.iterkeys():
                                if (row,col) in self.selected[k_team]:
                                    self.selected[k_team].remove((row,col))
                            for r,c in adjacents:
                                if self.cells[r][c].isHunter():
                                    for i in range(self.cells[r][c].hunterLevel()):
                                        self.land[row][col].regen()
                                        self.land[row][col].regen()
                                        self.land[row][col].regen()
                                        self.land[row][col].regen()
                    elif team == neutral_str:
                        threes = []
                        for c_team, count in counts.items():
                            if count == 3 and c_team not in neutral_teams:
                                threes.append(c_team)
                        if len(threes) == 1:
                            strength = strengths[threes[0]] + self.rand.randint(1,12)
                            parents = [self.cells[loc[0]][loc[1]] for loc in adjacents if self.cells[loc[0]][loc[1]].team == threes[0]] 
                            step[row][col] = offspring(parents[0],parents[1],parents[2])
                            self.points[threes[0]] += 1
                            for steam in self.selected:
                                if (row,col) in self.selected[steam]:
                                    self.selected[steam].remove((row,col))
                        elif len(threes) == 2:
                            if strengths[threes[0]] > strengths[threes[1]]:
                                winner = threes[0]
                            elif strengths[threes[0]] < strengths[threes[1]]:
                                winner = threes[1]
                            else:
                                winner = threes[self.rand.randint(0,1)]
                            parents = [self.cells[loc[0]][loc[1]] for loc in adjacents if self.cells[loc[0]][loc[1]].team == winner] 
                            step[row][col] = offspring(parents[0],parents[1],parents[2])
                            for steam in self.selected:
                                if (row,col) in self.selected[steam]:
                                    self.selected[steam].remove((row,col))
                            self.points[winner] += 1
            for (new_r, new_c), (old_r, old_c) in zip(self.tornadoes, self.old_tornadoes):
                step[new_r][new_c] = tornado()
                for team in self.teams:
                    if (old_r,old_c) in self.selected[team]:
                        self.selected[team].remove((old_r,old_c))
                        self.selected[team].add((new_r,new_c))
            self.cells = step
    def extinct(self):
        with self.lock:
            for row in range(self.height):
                for col in range(self.width):
                    if self.cells[row][col].team not in neutral_teams:
                        return False
            return True
    def kill(self, row, col, team):
        # returns true if any cells were killed
        ret = set()
        with self.lock:
            if (row, col) in self.selected[team]:
                if self.cells[row][col].team == team or self.testing:
                    for r,c in self.selected[team]:
                        self.cells[r][c] = neutral()
                        ret.add((r,c))
            else:
                if not self.selected[team]:
                    # nothing selected
                    if team == self.cells[row][col].team or self.testing:
                        self.cells[row][col] = neutral()
                        ret.add((row,col))
            ret = ret.union(self.clearSelection(team))
        return ret
    def specialize(self, specialization, team):
        with self.lock:
            if self.selected[team]:
                r,c = iter(self.selected[team]).next()
                if self.cells[r][c].team == team or self.testing:
                    cost = len(self.selected[team]) * 2
                    if cost > self.points[team] and not self.testing:
                        # TODO response
                        return "Mutation requires " + str(cost) + " points."
                    if self.testing:
                        self.points[self.cells[r][c].team] -= cost
                    else:
                        self.points[team] -= cost
                    for (row,col) in self.selected[team]:
                        mod = self.cells[row][col].modFromString(specialization)
                        self.cells[row][col].specialize(mod)
                else:
                    return "Cannot specialize enemy team."
        return self.selected[team]
    def select(self, row, col, team):
        with self.lock:
            was_selected = set([(row,col)]) == self.selected[team]
            self.clearSelection(team)
            if not was_selected:
                self.selected[team].add((row,col))
    def selectAll(self, row, col, team):
        with self.lock:
            self.clearSelection(team)
            self.addAll(row, col, team)
            return self.selected[team]
    def toggle(self, row, col, team):
        with self.lock:
            if (row,col) in self.selected[team]:
                self.selected[team].remove((row,col))
            else:
                if self.selected[team]:
                    r,c = iter(self.selected[team]).next() 
                    if self.cells[r][c].team != self.cells[row][col].team:
                        self.clearSelection(team)
                self.selected[team].add((row,col))
            return self.selected[team]
    def addAll(self, row, col, team):
        with self.lock:
            if self.selected[team]: 
                r,c = iter(self.selected[team]).next()
                if self.cells[r][c].team != self.cells[row][col].team:
                    self.clearSelection(team)
            self.selected[team].add((row,col))
            frontier = collections.deque()
            visited = set([(row,col)])
            frontier.append((row,col))
            while frontier:
                prow, pcol = frontier.pop()
                for (arow,acol) in self.adj(prow,pcol):
                    if (arow,acol) not in visited:
                        if self.cells[arow][acol].team == self.cells[row][col].team:
                            visited.add((arow,acol))
                            self.selected[team].add((arow,acol))
                            frontier.append((arow,acol))
            return self.selected[team]
    def clearSelection(self, team):
        with self.lock:
            ret = copy.copy(self.selected[team])
            self.selected[team].clear()
            return ret
    def move(self, displacement, team):
        with self.lock:
            ret = copy.copy(self.selected[team])
            if self.selected[team]:
                r,c = iter(self.selected[team]).next()
                if self.cells[r][c].team == tornado_str and not self.testing:
                    return "Cannot move tornado."
                if self.cells[r][c].team != team and not self.testing:
                    cost = len(self.selected[team]) * 2
                else:
                    cost = len(self.selected[team]) * 1
                if cost > self.points[team] and not self.testing:
                    # TODO response
                    return "Move requires " + str(cost) + " points."
                for row, col in self.selected[team]:
                    brow = row + displacement[0]
                    bcol = col + displacement[1]
                    if self.inGrid(brow, bcol) and (self.cells[brow][bcol] == neutral() or (brow,bcol) in self.selected[team]):
                        continue
                    else:
                        break
                else:
                    #move is valid
                    if self.testing:
                        self.points[self[r][c].team] -= cost
                    else:
                        self.points[team] -= cost
                    ordered = sorted(self.selected[team], key = orderings[displacement])
                    for row, col in ordered:
                        brow = row + displacement[0]
                        bcol = col + displacement[1]
                        self.cells[brow][bcol] = self.cells[row][col]
                        self.cells[row][col] = neutral() 
                        self.selected[team].remove((row,col))
                        self.selected[team].add((brow,bcol))
                        ret.add((brow,bcol))
        return ret
    def aiAct(self, turn, team, action, loc, displacement = None):
        ret = True
        row,col = loc
        with self.lock:
            # TODO lock
            if turn == self.turn:
                if action in specializations:
                    self.clearSelection(team)
                    self.selected[team].add(loc)
                    if not self.specialize(action, team):
                        ret = False
                elif action == "kill":
                    self.clearSelection(team)
                    killed = self.kill(row,col,team)
                    if not killed:
                        ret = False
                elif action == "move":
                    self.clearSelection(team)
                    self.selected[team].add(loc)
                    self.move(displacement,team)
            else:
                return False
        return ret
            
"""
extinct = 0
stable = 0
for x in range(1000):
    grid = Grid()
    for y in range(40):
        grid.step()
        if grid.extinct():
            extinct += 1
            break
    else:
        stable += 1
print "COMPLETE"
print "Stable: ", stable
"""

