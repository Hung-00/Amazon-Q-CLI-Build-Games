import pygame
import sys
import numpy as np
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
BOARD_SIZE = 600
MARGIN = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
HIGHLIGHT_COLOR = (255, 255, 0, 128)  # Yellow with transparency

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Ultimate Tic-Tac-Toe')

# Fonts
title_font = pygame.font.SysFont('Arial', 48, bold=True)
game_font = pygame.font.SysFont('Arial', 36)
small_font = pygame.font.SysFont('Arial', 24)
tiny_font = pygame.font.SysFont('Arial', 18)

class UltimateTicTacToe:
    def __init__(self):
        # Initialize the game state
        # 0 = empty, 1 = X, 2 = O
        self.big_board = np.zeros((3, 3), dtype=int)  # Tracks wins in each small board
        self.small_boards = np.zeros((3, 3, 3, 3), dtype=int)  # All small boards
        self.current_player = 1  # X starts
        self.active_board = None  # Which small board is active (None means player can choose)
        self.game_over = False
        self.winner = 0
        self.last_move = None
        
    def make_move(self, big_row, big_col, small_row, small_col):
        """Attempt to make a move at the specified position"""
        # Check if the game is over
        if self.game_over:
            return False
            
        # Check if the move is in the active board or if any board can be played
        if self.active_board is not None:
            active_row, active_col = self.active_board
            if active_row != big_row or active_col != big_col:
                return False
        
        # Check if the cell is empty
        if self.small_boards[big_row, big_col, small_row, small_col] != 0:
            return False
            
        # Make the move
        self.small_boards[big_row, big_col, small_row, small_col] = self.current_player
        self.last_move = (big_row, big_col, small_row, small_col)
        
        # Check if the small board is won
        if self.check_small_board_win(big_row, big_col):
            self.big_board[big_row, big_col] = self.current_player
            
        # Check if the game is won
        if self.check_big_board_win():
            self.game_over = True
            self.winner = self.current_player
        # Check if the game is a draw
        elif np.all(self.big_board != 0) or np.all(self.small_boards != 0):
            self.game_over = True
            self.winner = 0  # Draw
            
        # Determine the next active board
        next_board_row, next_board_col = small_row, small_col
        
        # If the next board is already won or full, player can choose any board
        if self.big_board[next_board_row, next_board_col] != 0 or \
           np.all(self.small_boards[next_board_row, next_board_col] != 0):
            self.active_board = None
        else:
            self.active_board = (next_board_row, next_board_col)
            
        # Switch player
        self.current_player = 3 - self.current_player  # Toggle between 1 and 2
        
        return True
        
    def check_small_board_win(self, big_row, big_col):
        """Check if a small board is won"""
        board = self.small_boards[big_row, big_col]
        
        # Check rows
        for row in range(3):
            if board[row, 0] != 0 and board[row, 0] == board[row, 1] == board[row, 2]:
                return True
                
        # Check columns
        for col in range(3):
            if board[0, col] != 0 and board[0, col] == board[1, col] == board[2, col]:
                return True
                
        # Check diagonals
        if board[0, 0] != 0 and board[0, 0] == board[1, 1] == board[2, 2]:
            return True
        if board[0, 2] != 0 and board[0, 2] == board[1, 1] == board[2, 0]:
            return True
            
        return False
        
    def check_big_board_win(self):
        """Check if the big board is won"""
        board = self.big_board
        
        # Check rows
        for row in range(3):
            if board[row, 0] != 0 and board[row, 0] == board[row, 1] == board[row, 2]:
                return True
                
        # Check columns
        for col in range(3):
            if board[0, col] != 0 and board[0, col] == board[1, col] == board[2, col]:
                return True
                
        # Check diagonals
        if board[0, 0] != 0 and board[0, 0] == board[1, 1] == board[2, 2]:
            return True
        if board[0, 2] != 0 and board[0, 2] == board[1, 1] == board[2, 0]:
            return True
            
        return False
        
    def is_board_full(self, big_row, big_col):
        """Check if a small board is full"""
        return np.all(self.small_boards[big_row, big_col] != 0)
        
    def reset(self):
        """Reset the game"""
        self.big_board = np.zeros((3, 3), dtype=int)
        self.small_boards = np.zeros((3, 3, 3, 3), dtype=int)
        self.current_player = 1
        self.active_board = None
        self.game_over = False
        self.winner = 0
        self.last_move = None

class GameRenderer:
    def __init__(self, game):
        self.game = game
        self.board_size = BOARD_SIZE
        self.margin = MARGIN
        self.big_cell_size = self.board_size // 3
        self.small_cell_size = self.big_cell_size // 3
        
    def draw_board(self):
        """Draw the entire game board"""
        screen.fill(WHITE)
        
        # Draw title
        title = title_font.render("Ultimate Tic-Tac-Toe", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Draw current player
        player_text = "Current Player: " + ("X" if self.game.current_player == 1 else "O")
        player_surface = game_font.render(player_text, True, 
                                         BLUE if self.game.current_player == 1 else RED)
        screen.blit(player_surface, (SCREEN_WIDTH // 2 - player_surface.get_width() // 2, 
                                    SCREEN_HEIGHT - 60))
        
        # Draw the big board outline
        pygame.draw.rect(screen, BLACK, 
                        (self.margin, self.margin, self.board_size, self.board_size), 3)
        
        # Draw the big board grid lines
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(screen, BLACK, 
                           (self.margin + i * self.big_cell_size, self.margin),
                           (self.margin + i * self.big_cell_size, self.margin + self.board_size),
                           3)
            # Horizontal lines
            pygame.draw.line(screen, BLACK, 
                           (self.margin, self.margin + i * self.big_cell_size),
                           (self.margin + self.board_size, self.margin + i * self.big_cell_size),
                           3)
        
        # Draw each small board
        for big_row in range(3):
            for big_col in range(3):
                self.draw_small_board(big_row, big_col)
                
        # Highlight the active board if there is one
        if self.game.active_board is not None:
            active_row, active_col = self.game.active_board
            highlight_surface = pygame.Surface((self.big_cell_size, self.big_cell_size), pygame.SRCALPHA)
            highlight_surface.fill(HIGHLIGHT_COLOR)
            screen.blit(highlight_surface, 
                      (self.margin + active_col * self.big_cell_size,
                       self.margin + active_row * self.big_cell_size))
                       
        # Draw game over message if applicable
        if self.game.game_over:
            self.draw_game_over()
            
    def draw_small_board(self, big_row, big_col):
        """Draw a small 3x3 board"""
        # Calculate the top-left corner of this small board
        start_x = self.margin + big_col * self.big_cell_size
        start_y = self.margin + big_row * self.big_cell_size
        
        # Draw the small board background based on its state
        if self.game.big_board[big_row, big_col] == 1:  # X won this board
            pygame.draw.rect(screen, (200, 200, 255),  # Light blue
                           (start_x, start_y, self.big_cell_size, self.big_cell_size))
        elif self.game.big_board[big_row, big_col] == 2:  # O won this board
            pygame.draw.rect(screen, (255, 200, 200),  # Light red
                           (start_x, start_y, self.big_cell_size, self.big_cell_size))
        elif self.game.is_board_full(big_row, big_col):  # Board is a draw
            pygame.draw.rect(screen, LIGHT_GRAY,
                           (start_x, start_y, self.big_cell_size, self.big_cell_size))
        
        # Draw the small board grid lines
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(screen, GRAY, 
                           (start_x + i * self.small_cell_size, start_y),
                           (start_x + i * self.small_cell_size, start_y + self.big_cell_size),
                           1)
            # Horizontal lines
            pygame.draw.line(screen, GRAY, 
                           (start_x, start_y + i * self.small_cell_size),
                           (start_x + self.big_cell_size, start_y + i * self.small_cell_size),
                           1)
        
        # Draw X's and O's in the small board
        for small_row in range(3):
            for small_col in range(3):
                cell_value = self.game.small_boards[big_row, big_col, small_row, small_col]
                if cell_value == 0:
                    continue
                    
                cell_x = start_x + small_col * self.small_cell_size + self.small_cell_size // 2
                cell_y = start_y + small_row * self.small_cell_size + self.small_cell_size // 2
                
                if cell_value == 1:  # X
                    self.draw_x(cell_x, cell_y, self.small_cell_size // 2 - 5)
                else:  # O
                    self.draw_o(cell_x, cell_y, self.small_cell_size // 2 - 5)
        
        # If this small board is won, draw a big X or O over it
        if self.game.big_board[big_row, big_col] != 0:
            center_x = start_x + self.big_cell_size // 2
            center_y = start_y + self.big_cell_size // 2
            
            if self.game.big_board[big_row, big_col] == 1:  # X
                self.draw_x(center_x, center_y, self.big_cell_size // 2 - 10, 5)
            else:  # O
                self.draw_o(center_x, center_y, self.big_cell_size // 2 - 10, 5)
                
    def draw_x(self, center_x, center_y, size, thickness=2):
        """Draw an X centered at (center_x, center_y)"""
        pygame.draw.line(screen, BLUE, 
                       (center_x - size, center_y - size),
                       (center_x + size, center_y + size),
                       thickness)
        pygame.draw.line(screen, BLUE, 
                       (center_x + size, center_y - size),
                       (center_x - size, center_y + size),
                       thickness)
                       
    def draw_o(self, center_x, center_y, size, thickness=2):
        """Draw an O centered at (center_x, center_y)"""
        pygame.draw.circle(screen, RED, 
                         (center_x, center_y),
                         size,
                         thickness)
                         
    def draw_game_over(self):
        """Draw the game over message"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        if self.game.winner == 0:
            message = "Game Over - It's a Draw!"
            color = YELLOW
        else:
            winner = "X" if self.game.winner == 1 else "O"
            message = f"Game Over - {winner} Wins!"
            color = BLUE if self.game.winner == 1 else RED
            
        text = title_font.render(message, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                         SCREEN_HEIGHT // 2 - 50))
                         
        restart = small_font.render("Press R to Restart", True, WHITE)
        screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + 20))
                            
    def get_board_position(self, mouse_pos):
        """Convert mouse position to board position"""
        x, y = mouse_pos
        
        # Check if click is within the board
        if x < self.margin or x >= self.margin + self.board_size or \
           y < self.margin or y >= self.margin + self.board_size:
            return None
            
        # Calculate big board position
        big_col = (x - self.margin) // self.big_cell_size
        big_row = (y - self.margin) // self.big_cell_size
        
        # Calculate small board position
        small_col = (x - self.margin - big_col * self.big_cell_size) // self.small_cell_size
        small_row = (y - self.margin - big_row * self.big_cell_size) // self.small_cell_size
        
        return (big_row, big_col, small_row, small_col)

def draw_instructions():
    """Draw the instructions screen"""
    screen.fill(WHITE)
    
    title = title_font.render("Ultimate Tic-Tac-Toe", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    instructions = [
        "How to Play:",
        "",
        "1. The board consists of 9 small tic-tac-toe boards arranged in a 3x3 grid.",
        "2. Win 3 small boards in a row to win the game.",
        "3. Your move determines which small board your opponent must play in next.",
        "4. If sent to a board that's already won or full, your opponent can play anywhere.",
        "5. The active board is highlighted in yellow.",
        "",
        "Click anywhere to start!"
    ]
    
    y_pos = 150
    for line in instructions:
        if line == "How to Play:":
            text = game_font.render(line, True, BLACK)
        else:
            text = small_font.render(line, True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
        y_pos += 40
    
    pygame.display.flip()
    
    # Wait for a click to start
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                waiting = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

def main():
    game = UltimateTicTacToe()
    renderer = GameRenderer(game)
    
    # Show instructions first
    draw_instructions()
    
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and not game.game_over:
                pos = renderer.get_board_position(event.pos)
                if pos:
                    big_row, big_col, small_row, small_col = pos
                    game.make_move(big_row, big_col, small_row, small_col)
            elif event.type == KEYDOWN:
                if event.key == K_r:  # Restart game
                    game.reset()
                elif event.key == K_ESCAPE:  # Quit game
                    running = False
        
        # Draw the board
        renderer.draw_board()
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
