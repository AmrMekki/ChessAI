"""
This class is responsible for storing all the information about the current state of a chess game. It will also be
responsible for determining the valid moves at the current state. It will also keep a move log.
"""


class GameState:
    def __init__(self):
        # board is a 8x8 2d list, each element of the list has 2 characters.
        # The first character represents the color of
        # The second character represents the of the piece 'b' or w piece 'K'
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "bp", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.getPawnsMove,
                              'R': self.getRookMove,
                              'N': self.getKnightMove,
                              'B': self.getBishopMove,
                              'Q': self.getQueenMove,
                              'K': self.getKingMove}
        self.whiteToMove = True
        self.moveLog = []

    """
    Takes a Move as parameter and executes it (this will not work for castling, pawn promotion, and en-passant.
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo later
        self.whiteToMove = not self.whiteToMove

    """
    Undo last move
    """

    def undoMove(self, move):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns

    def getValidMoves(self):
        return self.getAllPossibleMoves()  # for now, we will not worry about checks

    """
    All the moves without considering checks
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns
                turn = self.board[r][c][0]  # has either b or w or -
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]  # has name of piece
                    self.moveFunctions[piece](r,c,moves)
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add these moves to list
    """

    def getPawnsMove(self, r, c, moves):
        if self.whiteToMove:  # white pawns moves
            if self.board[r - 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:  # captures to the left
                if self.board[r - 1][c - 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
            if c + 1 < 7:  # captures to the right
                if self.board[r - 1][c + 1][0] == 'b':  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
        else: #black pawns moves
            if self.board[r + 1][c] == "--":  # 1 square pawn advance
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:  # captures to the left
                if self.board[r + 1][c - 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 < 7:  # captures to the right
                if self.board[r + 1][c + 1][0] == 'w':  # enemy piece to capture
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))

    """
    Get all the rook moves for the rook located at row, col and add these moves to list
    """
    def getRookMove(self, r, c, moves):
        if self.whiteToMove:
            if c + 1 < 7:  # to move to the right
                if self.board[r][c + 1] == "--" or self.board[r][c + 1][0] == 'b':
                    moves.append(Move((r,c), (r , c+1), self.board))

    """
    Get all the knight moves for the knight located at row, col and add these moves to list
    """
    def getKnightMove(self, r, c, moves):
        pass

    """
    Get all the bishop moves for the bishop located at row, col and add these moves to list
    """
    def getBishopMove(self, r, c, moves):
        pass

    """
    Get all the king moves for the king located at row, col and add these moves to list
    """
    def getKingMove(self, r, c, moves):
        pass


    """
    Get all the queen moves for the queen located at row, col and add these moves to list
    """
    def getQueenMove(self, r, c, moves):
        pass


class Move:
    # map keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding the equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        # add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
