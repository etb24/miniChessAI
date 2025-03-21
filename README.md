Mini Chess
A Python implementation of a 5x5 mini-chess game with AI capabilities using minimax algorithm and alpha-beta pruning.
Overview
Mini Chess is a simplified version of chess played on a 5x5 board with a reduced set of pieces. This implementation includes:

Complete game logic for all chess pieces
Different play modes: Human vs Human, Human vs AI, AI vs Human, and AI vs AI
AI powered by minimax algorithm with optional alpha-beta pruning
Multiple evaluation heuristics for the AI
Comprehensive game tracking and logging

Game Rules

The game is played on a 5x5 board
Pieces include: King (K), Queen (Q), Bishop (B), Knight (N), and Pawn (p)

Initial board configuration:

Copy4  bK  bQ  bB  bN   .
3   .   .  bp  bp   .
2   .   .   .   .   .
1   .  wp  wp   .   .
0   .  wN  wB  wQ  wK

   A   B   C   D   E

The goal is to capture the opponent's king
A draw occurs if no pieces are captured in 20 half-moves (10 full turns)
Pawns are automatically promoted to Queens upon reaching the opponent's back rank

Features

Multiple Play Modes:

Human vs Human (H-H)
Human vs AI (H-AI)
AI vs Human (AI-H)
AI vs AI (AI-AI)


AI Capabilities:

Configurable thinking time
Optional alpha-beta pruning for faster search
Iterative deepening for optimal move selection within time constraints
Statistics tracking (states explored, time taken, etc.)


Evaluation Heuristics:

e0: Basic material evaluation
e1: Material + piece positioning
e2: Advanced evaluation (material, positioning, piece safety)


Game Logging:

Detailed game trace files
Move history
AI statistics
Final game outcome



Installation
No external dependencies required. Simply download the Python file and run it with Python 3.

python mini_chess.py

How to Play

Run the program
Select your desired play mode (1-4)
If playing with AI, configure:

Maximum thinking time (in seconds)
Alpha-beta pruning (y/n)
Evaluation heuristic (1-3)


Enter moves in algebraic notation (e.g., "B2 B3" to move from B2 to B3)
Type "exit" at any point to quit the game

Move Notation
Moves are entered using algebraic notation with the format:

[starting square] [ending square]
Example: B2 B3 moves the piece at B2 to B3

The board coordinates are:
Copy4  A4  B4  C4  D4  E4
3  A3  B3  C3  D3  E3
2  A2  B2  C2  D2  E2
1  A1  B1  C1  D1  E1
0  A0  B0  C0  D0  E0

   A   B   C   D   E

Game Output
For each game played, a trace file is generated with the naming convention:
CopygameTrace-[alpha_beta]-[max_time]-[max_turns].txt
This file contains:

Initial game parameters
Board configuration at each turn
Moves made by each player
AI statistics (if applicable)
Final game outcome

Technical Details
AI Implementation
The AI uses the minimax algorithm with the following enhancements:

Alpha-beta pruning for more efficient search
Iterative deepening to ensure best move selection within time constraints
Three different evaluation heuristics

Piece Movement

King: One square in any direction
Queen: Any number of squares diagonally, horizontally, or vertically
Bishop: Any number of squares diagonally
Knight: L-shaped movement (2 squares in one direction, 1 square perpendicular)
Pawn: One square forward, captures diagonally forward

You can modify the evaluation heuristics or add new ones by editing the evaluate_board method in the code.
