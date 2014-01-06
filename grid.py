import random
import collections
class Cell:
    # read only
    def __init__(self, team, strength):
        self.team = team
        self.strength = strength
    def __str__(self):
        return str(self.team) + str(self.strength)
neutralstr = "N"
def neutral():
    return Cell(neutralstr,0)
tornadostr = "T"
def tornado():
    return Cell(tornadostr,0)
neutralteams = [neutralstr, tornadostr]
class Grid:
    def __init__(self, length = 8, width = 8):
        self.cells = [[neutral() for col in range(width)] for row in range(length)]
        self.rand = random.Random()
        self.width = width
        self.length = length
        self.reset()
    def __str__(self):
        cat = ""
        for row in self.cells:
            for cell in row:
                cat += str(cell) + "\t"
            cat += "\n"
        return cat
    def adj(self, row, col):
        # return list of valid adjacent cell indices (row, col)
        # counter clockwise
        ret = []
        for diffx, diffy in [(1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0)]:
            r = row +diffx
            c = col + diffy
            if r >= 0 and c >= 0 and r < self.length and c < self.width:
                ret.append((r,c))
        return ret
    def reset(self):
        self.turn = 0
        for row in range(self.length):
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
                    self.cells[row][col] = Cell("R", 3)
                    self.cells[row][self.width - col - 1] = Cell("B", 3)
                else:
                    self.cells[row][col] = neutral()
                    self.cells[row][self.width - col - 1] = neutral()
        self.cells[self.width / 2][self.length / 2] = tornado()
    def step(self):
        step = [[neutral() for col in range(self.width)] for row in range(self.length)]
        tornadoes = []
        for row in range(self.length):
            for col in range(self.width):
                if self.cells[row][col].team == tornadostr:
                    adjacents = self.adj(row,col)
                    temp = None
                    for i in reversed(range(len(adjacents))):
                         r1,c1 = adjacents[i]
                         r2,c2 = adjacents[(i + 1) % len(adjacents)]
                         temp = self.cells[r1][c1]
                         self.cells[r1][c1] = self.cells[r2][c2]
                         self.cells[r2][c2] = temp
                    # set new location
                    r, c = random.choice(adjacents)
                    tornadoes.append((r,c))
        for row in range(self.length):
            for col in range(self.width):
                counts = collections.Counter() 
                strengths = collections.Counter()
                for (r,c) in self.adj(row,col):
                    counts[self.cells[r][c].team] += 1
                    strengths[self.cells[r][c].team] += self.cells[r][c].strength
                if self.cells[row][col].team not in neutralteams:
                    friendly = counts[self.cells[row][col].team]
                    sumenmy = 0
                    for team, strength in strengths.items():
                        if team != self.cells[row][col].team:
                            sumenmy += strength
                    if friendly >= 2 and friendly <= 3 and sumenmy <= strengths[self.cells[row][col].team]:
                        step[row][col] = self.cells[row][col]
                elif self.cells[row][col].team == neutralstr:
                    threes = []
                    for team, count in counts.items():
                        if count == 3 and team not in neutralteams:
                            threes.append(team)
                    if len(threes) == 1:
                        strength = strengths[threes[0]] + self.rand.randint(1,12)
                        step[row][col] = Cell(threes[0], strength / 4)
                    if len(threes) == 2:
                        if strengths[threes[0]] > strengths[threes[1]]:
                            winner = threes[0]
                        elif strengths[threes[0]] < strengths[threes[1]]:
                            winner = threes[1]
                        else:
                            winner = threes[self.rand.randint(0,1)]
                        strength = strengths[winner] + self.rand.randint(1,12)
                        step[row][col] = Cell(winner, strength / 4)
        for r,c in tornadoes:
            step[r][c] = tornado()
        self.cells = step
        self.turn += 1
    def extinct(self):
        for row in range(self.length):
            for col in range(self.width):
                if self.cells[row][col].team != neutralstr:
                    return False
        return True
    def kill(self, row, col):
        self.cells[row][col] = neutral()
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
