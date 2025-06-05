import pygame
import sys
import random
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
BOARD_SIZE = 4
TILE_SIZE = 100
MARGIN = 5
WINDOW_SIZE = BOARD_SIZE * (TILE_SIZE + MARGIN) + MARGIN
BACKGROUND_COLOR = (50, 50, 50)
TILE_COLOR = (100, 149, 237)  # Cornflower blue
TEXT_COLOR = (255, 255, 255)
EMPTY_TILE = BOARD_SIZE * BOARD_SIZE  # The value of the empty tile (16 in a 4x4 grid)

# Set up the window
WINDOW = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('15 Puzzle')
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont('Arial', 40, bold=True)

class SlidePuzzle:
    def __init__(self, board_size=BOARD_SIZE):
        self.board_size = board_size
        self.total_tiles = board_size * board_size
        self.board = list(range(1, self.total_tiles + 1))
        self.empty_pos = self.total_tiles - 1  # Last position (bottom right)
        self.solved_state = list(range(1, self.total_tiles + 1))
        
    def shuffle(self, moves=1000):
        """Shuffle the board by making random valid moves"""
        for _ in range(moves):
            possible_moves = self.get_possible_moves()
            if possible_moves:
                move = random.choice(possible_moves)
                self.move_tile(move)
        
        # Ensure the puzzle is solvable
        if not self.is_solvable():
            # Swap any two tiles to make it solvable
            if self.empty_pos != 0 and self.empty_pos != 1:
                self.board[0], self.board[1] = self.board[1], self.board[0]
            else:
                self.board[2], self.board[3] = self.board[3], self.board[2]
    
    def is_solvable(self):
        """Check if the current board configuration is solvable"""
        # Count inversions
        inversions = 0
        board_without_empty = [tile for tile in self.board if tile != self.total_tiles]
        
        for i in range(len(board_without_empty)):
            for j in range(i + 1, len(board_without_empty)):
                if board_without_empty[i] > board_without_empty[j]:
                    inversions += 1
        
        # For a 4x4 puzzle, if the empty tile is on an even row from the bottom and inversions is odd,
        # or if the empty tile is on an odd row from the bottom and inversions is even, the puzzle is solvable
        empty_row = self.empty_pos // self.board_size
        from_bottom = self.board_size - empty_row
        
        return (from_bottom % 2 == 0 and inversions % 2 == 1) or (from_bottom % 2 == 1 and inversions % 2 == 0)
    
    def get_possible_moves(self):
        """Get all possible positions that can be moved into the empty space"""
        possible_moves = []
        empty_row, empty_col = divmod(self.empty_pos, self.board_size)
        
        # Check all four directions
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        
        for d_row, d_col in directions:
            new_row, new_col = empty_row + d_row, empty_col + d_col
            
            # Check if the new position is within the board
            if 0 <= new_row < self.board_size and 0 <= new_col < self.board_size:
                move_pos = new_row * self.board_size + new_col
                possible_moves.append(move_pos)
                
        return possible_moves
    
    def move_tile(self, position):
        """Move a tile to the empty position if it's adjacent"""
        if position in self.get_possible_moves():
            # Swap the tile with the empty position
            self.board[self.empty_pos], self.board[position] = self.board[position], self.board[self.empty_pos]
            self.empty_pos = position
            return True
        return False
    
    def is_solved(self):
        """Check if the puzzle is solved"""
        return self.board == self.solved_state
    
    def get_tile_position(self, tile_value):
        """Get the position of a specific tile value"""
        return self.board.index(tile_value)

def draw_board(puzzle):
    """Draw the puzzle board on the screen"""
    WINDOW.fill(BACKGROUND_COLOR)
    
    for i in range(puzzle.total_tiles):
        tile_value = puzzle.board[i]
        
        if tile_value != EMPTY_TILE:  # Don't draw the empty tile
            row, col = divmod(i, puzzle.board_size)
            x = col * (TILE_SIZE + MARGIN) + MARGIN
            y = row * (TILE_SIZE + MARGIN) + MARGIN
            
            # Draw tile
            pygame.draw.rect(WINDOW, TILE_COLOR, (x, y, TILE_SIZE, TILE_SIZE))
            
            # Draw number
            text = FONT.render(str(tile_value), True, TEXT_COLOR)
            text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
            WINDOW.blit(text, text_rect)
    
    pygame.display.update()

def get_clicked_position(mouse_pos):
    """Convert mouse position to board position"""
    x, y = mouse_pos
    
    # Check if click is within the board
    if x < MARGIN or x >= WINDOW_SIZE - MARGIN or y < MARGIN or y >= WINDOW_SIZE - MARGIN:
        return None
    
    col = (x - MARGIN) // (TILE_SIZE + MARGIN)
    row = (y - MARGIN) // (TILE_SIZE + MARGIN)
    
    return row * BOARD_SIZE + col

def main():
    puzzle = SlidePuzzle()
    puzzle.shuffle()
    
    running = True
    game_won = False
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            if not game_won and event.type == MOUSEBUTTONDOWN:
                clicked_pos = get_clicked_position(pygame.mouse.get_pos())
                if clicked_pos is not None:
                    puzzle.move_tile(clicked_pos)
                    
                    if puzzle.is_solved():
                        game_won = True
            
            # Allow restarting with R key
            if event.type == KEYDOWN:
                if event.key == K_r:
                    puzzle = SlidePuzzle()
                    puzzle.shuffle()
                    game_won = False
        
        draw_board(puzzle)
        
        if game_won:
            # Display win message
            win_font = pygame.font.SysFont('Arial', 30, bold=True)
            win_text = win_font.render('Puzzle Solved! Press R to restart', True, (255, 215, 0))
            text_rect = win_text.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
            WINDOW.blit(win_text, text_rect)
            pygame.display.update()
        
        CLOCK.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
