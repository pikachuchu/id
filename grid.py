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
        ret = []
        for r in [row-1, row, row+1]:
            for c in [col-1, col, col+1]:
                if not (r == row and c == col) and r >= 0 and c >= 0 and r < self.length and c < self.width:
                    ret.append((r,c))
        return ret
    def reset(self):
        self.turn = 0
        for row in range(self.length):
            for col in range(self.width * 2 / 5):
                result = self.rand.random()
                if result < .75:
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
    def step(self):
        step = [[neutral() for col in range(self.width)] for row in range(self.length)]
        for row in range(self.length):
            for col in range(self.width):
                counts = collections.Counter() 
                strengths = collections.Counter()
                for (r,c) in self.adj(row,col):
                    counts[self.cells[r][c].team] += 1
                    strengths[self.cells[r][c].team] += self.cells[r][c].strength
                if self.cells[row][col].team != neutralstr:
                    friendly = counts[self.cells[row][col].team]
                    if friendly >= 2 and friendly <= 3:
                        step[row][col] = self.cells[row][col]
                else:
                    threes = []
                    for team, count in counts.items():
                        if count == 3 and team != neutralstr:
                            threes.append(team)
                    if len(threes) == 1:
                        strength = strengths[threes[0]] + self.rand.randint(1,9)
                        step[row][col] = Cell(threes[0], strength / 4)
                    if len(threes) == 2:
                        if strengths[threes[0]] > strengths[threes[1]]:
                            winner = threes[0]
                        elif strengths[threes[0]] < strengths[threes[1]]:
                            winner = threes[1]
                        else:
                            winner = threes[self.rand.randint(0,1)]
                        strength = strengths[winner] + self.rand.randint(1,9)
                        step[row][col] = Cell(winner, strength / 4)
        self.cells = step
        self.turn += 1
    def extinct(self):
        for row in range(self.length):
            for col in range(self.width):
                if self.cells[row][col].team != neutralstr:
                    return False
        return True

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
