import math
import copy
import time
import argparse

class MiniChess:
    def __init__(self):
        self.current_game_state = self.init_board()

    """
    Initialize the board

    Args:
        - None
    Returns:
        - state: A dictionary representing the state of the game
    """
    def init_board(self):
        state = {
                "board": 
                [['bK', 'bQ', 'bB', 'bN', '.'],
                ['.', '.', 'bp', 'bp', '.'],
                ['.', '.', '.', '.', '.'],
                ['.', 'wp', 'wp', '.', '.'],
                ['.', 'wN', 'wB', 'wQ', 'wK']],
                "turn": 'white',
                }
        return state

    """
    Prints the board
    
    Args:
        - game_state: Dictionary representing the current game state
    Returns:
        - None
    """
    def display_board(self, game_state):
        print()
        for i, row in enumerate(game_state["board"], start=1):
            print(str(6-i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        print()
        print("     A   B   C   D   E")
        print()

    """
    Check if the move is valid    
    
    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move which we check the validity of ((start_row, start_col),(end_row, end_col))
    Returns:
        - boolean representing the validity of the move
    """
    def is_valid_move(self, game_state, move):
        #checks if a move is valid by verifying piece movement rules and legality.
        start, end = move
        start_row, start_col = start
        end_row, end_col = end

        board = game_state["board"]
        piece = board[start_row][start_col]

        #ensure a piece is being moved
        if piece == '.':
            return False

        #ensure the piece belongs to the correct player
        piece_color = "white" if piece[0] == 'w' else "black"
        if piece_color != game_state["turn"]:
            return False

        #get all moves for this piece
        possible_moves = self.generate_moves_for_piece(piece, start, board)

        #check if the move is in the allowed moves
        return move in possible_moves


    """
    Returns a list of valid moves

    Args:
        - game_state:   dictionary | Dictionary representing the current game state
    Returns:
        - valid moves:   list | A list of nested tuples corresponding to valid moves [((start_row, start_col),(end_row, end_col)),((start_row, start_col),(end_row, end_col))]
    """
    def valid_moves(self, game_state):
        valid_moves_list = []
        board = game_state["board"]
        current_turn = game_state["turn"]
        
        for row in range(5):
            for col in range(5):
                piece = board[row][col]
                if piece == '.':
                    continue  #empty square, skip
                
                piece_color = "white" if piece[0] == 'w' else "black"
                
                if piece_color != current_turn:
                    continue  #skip opponent's pieces
                
                #generate possible moves based on piece type
                possible_moves = self.generate_moves_for_piece(piece, (row, col), board)
                
                valid_moves_list.extend(possible_moves)

        return valid_moves_list
    

    def generate_moves_for_piece(self, piece, position, board):
        #calls the appropriate movement function based on the piece type.
        row, col = position
        piece_type = piece[1]
        
        if piece_type == 'K':  # King
            return self.generate_king_moves(position)
        
        elif piece_type == 'Q':  # Queen
            return self.generate_queen_moves(position, board)
        
        elif piece_type == 'B':  # Bishop
            return self.generate_bishop_moves(position, board)
        
        elif piece_type == 'N':  # Knight
            return self.generate_knight_moves(position)
        
        elif piece_type == 'p':  # Pawn
            return self.generate_pawn_moves(piece, position, board)
        
        return []
    
    def generate_king_moves(self, position):
        #generates all valid king moves (one step in any direction).
        row, col = position
        moves = []

        directions = [(-1, -1), (-1, 0), (-1, 1), 
                  (0, -1),        (0, 1), 
                  (1, -1), (1, 0), (1, 1)]  #all 8 directions

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                moves.append(((row, col), (new_row, new_col)))

        return moves
    
    def generate_queen_moves(self, position, board):
        #generates all valid queen moves (combining rook and bishop moves).
        return self.generate_rook_moves(position, board) + self.generate_bishop_moves(position, board)
    

    def generate_rook_moves(self, position, board):
        #generates all valid rook moves (horizontal & vertical lines).
        row, col = position
        moves = []

        #rook moves: Up, Down, Left, Right
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 5 and 0 <= c < 5:  #stay within board boundaries
                if board[r][c] == '.':  #empty square → valid move
                    moves.append(((row, col), (r, c)))
                else:
                    if board[r][c][0] != board[row][col][0]:  #opponent piece → capture allowed
                        moves.append(((row, col), (r, c)))  
                    break  #stop if hitting any piece (cannot move past it)
                r += dr
                c += dc  #keep moving in the same direction

        return moves

    def generate_bishop_moves(self, position, board):
        #generates all valid bishop moves (diagonal only).
        row, col = position
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  #diagonal directions

        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 5 and 0 <= c < 5:
                if board[r][c] == '.':  
                    moves.append(((row, col), (r, c)))  #valid empty move
                else:
                    if board[r][c][0] != board[row][col][0]:  #opponent piece
                        moves.append(((row, col), (r, c)))  #capture allowed
                    break  #stop if any piece blocks the path
                r += dr
                c += dc

        return moves
    
    def generate_knight_moves(self, position):
        #generates all valid knight moves (L-shaped jumps).
        row, col = position
        moves = []

        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                moves.append(((row, col), (new_row, new_col)))

        return moves
    
    def generate_pawn_moves(self, piece, position, board):
        #generates all valid pawn moves (forward movement + diagonal capture).
        row, col = position
        moves = []
        direction = -1 if piece[0] == 'w' else 1  #white moves up, Black moves down

        #normal move forward (only if empty)
        if 0 <= row + direction < 5 and board[row + direction][col] == '.':
            moves.append(((row, col), (row + direction, col)))

        #diagonal captures
        for dc in [-1, 1]:  #left diagonal, right diagonal
            new_row, new_col = row + direction, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                if board[new_row][new_col] != '.' and board[new_row][new_col][0] != piece[0]:  #opponent piece
                    moves.append(((row, col), (new_row, new_col)))

        return moves




    """
    Modify to board to make a move

    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    Returns:
        - game_state:   dictionary | Dictionary representing the modified game state
    """
    def make_move(self, game_state, move):
        start = move[0]
        end = move[1]
        start_row, start_col = start
        end_row, end_col = end
        piece = game_state["board"][start_row][start_col]
        game_state["board"][start_row][start_col] = '.'
        if (game_state["board"][end_row][end_col] != '.'):
            turn_count = 0
        game_state["board"][end_row][end_col] = piece

        if piece[1] == 'p':  #if moving piece is a pawn
            if (piece[0] == 'w' and end_row == 0) or (piece[0] == 'b' and end_row == 4):  #promotion row
                game_state["board"][end_row][end_col] = piece[0] + 'Q'  #upgrade to Queen
        
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"

        return game_state

    """
    Parse the input string and modify it into board coordinates

    Args:
        - move: string representing a move "B2 B3"
    Returns:
        - (start, end)  tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    """
    def parse_input(self, move):
        try:
            start, end = move.split()
            start = (5-int(start[1]), ord(start[0].upper()) - ord('A'))
            end = (5-int(end[1]), ord(end[0].upper()) - ord('A'))
            return (start, end)
        except:
            return None

    """
    Game loop

    Args:
        - None
    Returns:
        - None
    """
    def play(self):
        print("Welcome to Mini Chess! Enter moves as 'B2 B3'. Type 'exit' to quit.")
        turn_count = 0
        while True:
            self.display_board(self.current_game_state)

            if self.is_game_over(self.current_game_state):
                break  #exit game if someone wins

            move = input(f"{self.current_game_state['turn'].capitalize()} to move: ")
            if move.lower() == 'exit':
                print("Game exited.")
                exit(1)

            move = self.parse_input(move)
            if not move or not self.is_valid_move(self.current_game_state, move):
                print("Invalid move. Try again.")
                continue

            self.make_move(self.current_game_state, move)
            turn_count += 1 #increment turn_count

            if turn_count >= 20:
                print("Draw! No captures have been made in 10 turns.")
                break

    def is_game_over(self, game_state):
        #checks if a King has been captured and determines the winner
        board = game_state["board"]
        white_king_exists = any('wK' in row for row in board)
        black_king_exists = any('bK' in row for row in board)

        if not white_king_exists:
            print("Black wins! White King has been captured.")
            return True
        elif not black_king_exists:
            print("White wins! Black King has been captured.")
            return True

        return False  #game continues

if __name__ == "__main__":
    game = MiniChess()
    game.play()