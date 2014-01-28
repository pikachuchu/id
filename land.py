from cell import neutral
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
    def outlineColor(self):
        if self.percent < .05:
            return '#FFFF00' 
        if self.percent < .25:
            return '#FFFF00'
        if self.percent < .75:
            return '#000000'
        return '#000000'
    def description(self):
        percent = int(self.percent*100)
        if self.percent < .05:
            return 'Destroyed, ' + str(percent) + '%'
        if self.percent < .25:
            return 'Depleted, ' + str(percent) + '%'
        if self.percent < .75:
            return 'Normal, ' + str(percent) + '%'
        return 'Fertile, ' + str(percent) + '%'
    def regen(self):
        self.percent += .04 * self.percent
        self.percent = min(self.percent, 1.0)
    def deplete(self, cell):
        if cell != neutral():
            self.percent -= .05
            self.percent -= (abs(cell.pheno[0]) + abs(cell.pheno[1]) + abs(cell.pheno[2])) * .01
            self.percent = max(self.percent, .004)
    def decimate(self, prop):
        self.percent *= prop 
def baseLand():
    return Land(.6)
