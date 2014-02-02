class Beliefs:
    def __init__(self):
        self.probabilities = dict()
        self.arg_max = None
        self.total = 0
    def __getitem__(self, key):
        return self.probabilities[key] 
    def __setitem__(self, key, value):
        if self.probabilities.has_key(key):
            self.total -= self.probabilities[key]
            self.total += value
        self.probabilities[key] = value 
        if value > self.probabilities[self.arg_max]: 
            self.arg_max = key
    def __delitem__(self, key):
        self.total -= self.probabilities[key]
        del self.probabilities[key]
        value_max = 0 
        if key == self.arg_max:
            for team in self.probabilities: 
                if self.probabilities[team] > value_max:
                    value_max = self.probabilities[team]
                    self.arg_max = team 
    def normalize(self):
        if self.total != 0:
            for key in self.probabilities:
                self.probabiities[key] /= total
    def argMax(self):
        return self.arg_max
