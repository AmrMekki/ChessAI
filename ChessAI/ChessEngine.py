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
            ["--", "--", "--", "--", "--", "--", "--", "--"],
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
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        self.enPassantPossible = ()  # coordinates for the square where an en passant capture is possible

    """
    Takes a Move as parameter and executes it (this will not work for castling, pawn promotion, and en-passant.
    """

    def makeMove(self, move):
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.board[move.startRow][move.startCol] = "--"
        self.moveLog.append(move)  # log the move so we can undo later
        self.whiteToMove = not self.whiteToMove
        # update the king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        # if pawn moves twice, next move can capture enpassant
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enPassantPossible = ((move.endRow + move.startRow) // 2, move.endCol)
        else:
            self.enPassantPossible = ()

        # if en passant move, must update the board to capture the pawn
        if move.enPassant:
            self.board[move.startRow][move.endCol] = "--"
        # if pawn promotion change piece
        if move.pawnPromotion:
            promotedPiece = input("Promote to Q, R, B, or N:")  # we can make this part of the ui later
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

    """
    Undo last move
    """

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved  # put piece on starting square
            self.board[move.endRow][move.endCol] = move.pieceCaptured  # put back captured piece
            self.whiteToMove = not self.whiteToMove  # switch turns back
            # update king's position if needed
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant is different
            if move.enPassant:
                self.board[move.endRow][move.endCol] = "--"  # removes the pawn that was added in the wrong square
                self.board[move.startRow][
                    move.endCol] = move.pieceCaptured  # puts the pawn back on the correct square it was captured from
                self.enPassantPossible = (move.endRow, move.endCol)  # allow an en passant to happen on the next move
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enPassantPossible = ()

    """
    All moves considering checks
    """

    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block a check you must move a piece into one of the squares between the enemy piece and king
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []  # squares that pieces can move to
                # if knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i,
                                       kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        # once you get to piece end checks
                        # print(check[2])
                        # print(check[3])
                        # print(i)
                        # print(validSquares)
                        # print(validSquare)
                        # print(checkRow)
                        # print(checkCol)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                # get rid of any moves that don't block check or move king
                # go through backwards when you are removing from a list as iterating
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':  # move doesn't move king, so it must block or capture
                        if not (moves[i].endRow,
                                moves[i].endCol) in validSquares:  # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMove(kingRow, kingCol, moves)
        else:  # not in check so all moves are fine
            moves = self.getAllPossibleMoves()

        return moves

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
                    self.moveFunctions[piece](r, c, moves)
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add these moves to list
    """

    def getPawnsMove(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            backRow = 0
            enemyColor = 'b'
        else:
            moveAmount = 1
            startRow = 1
            backRow = 7
            enemyColor = 'w'
        pawnPromotion = False

        if self.board[r + moveAmount][c] == "--":  # 1 square move
            if not piecePinned or pinDirection == (moveAmount, 0):
                if r + moveAmount == backRow:  # if piece gets to back rank then it is a pawn promotoion
                    pawnPromotion = True
                moves.append(Move((r, c), (r + moveAmount, c), self.board, pawnPromotion=pawnPromotion))
                if r == startRow and self.board[r + 2 * moveAmount][c] == "--":  # 2 square moves
                    moves.append(Move((r, c), (r + 2 * moveAmount, c), self.board))
        if c - 1 > 0:  # capture to left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[r + moveAmount][c - 1][0] == enemyColor:
                    if r + moveAmount == backRow:  # if piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c - 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c - 1), self.board, enPassant=True))
        if c + 1 <= 7:  # capture to right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[r + moveAmount][c + 1][0] == enemyColor:
                    if r + moveAmount == backRow:  # if piece gets to back rank then it is a pawn promotion
                        pawnPromotion = True
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, pawnPromotion=pawnPromotion))
                if (r + moveAmount, c + 1) == self.enPassantPossible:
                    moves.append(Move((r, c), (r + moveAmount, c + 1), self.board, enPassant=True))

    """
    Get all the rook moves for the rook located at row, col and add these moves to list
    """

    def getRookMove(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from pin on rook moves, only remove it on bishop moves
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece is valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:  # off board
                    break

    """
    Get all the knight moves for the knight located at row, col and add these moves to list
    """

    def getKnightMove(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # not an ally piece (empty or enemy)
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get all the bishop moves for the bishop located at row, col and add these moves to list
    """

    def getBishopMove(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        direction = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in direction:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:  # enemy piece is valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:  # friendly piece invalid
                            break
                else:  # off board
                    break

    """
    Get all the queen moves for the queen located at row, col and add these moves to list
    """

    def getQueenMove(self, r, c, moves):
        self.getRookMove(r, c, moves)
        self.getBishopMove(r, c, moves)

    """
    Get all the king moves for the king located at row, col and add these moves to list
    """

    def getKingMove(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[0]
            endCol = c + colMoves[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece (empty or enemy)
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    """
    Returns if the player is in check, a list of pins, and a list of checks
    """

    def checkForPinsAndChecks(self):
        pins = []  # squares where the allied pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        typeOfPiece = endPiece[1]
                        # 5 possibilities here in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        # (this is necessary to prevent a king move to a square controlled by another king)
                        if (0 <= j <= 3 and typeOfPiece == "R") or \
                                (4 <= j <= 7 and typeOfPiece == "B") or \
                                (i == 1 and typeOfPiece == 'p' and
                                 ((enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or \
                                (typeOfPiece == "Q") or (i == 1 and typeOfPiece == "K"):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
            # check for knight checks
            knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
            for m in knightMoves:
                endRow = startRow + m[0]
                endCol = startCol + m[1]
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == enemyColor and endPiece[1] == "N":  # enemy knight attacking king
                        inCheck = True
                        checks.append((endRow, endCol, m[0], m[1]))
        return inCheck, pins, checks


class Move:
    # map keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassant=False, pawnPromotion=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.enPassant = enPassant
        self.pawnPromotion = pawnPromotion
        if enPassant:
            self.pieceCaptured = 'bp' if self.pieceMoved == 'wp' else 'wp'  # enpassant captures opposite colored pawn
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Overriding the equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __str__(self):
        return self.moveID

    def getChessNotation(self):
        # add to make this like real chess notation
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
