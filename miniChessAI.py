import math
import copy
import time
import argparse

class MiniChess:
    def __init__(self, max_time=5.0, max_turns=100, use_alpha_beta=True, play_mode="H-H", heuristic="e0"):
        self.current_game_state = self.init_board()
        self.max_time = max_time  #maximum time allowed for AI move in seconds
        self.use_alpha_beta = use_alpha_beta  #whether to use alpha-beta pruning
        self.play_mode = play_mode  # H-H, H-AI, AI-H, AI-AI
        self.heuristic = heuristic  # e0, e1, e2
        self.turn_number = 1  #counter to track full turns in the game
        self.no_capture_count = 0  #counter to track half-moves without captures

        # Statistics tracking for AI
        self.states_explored = 0
        self.states_by_depth = {}
        self.total_branches = 0  #for calculating average branching factor
        self.total_nodes = 0  #for calculating average branching factor
    
        #output file setup
        alpha_beta_str = "true" if use_alpha_beta else "false"
        self.output_file = f"gameTrace-{alpha_beta_str}-{max_time}-{max_turns}.txt"

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
        #end_row, end_col = end

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
    """
    

    def generate_moves_for_piece(self, piece, position, board):
        #calls the appropriate movement function based on the piece type.
        piece_type = piece[1]
        
        if piece_type == 'K':  # King
            return self.generate_king_moves(position, board)
        
        elif piece_type == 'Q':  # Queen
            return self.generate_queen_moves(position, board)
        
        elif piece_type == 'B':  # Bishop
            return self.generate_bishop_moves(position, board)
        
        elif piece_type == 'N':  # Knight
            return self.generate_knight_moves(position, board)
        
        elif piece_type == 'p':  # Pawn
            return self.generate_pawn_moves(piece, position, board)
        
        return []
    
    def generate_king_moves(self, position, board):
        #generates all valid king moves (one step in any direction)
        row, col = position
        moves = []
        piece_color = board[row][col][0]  #get piece color from the board

        directions = [(-1, -1), (-1, 0), (-1, 1), 
                    (0, -1),           (0, 1), 
                    (1, -1),  (1, 0),  (1, 1)]  #all 8 directions

        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                #check if the destination is empty or has an opponent's piece
                target = board[new_row][new_col]
                if target == '.' or target[0] != piece_color:
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
    
    def generate_knight_moves(self, position, board):
        #generates all valid knight moves (L-shaped jumps)
        row, col = position
        moves = []
        piece_color = board[row][col][0]  #get piece color from the board

        knight_moves = [
            (-2, -1), (-2, 1), (2, -1), (2, 1),
            (-1, -2), (-1, 2), (1, -2), (1, 2)
        ]

        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            #check if the move is on the board
            if 0 <= new_row < 5 and 0 <= new_col < 5:
                #check if the destination is empty or has an opponent's piece
                target = board[new_row][new_col]
                if target == '.' or target[0] != piece_color:
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
    def make_move(self, game_state, move, is_real_move = True):
        #create a copy to avoid modifying the original
        new_state = copy.deepcopy(game_state)

        start = move[0]
        end = move[1]
        start_row, start_col = start
        end_row, end_col = end
        piece = new_state["board"][start_row][start_col]
        new_state["board"][start_row][start_col] = '.'

        #check if a capture was made
        was_capture = new_state["board"][end_row][end_col] != '.'
        
        #only update the counter for real moves, not during search
        if is_real_move:
            if was_capture:
                self.no_capture_count = 0  #reset counter if a capture was made
            else:
                self.no_capture_count += 1  #increment counter if no capture
            
        new_state["board"][end_row][end_col] = piece

        if piece[1] == 'p':  #if moving piece is a pawn
            if (piece[0] == 'w' and end_row == 0) or (piece[0] == 'b' and end_row == 4):  #promotion row
                new_state["board"][end_row][end_col] = piece[0] + 'Q'  #upgrade to Queen
        
        new_state["turn"] = "black" if new_state["turn"] == "white" else "white"

        return new_state

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
        
    def format_coord(self, coord):

        row, col = coord
        col_letter = chr(col + ord('A'))  #convert column number to letter
        row_number = 5 - row              #convert row number to chess notation
        return f"{col_letter}{row_number}"
        
    def write_game_parameters(self):
        with open(self.output_file, "w") as file:
            #game parameters
            file.write("Game Parameters:\n")
            
            #timeout value
            file.write(f"a) Timeout: {self.max_time} seconds\n")
            
            #max number of turns for draw (20 half-moves = 10 full turns)
            file.write(f"b) Max turns for draw: 10 (20 half-moves)\n")
            
            #play modes
            file.write(f"c) Play mode: {self.play_mode}\n")
            
            #alpha-beta setting (if AI is involved)
            if "AI" in self.play_mode:
                file.write(f"d) Alpha-beta: {'on' if self.use_alpha_beta else 'off'}\n")
            
            #heuristic used (if AI is involved)
            if "AI" in self.play_mode:
                file.write(f"e) Heuristic: {self.heuristic}\n")
            
            #initial board configuration
            file.write("\nInitial board configuration:\n")
            for i, row in enumerate(self.current_game_state["board"]):
                file.write(f"{5-i}  {' '.join(piece.rjust(2) for piece in row)}\n")
            file.write("\n   A  B  C  D  E\n\n")

    def log_move(self, move, player_color, time_taken=None, heuristic_score=None, search_score=None):
        
        start_notation = self.format_coord(move[0])
        end_notation = self.format_coord(move[1])

        current_state = self.current_game_state

        
        with open(self.output_file, "a") as file:
            #log player and turn information
            file.write(f"\n{player_color.capitalize()} (Turn #{self.turn_number})\n")
            file.write(f"Move: from {start_notation} to {end_notation}\n")
            
            #log AI-specific information if this is an AI move
            if time_taken is not None:
                file.write(f"Time for this action: {time_taken:.2f} sec\n")
            
            if heuristic_score is not None:
                file.write(f"Heuristic score: {heuristic_score}\n")
            
            if search_score is not None:
                algorithm = "alpha-beta" if self.use_alpha_beta else "minimax"
                file.write(f"{algorithm} search score: {search_score}\n")
            
            #log the updated board state
            file.write("\nBoard configuration:\n")
            for i, row in enumerate(current_state["board"]):
                file.write(f"{5-i}  {' '.join(piece.rjust(2) for piece in row)}\n")
            file.write("\n   A  B  C  D  E\n\n")
            
            #log AI statistics if this is an AI move
            if time_taken is not None:
                file.write(f"Cumulative states explored: {self.states_explored}\n")
                
                #states explored by depth
                depth_stats = []
                for depth, count in sorted(self.states_by_depth.items()):
                    if count > 0:
                        depth_stats.append(f"{depth}={count}")
                
                if depth_stats:
                    file.write(f"Cumulative states explored by depth: {' '.join(depth_stats)}\n")


    def minimax(self, game_state, depth, maximizing_player, start_time):

        if time.time() - start_time > self.max_time:
            return 0, None
        
        #update statistics
        self.states_explored += 1
        
        #initialize depth in stats
        if depth not in self.states_by_depth:
            self.states_by_depth[depth] = 0
        self.states_by_depth[depth] += 1
        
        #check if the game is over
        is_over, winner = self.is_game_over(game_state)
        if is_over:
            if winner is None:  #draw
                return 0, None
            elif winner == "white":
                return 1000, None  #white wins
            else:  #black wins
                return -1000, None
        
        #if maximum depth reached, evaluate the board
        if depth == 0:
            return self.evaluate_board(game_state), None
        
        #if it's white's turn and we're maximizing
        current_player = "white" if maximizing_player else "black"
        temp_state = copy.deepcopy(game_state)
        temp_state["turn"] = current_player
        
        #get all valid moves
        all_moves = self.valid_moves(temp_state)
        
        #track branching factor
        self.total_branches += len(all_moves)
        self.total_nodes += 1
        
        if maximizing_player:
            max_score = float('-inf')
            best_move = None
            
            for move in all_moves:
                #make the move
                new_state = copy.deepcopy(temp_state)
                self.make_move(new_state, move, False)
                
                #recursive minimax call
                score, _ = self.minimax(new_state, depth - 1, False, start_time)
                
                if score > max_score:
                    max_score = score
                    best_move = move
                    
            return max_score, best_move
        else:
            min_score = float('inf')
            best_move = None
            
            for move in all_moves:
                #make the move
                new_state = copy.deepcopy(temp_state)
                self.make_move(new_state, move, False)
                
                #recursive minimax call
                score, _ = self.minimax(new_state, depth - 1, True, start_time)
                
                if score < min_score:
                    min_score = score
                    best_move = move
                    
            return min_score, best_move
        
    def alpha_beta(self, game_state, depth, alpha, beta, maximizing_player, start_time):

        if time.time() - start_time > self.max_time:
            return 0, None
        
        #update statistics
        self.states_explored += 1
        
        #initialize depth in stats
        if depth not in self.states_by_depth:
            self.states_by_depth[depth] = 0
        self.states_by_depth[depth] += 1
        
        #check if the game is over
        is_over, winner = self.is_game_over(game_state)
        if is_over:
            if winner is None:  #draw
                return 0, None
            elif winner == "white":
                return 1000, None  #white wins
            else:  #black wins
                return -1000, None
        
        #if maximum depth reached, evaluate the board
        if depth == 0:
            return self.evaluate_board(game_state), None
        
        #if it's white's turn and we're maximizing
        current_player = "white" if maximizing_player else "black"
        temp_state = copy.deepcopy(game_state)
        temp_state["turn"] = current_player
        
        #get all valid moves
        all_moves = self.valid_moves(temp_state)
        
        #track branching factor
        self.total_branches += len(all_moves)
        self.total_nodes += 1
        
        if maximizing_player:
            max_score = float('-inf')
            best_move = None
            
            for move in all_moves:
                #make the move
                new_state = copy.deepcopy(temp_state)
                self.make_move(new_state, move, False)
                
                #recursive alpha-beta call
                score, _ = self.alpha_beta(new_state, depth - 1, alpha, beta, False, start_time)
                
                if score > max_score:
                    max_score = score
                    best_move = move
                    
                alpha = max(alpha, max_score)
                if beta <= alpha:
                    break  #beta cutoff
                    
            return max_score, best_move
        else:
            min_score = float('inf')
            best_move = None
            
            for move in all_moves:
                #make the move
                new_state = copy.deepcopy(temp_state)
                self.make_move(new_state, move, False)
                
                #recursive alpha-beta call
                score, _ = self.alpha_beta(new_state, depth - 1, alpha, beta, True, start_time)
                
                if score < min_score:
                    min_score = score
                    best_move = move
                    
                beta = min(beta, min_score)
                if beta <= alpha:
                    break  #alpha cutoff
                    
            return min_score, best_move
        
    def ai_move(self):
        #reset statistics
        self.states_explored = 0
        self.states_by_depth = {}
        self.total_branches = 0
        self.total_nodes = 0
        
        start_time = time.time()
        depth = 1
        best_move = None
        best_score = None
        
        #iterative deepening
        while True:
            #check if we have time for another iteration
            current_time = time.time()
            if current_time - start_time > self.max_time * 0.7:  #use 70% of allocated time
                break
                
            #choose search method based on settings
            if self.use_alpha_beta:
                score, move = self.alpha_beta(self.current_game_state, depth, float('-inf'), float('inf'), self.current_game_state["turn"] == "white", start_time)
            else:
                score, move = self.minimax(self.current_game_state, depth, self.current_game_state["turn"] == "white", start_time)
            
            #update best move if found
            if move is not None:
                best_move = move
                best_score = score
            
            #increase depth for next iteration
            depth += 1
            
            #break if time is almost up
            if time.time() - start_time > self.max_time * 0.8:
                break
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if best_move is None:
            #fallback: choose a random valid move
            print("Warning: AI could not find a move in time or no valid moves available.")
            valid_moves = self.valid_moves(self.current_game_state)
            if valid_moves:
                best_move = valid_moves[0]
                best_score = 0
            else:
                print("No valid moves available for AI. Stalemate or checkmate.")
                return None, elapsed_time, None, None
        
        heuristic_score = self.evaluate_board(self.current_game_state)
        
        #print info to console
        if best_move is not None:
            print(f"AI move: {self.format_coord(best_move[0])} to {self.format_coord(best_move[1])}")
        else:
            print("AI could not make a move.")
        print(f"Time taken: {elapsed_time:.3f} seconds")
        print(f"Search depth: {depth-1}")
        print(f"States explored: {self.states_explored}")

        return best_move, elapsed_time, heuristic_score, best_score
    
    def evaluate_board(self, game_state):
        board = game_state["board"]

        #position tables for each piece type
        pawn_table = [
            [0.0, 0.0, 0.0, 0.0, 0.0],   # Row 0 (top) - promotion row for white
            [2.0, 2.0, 2.5, 2.0, 2.0],   # Row 1 - near promotion
            [1.0, 1.2, 1.5, 1.2, 1.0],   # Row 2
            [0.5, 0.6, 0.8, 0.6, 0.5],   # Row 3
            [0.0, 0.0, 0.0, 0.0, 0.0]    # Row 4 (bottom)
        ]

        knight_table = [
            [0.0, 0.5, 1.0, 0.5, 0.0],
            [0.5, 1.0, 1.5, 1.0, 0.5],
            [1.0, 1.5, 2.0, 1.5, 1.0],
            [0.5, 1.0, 1.5, 1.0, 0.5],
            [0.0, 0.5, 1.0, 0.5, 0.0]
        ]

        bishop_table = [
            [0.5, 0.0, 0.0, 0.0, 0.5],   #bishops better on diagonals
            [0.0, 1.0, 0.5, 1.0, 0.0],
            [0.0, 0.5, 1.0, 0.5, 0.0],
            [0.0, 1.0, 0.5, 1.0, 0.0],
            [0.5, 0.0, 0.0, 0.0, 0.5]
        ]

        queen_table = [
            [0.0, 0.2, 0.2, 0.2, 0.0],
            [0.2, 0.5, 0.5, 0.5, 0.2],   #queen better in center
            [0.2, 0.5, 1.0, 0.5, 0.2],
            [0.2, 0.5, 0.5, 0.5, 0.2],
            [0.0, 0.2, 0.2, 0.2, 0.0]
        ]

        king_table = [
            [0.5, 0.0, 0.0, 0.0, 0.5],   #king safer on edges in this small board
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 0.0, 0.0, 0.0, 0.5]
        ]
        


        #count pieces
        white_p = black_p = 0  # pawns
        white_B = black_B = 0  # bishops
        white_N = black_N = 0  # knights
        white_Q = black_Q = 0  # queens
        white_K = black_K = 0  # kings

        #position scores
        white_position = 0
        black_position = 0
        
         #count pieces and calculate position scores
        for row in range(5):
            for col in range(5):
                piece = board[row][col]
                if piece == '.':
                    continue
                    
                #count pieces
                if piece == 'wp': 
                    white_p += 1
                    white_position += pawn_table[row][col]
                elif piece == 'wB': 
                    white_B += 1
                    white_position += bishop_table[row][col]
                elif piece == 'wN': 
                    white_N += 1
                    white_position += knight_table[row][col]
                elif piece == 'wQ': 
                    white_Q += 1
                    white_position += queen_table[row][col]
                elif piece == 'wK': 
                    white_K += 1
                    white_position += king_table[row][col]
                elif piece == 'bp': 
                    black_p += 1
                    black_position += pawn_table[4-row][col]  #flip for black
                elif piece == 'bB': 
                    black_B += 1
                    black_position += bishop_table[4-row][col]
                elif piece == 'bN': 
                    black_N += 1
                    black_position += knight_table[4-row][col]
                elif piece == 'bQ': 
                    black_Q += 1
                    black_position += queen_table[4-row][col]
                elif piece == 'bK': 
                    black_K += 1
                    black_position += king_table[4-row][col]

        white_material = (white_p + 3*white_B + 3*white_N + 9*white_Q + 999*white_K)
        black_material = (black_p + 3*black_B + 3*black_N + 9*black_Q + 999*black_K)

        #e0
        if self.heuristic == "e0":
            # e0 = (#wp + 3·#wB + 3·#wN + 9·#wQ + 999·wK) − (#bp + 3·#bB + 3·#bN + 9·#bQ + 999·bK)
            return white_material - black_material
        
        #e1 -  material + piece positioning
        elif self.heuristic == "e1":
            white_score = white_material + white_position
            black_score = black_material + black_position
            
            return white_score - black_score
        
        #e2 - material + position + piece safety
        elif self.heuristic == "e2":
            white_score = white_material + white_position
            black_score = black_material + black_position

            #piece safety - penalize undefended pieces
            white_attacked = 0
            black_attacked = 0
            
            #temporarily switch turn to check attacks
            temp_state = copy.deepcopy(game_state)
            
            #check black attacks on white pieces
            temp_state["turn"] = "black"
            black_moves = self.valid_moves(temp_state)
            black_attack_squares = set()
            
            for move in black_moves:
                _, end = move
                black_attack_squares.add(end)
                
                #check if a white piece is under attack
                end_row, end_col = end
                if board[end_row][end_col] != '.' and board[end_row][end_col][0] == 'w':
                    piece_type = board[end_row][end_col][1]
                    if piece_type == 'p': white_attacked += 1
                    elif piece_type in ['B', 'N']: white_attacked += 3
                    elif piece_type == 'Q': white_attacked += 9
                    elif piece_type == 'K': white_attacked += 50
            
            #check white attacks on black pieces
            temp_state["turn"] = "white"
            white_moves = self.valid_moves(temp_state)
            white_attack_squares = set()
            
            for move in white_moves:
                _, end = move
                white_attack_squares.add(end)
                
                #check if a black piece is under attack
                end_row, end_col = end
                if board[end_row][end_col] != '.' and board[end_row][end_col][0] == 'b':
                    piece_type = board[end_row][end_col][1]
                    if piece_type == 'p': black_attacked += 1
                    elif piece_type in ['B', 'N']: black_attacked += 3
                    elif piece_type == 'Q': black_attacked += 9
                    elif piece_type == 'K': black_attacked += 50
            
            #adjust scores based on piece safety
            white_score -= white_attacked * 0.5  #penalize having pieces under attack
            black_score -= black_attacked * 0.5

            return white_score - black_score
            
        #default to e0 if invalid heuristic
        white_score = (white_p + 3*white_B + 3*white_N + 9*white_Q + 999*white_K)
        black_score = (black_p + 3*black_B + 3*black_N + 9*black_Q + 999*black_K)
        return white_score - black_score
    

    """
    Game loop

    Args:
        - None
    Returns:
        - None
    """
    def play(self):
        #rite game parameters and initial state to file
        self.write_game_parameters()
        
        #determine which players are AI
        player1_is_ai = self.play_mode in ["AI-H", "AI-AI"]
        player2_is_ai = self.play_mode in ["H-AI", "AI-AI"]
        
        #main game loop
        game_over = False
        self.turn_number = 1
        self.no_capture_count = 0
        
        while not game_over:
            self.display_board(self.current_game_state)
            current_player = self.current_game_state["turn"]
            
            print(f"\n{current_player.capitalize()}'s turn (Turn #{self.turn_number})")
            
            #check if current player is AI
            is_ai_turn = (current_player == "white" and player1_is_ai) or (current_player == "black" and player2_is_ai)
            
            if is_ai_turn:
                #AI's turn
                print(f"AI ({current_player}) is thinking...")
                move, elapsed_time, heuristic_score, best_score = self.ai_move()
    
                #apply and log move
                self.current_game_state = self.make_move(self.current_game_state, move, True)
                self.log_move(move, current_player, elapsed_time, heuristic_score, best_score)
            else:
                #human's turn
                while True:
                    move_str = input(f"Enter your move (e.g. B2 B3) or 'exit' to quit: ")
                    
                    if move_str.lower() == 'exit':
                        print("Game exited.")
                        return
                    
                    move = self.parse_input(move_str)
                    if move is None:
                        print("Invalid move format. Please use format like 'B2 B3'.")
                        continue
                    
                    if not self.is_valid_move(self.current_game_state, move):
                        print("Invalid move. Please try again.")
                        continue
                    break
                #make the move
                self.current_game_state = self.make_move(self.current_game_state, move, True)
                #log human move
                self.log_move(move, current_player)
            
            
            
            #check if game is over
            is_over, winner = self.is_game_over(self.current_game_state)
            if is_over:
                self.display_board(self.current_game_state)
                if winner is None:
                    # Draw
                    print(f"\nDraw! No pieces have been captured in 20 moves.")
                    
                    # Log draw
                    with open(self.output_file, "a") as file:
                        file.write(f"\nDraw after {self.turn_number} turns (no captures in 20 moves)\n")
                else:
                    # Someone won
                    print(f"\n{winner.capitalize()} wins in {self.turn_number} turns!")
                    
                    # Log final result
                    with open(self.output_file, "a") as file:
                        file.write(f"\n{winner.capitalize()} won in {self.turn_number} turns\n")
                        
                game_over = True
            
            #increment turn number if it's white's turn next
            if self.current_game_state["turn"] == "white":
                self.turn_number += 1


    def check_for_draw(self):
        return self.no_capture_count >= 20  #20 half-moves (10 full turns)
    

    def is_game_over(self, game_state):
        board = game_state["board"]
        
        #check if kings exist
        white_king_exists = any('wK' in row for row in board)
        black_king_exists = any('bK' in row for row in board)
        
        #if white king is captured, black wins
        if not white_king_exists:
            return True, "black"
            
        #if black king is captured, white wins
        if not black_king_exists:
            return True, "white"
        
        #check for draw
        if self.check_for_draw():
            return True, None
        
        #game is not over
        return False, None

if __name__ == "__main__":
    print("Welcome to Mini Chess!")
    print("Configure your game settings.\n")
    
    #configure play mode
    print("Available play modes:")
    print("1. Human vs Human (H-H)")
    print("2. Human vs AI (H-AI)")
    print("3. AI vs Human (AI-H)")
    print("4. AI vs AI (AI-AI)")
    
    while True:
        mode_choice = input("Enter your choice (1-4): ")
        if mode_choice in ["1", "2", "3", "4"]:
            break
        print("Invalid choice. Please enter a number between 1 and 4.")
    
    mode_map = {
        "1": "H-H", 
        "2": "H-AI", 
        "3": "AI-H", 
        "4": "AI-AI"
    }
    play_mode = mode_map[mode_choice]
    
    #only ask for AI settings if AI is involved
    max_time = 5.0
    use_alpha_beta = True
    heuristic = "e0"
    
    if play_mode != "H-H":
        print("\nAI Configuration:")
        
        #configure time limit
        while True:
            time_input = input("Enter maximum thinking time for AI (in seconds, recommended 1-10): ")
            try:
                max_time = float(time_input)
                if max_time > 0:
                    break
                print("Time must be greater than 0.")
            except ValueError:
                print("Please enter a valid number.")
        
        #configure alpha-beta
        while True:
            ab_input = input("Use alpha-beta pruning? (y/n): ").lower()
            if ab_input in ["y", "n", "yes", "no"]:
                use_alpha_beta = ab_input.startswith("y")
                break
            print("Please enter 'y' or 'n'.")
        
        #configure heuristic
        print("\nAvailable heuristics:")
        print("1. e0 - Basic material evaluation")
        print("2. e1 - Material + mobility + pawn advancement")
        print("3. e2 - Advanced evaluation (material, piece activity, center control, king safety)")
        
        while True:
            heuristic_choice = input("Choose a heuristic (1-3): ")
            if heuristic_choice in ["1", "2", "3"]:
                heuristic = "e" + str(int(heuristic_choice) - 1)
                break
            print("Invalid choice. Please enter a number between 1 and 3.")
    
    #display selected settings
    print("\nSelected Settings:")
    print(f"Play Mode: {play_mode}")
    
    if play_mode != "H-H":
        print(f"AI Thinking Time: {max_time} seconds")
        print(f"Alpha-Beta Pruning: {'Enabled' if use_alpha_beta else 'Disabled'}")
        print(f"Heuristic: {heuristic}")
    
    #confirm settings
    confirm = input("\nStart game with these settings? (y/n): ").lower()
    if not confirm.startswith("y"):
        print("Game setup cancelled. Please run the program again to configure.")
        exit(1)
    
    #create and run the game
    game = MiniChess(
        max_time=max_time,
        use_alpha_beta=use_alpha_beta,
        play_mode=play_mode,
        heuristic=heuristic
    )

    game.play()