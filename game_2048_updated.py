#!/usr/bin/env python3
import pygame
import sys
import random
import math
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1100  # Increased window width to accommodate side panel
SCREEN_HEIGHT = 800
GRID_SIZE = 8  # Updated to 8x8 grid
CELL_SIZE = 80  # Slightly smaller cells to fit the larger grid
GRID_PADDING = 10
ANIMATION_SPEED = 25  # Increased sliding speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
GRID_COLOR = (187, 173, 160)
CELL_EMPTY_COLOR = (205, 193, 180)

# Tile colors
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (118, 114, 91),
    8192: (242, 89, 136)  # Special color for 8192 (win condition)
}

# Text colors
TEXT_COLORS = {
    2: (119, 110, 101),
    4: (119, 110, 101),
    8: (249, 246, 242),
    16: (249, 246, 242),
    32: (249, 246, 242),
    64: (249, 246, 242),
    128: (249, 246, 242),
    256: (249, 246, 242),
    512: (249, 246, 242),
    1024: (249, 246, 242),
    2048: (249, 246, 242),
    4096: (249, 246, 242),
    8192: (249, 246, 242)
}

# Load sound effects
try:
    move_sound = pygame.mixer.Sound('move.wav')
    merge_sound = pygame.mixer.Sound('merge.wav')
    game_over_sound = pygame.mixer.Sound('game_over.wav')
    win_sound = pygame.mixer.Sound('win.wav')
except:
    # Create silent sounds if files not found
    move_sound = pygame.mixer.Sound(buffer=bytearray(44))
    merge_sound = pygame.mixer.Sound(buffer=bytearray(44))
    game_over_sound = pygame.mixer.Sound(buffer=bytearray(44))
    win_sound = pygame.mixer.Sound(buffer=bytearray(44))
    print("Sound files not found. Using silent sounds.")

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('2048 - 8x8 Edition')
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.SysFont('Arial', 50, bold=True)
score_font = pygame.font.SysFont('Arial', 30, bold=True)
instruction_font = pygame.font.SysFont('Arial', 18)
game_over_font = pygame.font.SysFont('Arial', 60, bold=True)

# Create fonts for different tile values
tile_fonts = {}
for value in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]:
    # Adjust font size based on number of digits
    if value < 10:
        size = 45
    elif value < 100:
        size = 40
    elif value < 1000:
        size = 35
    else:
        size = 25
    tile_fonts[value] = pygame.font.SysFont('Arial', size, bold=True)

class Tile:
    def __init__(self, value=0, row=0, col=0):
        self.value = value
        self.row = row
        self.col = col
        # Position tiles on the right side of the screen
        self.x = col * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + 300  # Offset for side panel
        self.y = row * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + 50   # Reduced top offset
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False
        self.merging = False
        self.new = value != 0
        self.scale = 0.1 if self.new else 1.0
    
    def update(self):
        # Handle movement animation
        if self.moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < ANIMATION_SPEED:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False
            else:
                self.x += dx * ANIMATION_SPEED / distance
                self.y += dy * ANIMATION_SPEED / distance
        
        # Handle new tile animation
        if self.new and self.scale < 1.0:
            self.scale += 0.1
            if self.scale >= 1.0:
                self.scale = 1.0
                self.new = False
    
    def move_to(self, row, col):
        self.row = row
        self.col = col
        self.target_x = col * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + 300  # Offset for side panel
        self.target_y = row * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + 50   # Reduced top offset
        self.moving = True
    
    def draw(self, surface):
        if self.value == 0:
            return
        
        # Calculate position and size with animation
        size = int(CELL_SIZE * self.scale)
        pos_x = self.x + (CELL_SIZE - size) // 2
        pos_y = self.y + (CELL_SIZE - size) // 2
        
        # Draw tile background
        pygame.draw.rect(surface, TILE_COLORS.get(self.value, (60, 58, 50)), 
                       (pos_x, pos_y, size, size), 0, 5)
        
        # Draw tile value
        if self.value > 0:
            font = tile_fonts.get(self.value, tile_fonts[8192])
            text_color = TEXT_COLORS.get(self.value, WHITE)
            text = font.render(str(self.value), True, text_color)
            text_rect = text.get_rect(center=(self.x + CELL_SIZE // 2, self.y + CELL_SIZE // 2))
            surface.blit(text, text_rect)

class Game2048:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.tiles = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.best_score = 0
        self.game_over = False
        self.won = False
        self.can_continue = False
        self.moving = False
        self.need_new_tile = False
        
        # Initialize tiles
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self.tiles[row][col] = Tile(0, row, col)
        
        # Add initial tiles
        self.add_random_tile()
        self.add_random_tile()
    
    def add_random_tile(self):
        empty_cells = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == 0:
                    empty_cells.append((row, col))
        
        if empty_cells:
            row, col = random.choice(empty_cells)
            value = 2 if random.random() < 0.9 else 4
            self.grid[row][col] = value
            self.tiles[row][col] = Tile(value, row, col)
    
    def move(self, direction):
        if self.game_over or self.moving:
            return False
        
        self.moving = True
        moved = False
        merged = False
        
        # 0: up, 1: right, 2: down, 3: left
        if direction == 0:  # Up
            for col in range(GRID_SIZE):
                for row in range(1, GRID_SIZE):
                    if self.grid[row][col] != 0:
                        result = self.move_tile(row, col, -1, 0)
                        moved |= result[0]
                        merged |= result[1]
        
        elif direction == 1:  # Right
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE - 2, -1, -1):
                    if self.grid[row][col] != 0:
                        result = self.move_tile(row, col, 0, 1)
                        moved |= result[0]
                        merged |= result[1]
        
        elif direction == 2:  # Down
            for col in range(GRID_SIZE):
                for row in range(GRID_SIZE - 2, -1, -1):
                    if self.grid[row][col] != 0:
                        result = self.move_tile(row, col, 1, 0)
                        moved |= result[0]
                        merged |= result[1]
        
        elif direction == 3:  # Left
            for row in range(GRID_SIZE):
                for col in range(1, GRID_SIZE):
                    if self.grid[row][col] != 0:
                        result = self.move_tile(row, col, 0, -1)
                        moved |= result[0]
                        merged |= result[1]
        
        if moved:
            # Play move sound
            move_sound.play()
            if merged:
                merge_sound.play()
            
            # Set flag to add a new tile after animations complete
            self.need_new_tile = True
        else:
            # No movement occurred, so we're not moving anymore
            self.moving = False
        
        return moved
    
    def move_tile(self, row, col, dr, dc):
        moved = False
        merged = False
        curr_row, curr_col = row, col
        value = self.grid[row][col]
        
        # Find the farthest position
        while True:
            next_row, next_col = curr_row + dr, curr_col + dc
            if not (0 <= next_row < GRID_SIZE and 0 <= next_col < GRID_SIZE):
                break
            
            if self.grid[next_row][next_col] == 0:
                curr_row, curr_col = next_row, next_col
                moved = True
            elif self.grid[next_row][next_col] == value:
                curr_row, curr_col = next_row, next_col
                moved = True
                merged = True
                break
            else:
                break
        
        if moved:
            # Move the tile
            if self.grid[curr_row][curr_col] == value:  # Merge
                self.grid[curr_row][curr_col] = value * 2
                self.score += value * 2
                self.best_score = max(self.best_score, self.score)
                
                # Check for win - updated to 8192
                if value * 2 == 8192 and not self.won:
                    self.won = True
                    win_sound.play()
                
                # Update tile
                self.tiles[curr_row][curr_col] = Tile(value * 2, curr_row, curr_col)
                self.tiles[curr_row][curr_col].merging = True
            else:  # Just move
                self.grid[curr_row][curr_col] = value
                # Move the tile object
                self.tiles[row][col].move_to(curr_row, curr_col)
                self.tiles[curr_row][curr_col] = self.tiles[row][col]
            
            self.grid[row][col] = 0
            self.tiles[row][col] = Tile(0, row, col)
        
        return moved, merged
    
    def check_game_over(self):
        # Check if the grid is full
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == 0:
                    return False
        
        # Check if any moves are possible
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                value = self.grid[row][col]
                
                # Check adjacent cells
                for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    next_row, next_col = row + dr, col + dc
                    if 0 <= next_row < GRID_SIZE and 0 <= next_col < GRID_SIZE:
                        if self.grid[next_row][next_col] == value:
                            return False
        
        self.game_over = True
        game_over_sound.play()
        return True
    
    def update(self):
        # Update all tiles
        any_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.tiles[row][col]:
                    self.tiles[row][col].update()
                    if self.tiles[row][col].moving:
                        any_moving = True
        
        # If no tiles are moving and we need to add a new tile
        if not any_moving and self.need_new_tile:
            self.add_random_tile()
            self.check_game_over()
            self.need_new_tile = False
            self.moving = False
    
    def draw(self, surface):
        # Draw background
        surface.fill(LIGHT_GRAY)
        
        # Draw side panel background
        side_panel = pygame.Rect(0, 0, 280, SCREEN_HEIGHT)
        pygame.draw.rect(surface, GRID_COLOR, side_panel)
        
        # Draw title
        title_text = title_font.render("2048", True, WHITE)
        surface.blit(title_text, (20, 20))
        
        subtitle_text = instruction_font.render("8x8 Edition", True, WHITE)
        surface.blit(subtitle_text, (20, 70))
        
        # Draw score boxes
        score_box = pygame.Rect(20, 100, 240, 60)
        best_box = pygame.Rect(20, 170, 240, 60)
        
        pygame.draw.rect(surface, (187, 173, 160, 100), score_box, 0, 5)
        pygame.draw.rect(surface, (187, 173, 160, 100), best_box, 0, 5)
        
        score_label = score_font.render("SCORE", True, WHITE)
        best_label = score_font.render("BEST", True, WHITE)
        
        surface.blit(score_label, (score_box.centerx - score_label.get_width() // 2, score_box.y + 5))
        surface.blit(best_label, (best_box.centerx - best_label.get_width() // 2, best_box.y + 5))
        
        score_value = score_font.render(str(self.score), True, WHITE)
        best_value = score_font.render(str(self.best_score), True, WHITE)
        
        surface.blit(score_value, (score_box.centerx - score_value.get_width() // 2, score_box.y + 30))
        surface.blit(best_value, (best_box.centerx - best_value.get_width() // 2, best_box.y + 30))
        
        # Draw instructions
        instructions = [
            "HOW TO PLAY:",
            "Use arrow keys to move tiles",
            "When two tiles with the same",
            "number touch, they merge!",
            "Reach 8192 to win!",
            "",
            "CONTROLS:",
            "Arrow Keys: Move tiles",
            "R: Restart game",
            "C: Continue after winning",
            "ESC: Quit game"
        ]
        
        y_offset = 250
        for instruction in instructions:
            text = instruction_font.render(instruction, True, WHITE)
            surface.blit(text, (20, y_offset))
            y_offset += 22
        
        # Draw grid background
        grid_rect = pygame.Rect(
            300,  # Left side panel width
            50,   # Top margin
            (CELL_SIZE + GRID_PADDING) * GRID_SIZE + GRID_PADDING,
            (CELL_SIZE + GRID_PADDING) * GRID_SIZE + GRID_PADDING
        )
        pygame.draw.rect(surface, GRID_COLOR, grid_rect, 0, 5)
        
        # Draw empty cells
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell_rect = pygame.Rect(
                    col * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + 300,  # Offset for side panel
                    row * (CELL_SIZE + GRID_PADDING) + GRID_PADDING + 50,   # Reduced top offset
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(surface, CELL_EMPTY_COLOR, cell_rect, 0, 5)
        
        # Draw tiles
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.tiles[row][col]:
                    self.tiles[row][col].draw(surface)
        
        # Draw game over or win message
        if self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            surface.blit(overlay, (0, 0))
            
            game_over_text = game_over_font.render("Game Over!", True, (119, 110, 101))
            restart_text = instruction_font.render("Press R to restart", True, (119, 110, 101))
            
            surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
        
        elif self.won and not self.can_continue:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            surface.blit(overlay, (0, 0))
            
            win_text = game_over_font.render("You Win!", True, (237, 194, 46))
            continue_text = instruction_font.render("Press C to continue playing", True, (119, 110, 101))
            restart_text = instruction_font.render("Press R to restart", True, (119, 110, 101))
            
            surface.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            surface.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            surface.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

def main():
    game = Game2048()
    
    # Main game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if event.key == K_r:
                    game.reset()
                
                if event.key == K_c and game.won and not game.can_continue:
                    game.can_continue = True
                
                if not game.moving and (not game.game_over) and (not game.won or game.can_continue):
                    if event.key == K_UP:
                        game.move(0)
                    elif event.key == K_RIGHT:
                        game.move(1)
                    elif event.key == K_DOWN:
                        game.move(2)
                    elif event.key == K_LEFT:
                        game.move(3)
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw(screen)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
