import random
import cell
import thread
import copy
app = None
# FIXME need to update board
# cont is a single member array bool (continue)
def easy(board, team, turn, strat, cont):
    # spends points on specialization randomly
    # no other actions
    mycells = []
    for row in range(board.height):
        for col in range(board.width):
            if board.cells[row][col].team == team:
                mycells.append((row,col))
    while board.points[team] > 1 and cont[0]:
        if mycells:
            row, col = random.choice(mycells)
            specialization = random.choice(strat)
            if not board.aiAct(turn, team, specialization, (row,col)):
                # our turn is over
                cont[0] = False
            else:
                app.eventq.put((app.drawThings,()))
        else:
            cont[0] = False
    thread.exit()

def medium(board, team, turn, strat, cont):
    #kill cells that land cannot support
    mycells = []
    for row in range(board.height):
        for col in range(board.width):
            if board.cells[row][col].team == team:
                mycells.append((row,col))
    while board.points[team] > 1 and cont[0]:
        if mycells:
            row, col = random.choice(mycells)
            specialization = random.choice(strat)
            if specialization is not "Farmer" and specialization is not "Hunter":
                specialization = random.choice(strat)
            if not board.aiAct(turn, team, specialization, (row,col)):
                # our turn is over
                cont[0] = False
            else:
                app.eventq.put((app.drawThings,()))
        else:
            cont[0] = False
    if cont[0]:
        #sorts cells by specialization
        mycells = sorted(mycells, key = lambda(r,c): sum([abs(board.cells[r][c].pheno[i]) for i in range(3)]))
        while cont[0]:
            for index, (r,c) in enumerate(mycells):
                count = 0
                for x,y in board.adj(r,c):
                    if board.cells[x][y].team == team:
                        count += 1 
                if count >= 2 and not board.land[r][c].canSupport(count):
                    if not board.aiAct(turn, team, "kill", (r,c)):
                        # our turn is over
                        cont[0] = False
                        break
                    else:
                        app.eventq.put((app.drawThings,()))
                        del mycells[index]
                    break
            else:
                break
    thread.exit()
def adj(board, row, col):
        # return list of valid adjacent cell indices (row, col)
        # counter clockwise
        ret = []
        for diff_x, diff_y in [(1,1), (0,1), (-1,1), (-1,0), (-1,-1), (0,-1), (1,-1), (1,0)]:
            r = row +diff_x
            c = col + diff_y
            if r >= 0 and c >= 0 and r < len(board) and c < len(board[r]):
                ret.append((r,c))
        return ret
"""
def probDist(cells, lands, ai_team):
    #TODO copy cells and land into 2D array
    board_copy = copy.deepcopy(cells)
    land_copy = copy.deepcopy(lands)
    probabilities = dict()
    tornados = []
    parents = collections.Counter()
    #TODO tornado rotation
    for row in range(len(board_copy)):
        for col in range(len(board_copy[row])):
            probabilities[(row,col)] = beliefs.Beliefs()
            adjacents = adj(board_copy, row,col)
            counts = collections.Counter()
            strengths = collections.Counter()
            team = board_copy[row][col].team
            for (r,c) in adjacents:
                counts[board_copy[r][c].team] += 1
                strengths[board_copy[r][c].team] += board_copy[r][c].strength
            if team == cell.neutral_str:
                threes = []
                for c_team, count in counts.items():
                    if count == 3 and c_team not in cell.neutral_teams:
                        threes.append(c_team)
                if len(threes) == 1:
                    probabiltiies[(row,col)][threes[0]] = 1
                    for (r,c) in adjacents:
                        if threes == ai_team and board_copy[r][c].team == threes:
                            parents[(r,c)] += 1
                elif len(threes) == 2:
                    if strengths[threes[0]] > strengths[threes[1]]:
                        probabilities[(row,col)][threes[0]] = 1
                    elif strengths[threes[0]] < strengths[threes[1]]:
                        probabilities[(row,col)][threes[1]] = 1
                    else:
                        probabilities[(row,col)][threes[0]] = .05
                        probabilities[(row,col)][threes[1]] = .05
            elif team == cell.tornado_str]:
                tornados.append((row,col))
            else:
                if board_copy[row][col].isWarrior():
                    strengths[team] += board_copy[row][col].strength
                if land_copy[row][col].canSupport(counts[team]):
                    if strengths[team] >  
                    probabilities[(row,col)][team] = 1
    for row,col in tornados:
        adjacents = board.adj(row,col)
        for r,c in adjacents:
            probabilities[(r,c)][cell.tornado_str] = 1/len(adjacents)
"""
