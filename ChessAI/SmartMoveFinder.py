import random

pieceScore = {"K":0, "Q":9, "R":5, "B":3, "N":3, "p":1}

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove():
    return