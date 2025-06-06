import pygame
import sys
import random
import time
import numpy as np
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.font.init()

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700
BOARD_SIZE = 450
MARGIN = 50
CELL_SIZE = BOARD_SIZE // 9

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
YELLOW = (255, 255, 0)
HIGHLIGHT_COLOR = (240, 240, 150)  # Light yellow
ERROR_COLOR = (255, 200, 200)  # Light red
ORIGINAL_COLOR = (200, 200, 255)  # Light blue

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Ultimate Sudoku')

# Fonts
title_font = pygame.font.SysFont('Arial', 40, bold=True)
game_font = pygame.font.SysFont('Arial', 36)
cell_font = pygame.font.SysFont('Arial', 28, bold=True)
small_font = pygame.font.SysFont('Arial', 20)
note_font = pygame.font.SysFont('Arial', 12)

class SudokuGenerator:
    def __init__(self):
        self.board = None
        self.solution = None
        
    def generate_solution(self, grid):
        """Generate a complete Sudoku solution"""
        # Find an empty cell
        for i in range(9):
            for j in range(9):
                if grid[i][j] == 0:
                    # Try digits 1-9
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        # Check if valid
                        if self.is_valid(grid, i, j, num):
                            grid[i][j] = num
                            # Recursively try to solve
                            if self.generate_solution(grid):
                                return True
                            # If not solvable with this digit, backtrack
                            grid[i][j] = 0
                    # No valid digits found, need to backtrack
                    return False
        # No empty cells left, solution found
        return True
        
    def is_valid(self, grid, row, col, num):
        """Check if a number can be placed at the given position"""
        # Check row
        for x in range(9):
            if grid[row][x] == num:
                return False
                
        # Check column
        for x in range(9):
            if grid[x][col] == num:
                return False
                
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if grid[i][j] == num:
                    return False
                    
        return True
        
    def generate_puzzle(self, difficulty):
        """Generate a Sudoku puzzle with the given difficulty"""
        # Start with an empty grid
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Generate a complete solution
        self.generate_solution(self.board)
        
        # Save the solution
        self.solution = [row[:] for row in self.board]
        
        # Remove numbers based on difficulty
        # Easy: 35-40 clues (41-46 removed)
        # Medium: 30-34 clues (46-50 removed)
        # Hard: 25-29 clues (51-55 removed)
        # Expert: 20-24 clues (56-60 removed)
        
        if difficulty == "Easy":
            remove_count = random.randint(41, 46)
        elif difficulty == "Medium":
            remove_count = random.randint(46, 50)
        elif difficulty == "Hard":
            remove_count = random.randint(51, 55)
        else:  # Expert
            remove_count = random.randint(56, 60)
            
        # Remove numbers randomly
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        for i, j in cells[:remove_count]:
            self.board[i][j] = 0
            
        return self.board, self.solution

class SudokuGame:
    def __init__(self):
        self.generator = SudokuGenerator()
        self.board = None
        self.solution = None
        self.original = None  # To track original clues
        self.selected_cell = None
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.game_over = False
        self.start_time = None
        self.elapsed_time = 0
        self.difficulty = "Medium"
        self.mistakes = 0
        self.max_mistakes = 3
        self.note_mode = False
        self.show_conflicts = True
        
    def new_game(self, difficulty=None):
        """Start a new game with the given difficulty"""
        if difficulty:
            self.difficulty = difficulty
            
        self.board, self.solution = self.generator.generate_puzzle(self.difficulty)
        self.original = [[self.board[i][j] != 0 for j in range(9)] for i in range(9)]
        self.selected_cell = None
        self.notes = [[set() for _ in range(9)] for _ in range(9)]
        self.game_over = False
        self.start_time = time.time()
        self.elapsed_time = 0
        self.mistakes = 0
        
    def select_cell(self, row, col):
        """Select a cell on the board"""
        if 0 <= row < 9 and 0 <= col < 9:
            # Can't select original cells
            if not self.original[row][col]:
                self.selected_cell = (row, col)
            else:
                self.selected_cell = None
                
    def input_number(self, num):
        """Input a number in the selected cell"""
        if self.selected_cell and not self.game_over:
            row, col = self.selected_cell
            
            # Can't modify original cells
            if self.original[row][col]:
                return
                
            if self.note_mode:
                # Toggle note
                if num in self.notes[row][col]:
                    self.notes[row][col].remove(num)
                else:
                    self.notes[row][col].add(num)
            else:
                # Clear notes when inputting a number
                self.notes[row][col].clear()
                
                # Check if the move is correct
                if num != 0 and num != self.solution[row][col]:
                    self.mistakes += 1
                    if self.mistakes >= self.max_mistakes:
                        self.game_over = True
                        
                # Set the number
                self.board[row][col] = num
                
                # Check if the puzzle is solved
                if self.is_solved():
                    self.game_over = True
                    self.elapsed_time = time.time() - self.start_time
                    
    def clear_cell(self):
        """Clear the selected cell"""
        if self.selected_cell and not self.game_over:
            row, col = self.selected_cell
            if not self.original[row][col]:
                self.board[row][col] = 0
                self.notes[row][col].clear()
                
    def toggle_note_mode(self):
        """Toggle note mode"""
        self.note_mode = not self.note_mode
        
    def is_solved(self):
        """Check if the puzzle is solved"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] != self.solution[i][j]:
                    return False
        return True
        
    def get_conflicts(self, row, col):
        """Get cells that conflict with the given cell"""
        if self.board[row][col] == 0:
            return []
            
        conflicts = []
        num = self.board[row][col]
        
        # Check row
        for j in range(9):
            if j != col and self.board[row][j] == num:
                conflicts.append((row, j))
                
        # Check column
        for i in range(9):
            if i != row and self.board[i][col] == num:
                conflicts.append((i, col))
                
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.board[i][j] == num:
                    conflicts.append((i, j))
                    
        return conflicts
        
    def get_hint(self):
        """Get a hint for an empty or incorrect cell"""
        if self.game_over:
            return
            
        # Find cells that are empty or incorrect
        candidates = []
        for i in range(9):
            for j in range(9):
                if not self.original[i][j] and self.board[i][j] != self.solution[i][j]:
                    candidates.append((i, j))
                    
        if candidates:
            # Choose a random cell to give a hint for
            row, col = random.choice(candidates)
            self.board[row][col] = self.solution[row][col]
            self.notes[row][col].clear()
            
            # Select the cell to show the hint
            self.selected_cell = (row, col)

class GameRenderer:
    def __init__(self, game):
        self.game = game
        self.board_size = BOARD_SIZE
        self.margin = MARGIN
        self.cell_size = CELL_SIZE
        
    def draw_board(self):
        """Draw the entire game board"""
        screen.fill(WHITE)
        
        # Draw title
        title = title_font.render("Ultimate Sudoku", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))
        
        # Draw difficulty and mistakes
        diff_text = small_font.render(f"Difficulty: {self.game.difficulty}", True, BLACK)
        screen.blit(diff_text, (self.margin, self.margin - 30))
        
        mistake_text = small_font.render(f"Mistakes: {self.game.mistakes}/{self.game.max_mistakes}", True, RED)
        screen.blit(mistake_text, (SCREEN_WIDTH - self.margin - mistake_text.get_width(), self.margin - 30))
        
        # Draw timer
        if self.game.start_time:
            if self.game.game_over:
                elapsed = self.game.elapsed_time
            else:
                elapsed = time.time() - self.game.start_time
            minutes, seconds = divmod(int(elapsed), 60)
            time_text = small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
            screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, self.margin - 30))
        
        # Draw the board outline
        pygame.draw.rect(screen, BLACK, 
                        (self.margin, self.margin, self.board_size, self.board_size), 3)
        
        # Draw the grid lines
        for i in range(10):
            line_width = 3 if i % 3 == 0 else 1
            # Vertical lines
            pygame.draw.line(screen, BLACK, 
                           (self.margin + i * self.cell_size, self.margin),
                           (self.margin + i * self.cell_size, self.margin + self.board_size),
                           line_width)
            # Horizontal lines
            pygame.draw.line(screen, BLACK, 
                           (self.margin, self.margin + i * self.cell_size),
                           (self.margin + self.board_size, self.margin + i * self.cell_size),
                           line_width)
        
        # Draw the cells
        for row in range(9):
            for col in range(9):
                self.draw_cell(row, col)
                
        # Draw note mode indicator
        note_text = small_font.render("Note Mode: " + ("ON" if self.game.note_mode else "OFF"), True, 
                                    GREEN if self.game.note_mode else BLACK)
        screen.blit(note_text, (self.margin, self.margin + self.board_size + 20))
        
        # Draw buttons
        self.draw_buttons()
        
        # Draw game over message if applicable
        if self.game.game_over:
            self.draw_game_over()
            
    def draw_cell(self, row, col):
        """Draw a single cell"""
        x = self.margin + col * self.cell_size
        y = self.margin + row * self.cell_size
        
        # Highlight selected cell
        if self.game.selected_cell == (row, col):
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, (x, y, self.cell_size, self.cell_size))
            
        # Highlight cells in the same row, column, and box as the selected cell
        elif self.game.selected_cell:
            sel_row, sel_col = self.game.selected_cell
            same_box = (row // 3 == sel_row // 3) and (col // 3 == sel_col // 3)
            if row == sel_row or col == sel_col or same_box:
                pygame.draw.rect(screen, LIGHT_GRAY, (x, y, self.cell_size, self.cell_size))
        
        # Highlight original cells
        if self.game.original[row][col]:
            pygame.draw.rect(screen, ORIGINAL_COLOR, (x, y, self.cell_size, self.cell_size))
            
        # Highlight conflicts
        if self.game.show_conflicts and self.game.board[row][col] != 0:
            conflicts = self.game.get_conflicts(row, col)
            if conflicts:
                pygame.draw.rect(screen, ERROR_COLOR, (x, y, self.cell_size, self.cell_size))
                
        # Draw the number
        if self.game.board[row][col] != 0:
            num_text = cell_font.render(str(self.game.board[row][col]), True, 
                                      BLACK if self.game.original[row][col] else BLUE)
            text_rect = num_text.get_rect(center=(x + self.cell_size // 2, y + self.cell_size // 2))
            screen.blit(num_text, text_rect)
        # Draw notes
        elif self.game.notes[row][col]:
            for num in range(1, 10):
                if num in self.game.notes[row][col]:
                    note_text = note_font.render(str(num), True, GRAY)
                    # Position notes in a 3x3 grid within the cell
                    note_x = x + ((num - 1) % 3) * (self.cell_size // 3) + self.cell_size // 6
                    note_y = y + ((num - 1) // 3) * (self.cell_size // 3) + self.cell_size // 6
                    screen.blit(note_text, (note_x, note_y))
                    
    def draw_buttons(self):
        """Draw the game buttons"""
        button_y = self.margin + self.board_size + 50
        button_height = 40
        button_width = 100
        spacing = 20
        
        # New Game button
        pygame.draw.rect(screen, BLUE, (self.margin, button_y, button_width, button_height), 0, 5)
        new_game_text = small_font.render("New Game", True, WHITE)
        screen.blit(new_game_text, (self.margin + button_width // 2 - new_game_text.get_width() // 2, 
                                  button_y + button_height // 2 - new_game_text.get_height() // 2))
        
        # Hint button
        pygame.draw.rect(screen, GREEN, (self.margin + button_width + spacing, button_y, 
                                      button_width, button_height), 0, 5)
        hint_text = small_font.render("Hint", True, WHITE)
        screen.blit(hint_text, (self.margin + button_width + spacing + button_width // 2 - hint_text.get_width() // 2, 
                              button_y + button_height // 2 - hint_text.get_height() // 2))
        
        # Notes button
        pygame.draw.rect(screen, RED if self.game.note_mode else GRAY, 
                       (self.margin + 2 * (button_width + spacing), button_y, 
                        button_width, button_height), 0, 5)
        notes_text = small_font.render("Notes", True, WHITE)
        screen.blit(notes_text, (self.margin + 2 * (button_width + spacing) + button_width // 2 - notes_text.get_width() // 2, 
                               button_y + button_height // 2 - notes_text.get_height() // 2))
        
        # Clear button
        pygame.draw.rect(screen, GRAY, (self.margin + 3 * (button_width + spacing), button_y, 
                                     button_width, button_height), 0, 5)
        clear_text = small_font.render("Clear", True, WHITE)
        screen.blit(clear_text, (self.margin + 3 * (button_width + spacing) + button_width // 2 - clear_text.get_width() // 2, 
                               button_y + button_height // 2 - clear_text.get_height() // 2))
                               
    def draw_game_over(self):
        """Draw the game over message"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        if self.game.is_solved():
            message = "Puzzle Solved!"
            color = GREEN
        else:
            message = "Game Over - Too Many Mistakes"
            color = RED
            
        text = title_font.render(message, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 
                         SCREEN_HEIGHT // 2 - 50))
                         
        # Display time
        minutes, seconds = divmod(int(self.game.elapsed_time), 60)
        time_text = game_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 
                              SCREEN_HEIGHT // 2))
                              
        restart = small_font.render("Press N for a new game", True, WHITE)
        screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 
                            SCREEN_HEIGHT // 2 + 50))
                            
    def get_cell_at_pos(self, pos):
        """Get the cell at the given position"""
        x, y = pos
        
        # Check if click is within the board
        if x < self.margin or x >= self.margin + self.board_size or \
           y < self.margin or y >= self.margin + self.board_size:
            return None
            
        # Calculate cell position
        col = (x - self.margin) // self.cell_size
        row = (y - self.margin) // self.cell_size
        
        return (row, col)
        
    def check_button_click(self, pos):
        """Check if a button was clicked"""
        x, y = pos
        button_y = self.margin + self.board_size + 50
        button_height = 40
        button_width = 100
        spacing = 20
        
        # New Game button
        if self.margin <= x <= self.margin + button_width and \
           button_y <= y <= button_y + button_height:
            return "new_game"
            
        # Hint button
        if self.margin + button_width + spacing <= x <= self.margin + 2 * button_width + spacing and \
           button_y <= y <= button_y + button_height:
            return "hint"
            
        # Notes button
        if self.margin + 2 * (button_width + spacing) <= x <= self.margin + 3 * button_width + 2 * spacing and \
           button_y <= y <= button_y + button_height:
            return "notes"
            
        # Clear button
        if self.margin + 3 * (button_width + spacing) <= x <= self.margin + 4 * button_width + 3 * spacing and \
           button_y <= y <= button_y + button_height:
            return "clear"
            
        return None

def draw_difficulty_selection():
    """Draw the difficulty selection screen"""
    screen.fill(WHITE)
    
    title = title_font.render("Ultimate Sudoku", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
    
    subtitle = game_font.render("Select Difficulty", True, BLACK)
    screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))
    
    difficulties = ["Easy", "Medium", "Hard", "Expert"]
    button_height = 50
    button_width = 200
    button_y = 250
    spacing = 20
    
    buttons = []
    
    for i, diff in enumerate(difficulties):
        y = button_y + i * (button_height + spacing)
        pygame.draw.rect(screen, BLUE, 
                       (SCREEN_WIDTH // 2 - button_width // 2, y, 
                        button_width, button_height), 0, 5)
        diff_text = game_font.render(diff, True, WHITE)
        screen.blit(diff_text, (SCREEN_WIDTH // 2 - diff_text.get_width() // 2, 
                              y + button_height // 2 - diff_text.get_height() // 2))
        buttons.append((diff, pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, y, 
                                       button_width, button_height)))
    
    pygame.display.flip()
    
    # Wait for a difficulty selection
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                for diff, rect in buttons:
                    if rect.collidepoint(event.pos):
                        return diff
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def draw_instructions():
    """Draw the instructions screen"""
    screen.fill(WHITE)
    
    title = title_font.render("Ultimate Sudoku", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    instructions = [
        "How to Play:",
        "",
        "1. Fill the grid so that every row, column, and 3x3 box",
        "   contains the digits 1-9 without repetition.",
        "",
        "2. Click a cell to select it, then press a number key (1-9)",
        "   to fill it or press 0 or Delete to clear it.",
        "",
        "3. Toggle note mode to add small notes in cells.",
        "",
        "4. You have 3 mistakes allowed before game over.",
        "",
        "5. Use hints if you get stuck, but use them wisely!",
        "",
        "Press any key to continue..."
    ]
    
    y_pos = 120
    for line in instructions:
        if line == "How to Play:":
            text = game_font.render(line, True, BLACK)
        else:
            text = small_font.render(line, True, BLACK)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y_pos))
        y_pos += 30
    
    pygame.display.flip()
    
    # Wait for a key press to continue
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN:
                waiting = False

def main():
    game = SudokuGame()
    renderer = GameRenderer(game)
    
    # Show instructions first
    draw_instructions()
    
    # Show difficulty selection
    difficulty = draw_difficulty_selection()
    game.new_game(difficulty)
    
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                # Check for button clicks
                button = renderer.check_button_click(event.pos)
                if button == "new_game":
                    difficulty = draw_difficulty_selection()
                    game.new_game(difficulty)
                elif button == "hint":
                    game.get_hint()
                elif button == "notes":
                    game.toggle_note_mode()
                elif button == "clear":
                    game.clear_cell()
                else:
                    # Check for cell selection
                    cell = renderer.get_cell_at_pos(event.pos)
                    if cell:
                        game.select_cell(cell[0], cell[1])
            elif event.type == KEYDOWN:
                if event.key == K_n:
                    # New game
                    difficulty = draw_difficulty_selection()
                    game.new_game(difficulty)
                elif event.key == K_ESCAPE:
                    running = False
                elif event.key == K_h:
                    # Hint
                    game.get_hint()
                elif event.key == K_SPACE or event.key == K_TAB:
                    # Toggle note mode
                    game.toggle_note_mode()
                elif event.key == K_DELETE or event.key == K_BACKSPACE:
                    # Clear cell
                    game.clear_cell()
                elif event.key in [K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]:
                    # Input number
                    num = event.key - K_0
                    game.input_number(num)
                elif event.key == K_0 or event.key == K_DELETE or event.key == K_BACKSPACE:
                    # Clear cell
                    game.clear_cell()
        
        # Draw the board
        renderer.draw_board()
        pygame.display.flip()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
