import random
import cell
import thread
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
                with board.lock:
                    pass
        else:
            cont[0] = False
    thread.exit()
