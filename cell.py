import random
import copy
class Cell:
    # read only
    def __init__(self, team, strength, dna):
        self.team = team
        self.strength = strength
        self.dna = dna 
        self.updatePheno()
    def updatePheno(self):
        self.pheno = [self.dna[0][i] + self.dna[1][i] + self.dna[2][i] for i in range(3)]
    def specialize(self, mod):
        to_change, change_by = mod
        for strand in self.dna:
            strand[to_change] += change_by
        self.updatePheno()
    def modFromString(self, specialization):
        # return (to_change, change_by)
        if specialization == "Medic":
            return (0, 1)
        elif specialization == "Warrior":
            return (0,-1)
        elif specialization == "Cleric":
            return (1, 1)
        elif specialization == "Scientist":
            return (1,-1)
        elif specialization == "Farmer":
            return (2, 1)
        elif specialization == "Hunter":
            return (2,-1)
        else:
            raise Exception("Unknown specialization")
    def __str__(self):
        ret = str(self.strength)
        if self.isWarrior():
            ret += "W"
        elif self.isMedic():
            ret += "M"
        if self.isCleric():
            ret += "C"
        elif self.isScientist():
            ret += "S"
        if self.isFarmer():
            ret += "F"
        elif self.isHunter():
            ret += "H"
        return ret
    def __eq__(self, other):
        return self.team == other.team and self.strength == other.strength
    def __ne__(self, other):
        return not self == other
    def isMedic(self):
        return self.pheno[0] > 1
    def isMedic2(self):
        return self.pheno[0] > 4
    def medicLevel(self):
        return (1 + self.pheno[0]) / 3
    def isWarrior(self):
        return self.pheno[0] < -1
    def isWarrior2(self):
        return self.pheno[0] < -4
    def warriorLevel(self):
        return (-self.pheno[0] + 1) / 3
    def isCleric(self):
        return self.pheno[1] > 1
    def isCleric2(self):
        return self.pheno[1] > 4
    def clericLevel(self):
        return (self.pheno[1] + 1) / 3
    def isScientist(self):
        return self.pheno[1] < -1
    def isScientist2(self):
        return self.pheno[1] < -4
    def scientistLevel(self):
        return (-self.pheno[1] + 1) / 3
    def isFarmer(self):
        return self.pheno[2] > 1
    def isFarmer2(self):
        return self.pheno[2] > 4
    def farmerLevel(self):
        return (self.pheno[2] + 1) / 3
    def isHunter(self):
        return self.pheno[2] < -1
    def isHunter2(self):
        return self.pheno[2] < -4
    def hunterLevel(self):
        return (-self.pheno[2] + 1) / 3
    def randStrand(self):
        return random.choice(self.dna)
def offspring(cell1, cell2, cell3):
    return Cell(cell1.team, (cell1.strength + cell2.strength + cell3.strength + random.randint(1,12)) / 4, [copy.copy(cell1.randStrand()), copy.copy(cell2.randStrand()), copy.copy(cell3.randStrand())])
def initDna():
    return [[0,0,0], [0,0,0], [0,0,0]]
neutral_str = "N"
def neutral():
    return Cell(neutral_str,0, initDna())
tornado_str = "T"
def tornado():
    return Cell(tornado_str,0, initDna())
neutral_teams = [neutral_str, tornado_str]
specializations = ['Warrior','Medic','Cleric','Scientist','Farmer','Hunter']

