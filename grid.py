import random
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
                if result < .70:
                    # <   1000 10000
                    # .25 .265
                    # .35 .385
                    # .50 .469
                    # .55 .487
                    # .60 .518
                    # .65 .522
                    # .67 .509 .5052
                    # .70 .522 .5001
                    # .75 .488
                    self.cells[row][col] = Cell("R", 3)
                    self.cells[row][self.width - col - 1] = Cell("R", 3) # TODO enmy
    def step(self):
        step = [[neutral() for col in range(self.width)] for row in range(self.length)]
        for row in range(self.length):
            for col in range(self.width):
                friendly = 0
                enemy = 0
                for (r,c) in self.adj(row,col):
                    if self.cells[r][c].team == self.cells[row][col].team:
                        friendly += 1
                    elif self.cells[r][c].team != neutralstr:
                        enemy += 1
                if self.cells[row][col].team != neutralstr:
                    if friendly >= 2 and friendly <= 3:
                        step[row][col] = self.cells[row][col]
                else:
                    if enemy == 3:
                        step[row][col] = Cell("R", 3)
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
for x in range(10000):
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
