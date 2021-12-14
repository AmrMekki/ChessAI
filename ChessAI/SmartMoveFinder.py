import random

pieceScore = {"K":0, "Q":9, "R":5, "B":3, "N":3, "p":1}
CHECKMATE = 1000
STALEMATE = 0


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove():
    return

"""
Score the board based on material.
"""
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0]=='w':
                score+= pieceScore[square[1]]
            elif square[0]=='b':
                score-= pieceScore[square[1]]
    return score
