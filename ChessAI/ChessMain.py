"""
this is our main driver file. It will be responsible for handling user input and displaying the current GameState
"""

import pygame as p

from ChessAI import ChessEngine

WIDTH = HEIGHT = 512  # 400 is another option
DIMENSION = 8  # dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # for animations later on
IMAGES = {}
""" 
Initialize a global dictionary of images. This will be called exactly once in the main 
"""


def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # Note: we can access an image by saying 'IMAGES['wp']'


""""  
The main driver for our code. This will handle user input and updating the graphics 
"""


def main():
    #p.init()
    background_colour = (255, 255, 255)
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(background_colour)
    gs = ChessEngine.GameState()
    print(gs.board)
    loadImages()
    running = True
    sqSelected = () #no square selected, keep track of the last click of the user (tuple: (row,col))
    playerClicks = [] #keep track of player clicks (two tuple: [(6,4),(4,4)])
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #get (x.y) location of mouse
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


"""
responsible for all the graphics withing a current game state.
"""


def drawGameState(screen, gs):
    drawBoard(screen)  # draw squares of the board
    drawPieces(screen, gs.board)  # draw pieces on top of the squares


"""
draw the squares on the board. the top left square is always light.
"""


def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece !=  "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE,SQ_SIZE))



if __name__ == "__main__":
    main()
