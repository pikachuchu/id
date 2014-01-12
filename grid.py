import random
import collections
class Cell:
    # read only
    def __init__(self, team, strength, dna):
        self.team = team
        self.strength = strength
	self.dna = dna 
	self.pheno = [dna[0][i] + dna[1][i] + dna[2][i] for i in range(3)]
    def __str__(self):
        return str(self.team) + str(self.strength)
    def __eq__(self, other):
        return self.team == other.team and self.strength == other.strength
    def __ne__(self, other):
        return not self == other
    def isMedic(self):
        return self.pheno[0] > 1
    def isMedic2(self):
        return self.pheno[0] > 4
    def isWarrior(self):
        return self.pheno[0] < -1
    def isWarrior2(self):
        return self.pheno[0] < -4
    def isPriest(self):
        return self.pheno[1] > 1
    def isPriest2(self):
        return self.pheno[1] > 4
    def isScientist(self):
        return self.pheno[1] < -1
    def isScientist2(self):
        return self.pheno[1] < -4
    def isFarmer(self):
        return self.pheno[2] > 1
    def isFarmer2(self):
        return self.pheno[2] > 4
    def isHunter(self):
        return self.pheno[2] < -1
    def isHunter2(self):
        return self.pheno[2] < -4
    def randStrand(self):
        return random.choice(self.dna)
def offspring(cell1, cell2, cell3):
    return Cell(cell1.team, (cell1.strength + cell2.strength + cell3.strength + random.randint(1,12)) / 4, [cell1.randStrand(), cell2.randStrand(), cell3.randStrand()])
def initDna():
    return [(0,0,0), (0,0,0), (0,0,0)]
neutral_str = "N"
def neutral():
    return Cell(neutral_str,0, initDna())
tornado_str = "T"
def tornado():
    return Cell(tornado_str,0, initDna())
neutral_teams = [neutral_str, tornado_str]
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
class Land:
    def __init__(self, percent):
        self.percent = percent
    def isLiving(self):
        return self.percent >= .05
    def canSupport(self, neighbors):
        if self.percent < .05:
            return False
        if self.percent < .25:
            return neighbors == 2
        if self.percent < .75:
            return neighbors == 2 or neighbors == 3
        return neighbors >= 2 and neighbors <= 4
    def color(self):
        if self.percent < .05:
            return '#000000' 
        if self.percent < .25:
            return '#663300'
        if self.percent < .75:
            return '#99FF33'
        return '#009900'
    def regen(self):
        self.percent += .04 * self.percent
        self.percent = min(self.percent, 1.0)
    def deplete(self, cell):
        if cell != neutral():
            self.percent -= .05
            self.percent -= (abs(cell.pheno[0]) + abs(cell.pheno[1]) + abs(cell.pheno[2])) * .01
    def decimate(self, prop):
        self.percent *= prop 
def baseLand():
    return Land(.6)
class Grid:
    def __init__(self, height = 8, width = 8):
        self.cells = [[neutral() for col in range(width)] for row in range(height)]
        self.rand = random.Random()
        self.width = width
        self.height = height 
        self.reset()
    def __str__(self):
        cat = ""
        for row in self.cells:
            for cell in row:
                cat += str(cell) + "\t"
            cat += "\n"
        return cat
    def inGrid(self, row, col):
        return row >= 0 and col >= 0 and row < self.height and col < self.width
    def adj(self, row, col):
        # return list of valid adjacent cell indices (row, col)
        # counter clockwise
        ret = []
        for diff_x, diff_y in [(1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0)]:
            r = row +diff_x
            c = col + diff_y
            if self.inGrid(r,c):
                ret.append((r,c))
        return ret
    def reset(self):
        self.turn = 0
        self.land = [[baseLand() for col in range(self.width)] for row in range(self.height)]
        self.selected = set()
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
                    self.cells[row][col] = Cell("R", 3, initDna())
                    self.cells[row][self.width - col - 1] = Cell("B", 3, initDna())
                else:
                    self.cells[row][col] = neutral()
                    self.cells[row][self.width - col - 1] = neutral()
        self.cells[self.width / 2][self.height / 2] = tornado()
    def color(self, row, col):
        return self.land[row][col].color()
    def step(self):
        self.external()
        self.internal()
    def external(self):
        ret = False # return whether anything was effected
        self.tornadoes = []
        for row in range(self.height):
            for col in range(self.width):
                if self.cells[row][col].team == tornado_str:
                    adjacents = self.adj(row,col)
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
                        temp1 = (r1,c1) in self.selected
                        temp2 = (r2,c2) in self.selected
                        if temp2:
                            self.selected.add((r1,c1))
                        elif temp1:
                            self.selected.remove((r1,c1))
                        if temp1:
                            self.selected.add((r2,c2))
                        elif temp2:
                            self.selected.remove((r2,c2))
                    # set new location
                    r, c = random.choice(adjacents)
                    self.tornadoes.append((r,c))
        return ret
    def internal(self):
        step = [[neutral() for col in range(self.width)] for row in range(self.height)]
        for row in range(self.height):
            for col in range(self.width):
                self.land[row][col].deplete(self.cells[row][col])
                self.land[row][col].regen()
                counts = collections.Counter() 
                strengths = collections.Counter()
                for (r,c) in self.adj(row,col):
                    counts[self.cells[r][c].team] += 1
                    strengths[self.cells[r][c].team] += self.cells[r][c].strength
                if self.cells[row][col].team not in neutral_teams:
                    friendly = counts[self.cells[row][col].team]
                    sum_enemy = 0
                    for team, strength in strengths.items():
                        if team != self.cells[row][col].team:
                            sum_enemy += strength
                    if self.land[row][col].canSupport(friendly) and sum_enemy <= strengths[self.cells[row][col].team]:
                        step[row][col] = self.cells[row][col]
                    else:
                        if (row,col) in self.selected:
                            self.selected.remove((row,col))
                elif self.cells[row][col].team == neutral_str:
                    threes = []
                    for team, count in counts.items():
                        if count == 3 and team not in neutral_teams:
                            threes.append(team)
                    if len(threes) == 1:
                        strength = strengths[threes[0]] + self.rand.randint(1,12)
                        parents = [self.cells[loc[0]][loc[1]] for loc in self.adj(row,col) if self.cells[loc[0]][loc[1]].team == threes[0]] 
                        step[row][col] = offspring(parents[0],parents[1],parents[2])
                    if len(threes) == 2:
                        if strengths[threes[0]] > strengths[threes[1]]:
                            winner = threes[0]
                        elif strengths[threes[0]] < strengths[threes[1]]:
                            winner = threes[1]
                        else:
                            winner = threes[self.rand.randint(0,1)]
                        parents = [self.cells[loc[0]][loc[1]] for loc in self.adj(row,col) if self.cells[loc[0]][loc[1]].team == winner] 
                        step[row][col] = offspring(parents[0],parents[1],parents[2])
        for r,c in self.tornadoes:
            step[r][c] = tornado()
        self.cells = step
        self.turn += 1
    def extinct(self):
        for row in range(self.height):
            for col in range(self.width):
                if self.cells[row][col].team != neutral_str:
                    return False
        return True
    def kill(self, row, col):
        if self.cells[row][col].team not in neutral_teams:
            self.cells[row][col] = neutral()
            return True
        return False
    def select(self, row, col):
        if set([(row,col)]) == self.selected:
            self.selected.clear()
        else:
            self.selected.clear()
            self.selected.add((row,col))
    def selectAll(self, row, col):
        self.selected.clear()
        self.addAll(row, col)
    def toggle(self, row, col):
        if (row,col) in self.selected:
            self.selected.remove((row,col))
        else:
            self.selected.add((row,col))
    def addAll(self, row, col):
        self.selected.add((row,col))
        frontier = collections.deque()
        visited = set([(row,col)])
        frontier.append((row,col))
        team = self.cells[row][col].team
        while frontier:
            prow, pcol = frontier.pop()
            for (arow,acol) in self.adj(prow,pcol):
                if (arow,acol) not in visited:
                    if self.cells[arow][acol].team == team:
                        visited.add((arow,acol))
			self.selected.add((arow,acol))
                        frontier.append((arow,acol))
    def clearSelection(self):
        if len(self.selected) == 0:
            return False
        self.selected.clear()
        return True
    def move(self, displacement):
        for row, col in self.selected:
            brow = row + displacement[0]
            bcol = col + displacement[1]
            if self.inGrid(brow, bcol) and (self.cells[brow][bcol] == neutral() or (brow,bcol) in self.selected):
                continue
            else:
                break
        else:
            #move is valid
            ordered = sorted(self.selected, key = orderings[displacement])
            for row, col in ordered:
                brow = row + displacement[0]
                bcol = col + displacement[1]
                self.cells[brow][bcol] = self.cells[row][col]
                self.cells[row][col] = neutral() 
                self.selected.remove((row,col))
                self.selected.add((brow,bcol))
            
            
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

