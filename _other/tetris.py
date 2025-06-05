#!/usr/bin/env python3
import pygame
import random
import sys
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GRID_X_OFFSET = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
GRID_Y_OFFSET = 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Tetromino shapes and their colors
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

COLORS = [CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

class Tetromino:
    def __init__(self, x, y, shape_index):
        self.x = x
        self.y = y
        self.shape_index = shape_index
        self.shape = SHAPES[shape_index]
        self.color = COLORS[shape_index]
        self.rotation = 0

    def rotate(self, grid):
        # Save the current rotation
        old_rotation = self.rotation
        old_shape = self.shape
        
        # Rotate the shape
        self.rotation = (self.rotation + 1) % 4
        # Create a new rotated shape
        rotated_shape = []
        shape = SHAPES[self.shape_index]
        
        if self.rotation == 0:
            self.shape = shape
        elif self.rotation == 1:
            # 90 degrees clockwise
            height = len(shape)
            width = len(shape[0])
            rotated_shape = [[0 for _ in range(height)] for _ in range(width)]
            for y in range(height):
                for x in range(width):
                    rotated_shape[x][height - 1 - y] = shape[y][x]
            self.shape = rotated_shape
        elif self.rotation == 2:
            # 180 degrees
            height = len(shape)
            width = len(shape[0])
            rotated_shape = [[0 for _ in range(width)] for _ in range(height)]
            for y in range(height):
                for x in range(width):
                    rotated_shape[height - 1 - y][width - 1 - x] = shape[y][x]
            self.shape = rotated_shape
        elif self.rotation == 3:
            # 270 degrees clockwise
            height = len(shape)
            width = len(shape[0])
            rotated_shape = [[0 for _ in range(height)] for _ in range(width)]
            for y in range(height):
                for x in range(width):
                    rotated_shape[width - 1 - x][y] = shape[y][x]
            self.shape = rotated_shape
        
        # Check if the rotation is valid
        if self.collision(grid):
            # If there's a collision, revert to the old rotation
            self.rotation = old_rotation
            self.shape = old_shape
            return False
        return True

    def move(self, dx, dy, grid):
        self.x += dx
        self.y += dy
        if self.collision(grid):
            self.x -= dx
            self.y -= dy
            return False
        return True

    def collision(self, grid):
        for y in range(len(self.shape)):
            for x in range(len(self.shape[y])):
                if self.shape[y][x]:
                    grid_x = self.x + x
                    grid_y = self.y + y
                    
                    # Check if out of bounds
                    if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
                        return True
                    
                    # Check if collides with another block in the grid
                    if grid_y >= 0 and grid[grid_y][grid_x]:
                        return True
        return False

    def lock(self, grid):
        for y in range(len(self.shape)):
            for x in range(len(self.shape[y])):
                if self.shape[y][x]:
                    grid_y = self.y + y
                    if grid_y < 0:
                        return True  # Game over if any block is above the grid
                    grid[grid_y][self.x + x] = self.color
        return False

def create_grid():
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def draw_grid(screen, grid):
    # Draw the grid background
    pygame.draw.rect(screen, WHITE, (GRID_X_OFFSET - 2, GRID_Y_OFFSET - 2, 
                                    GRID_WIDTH * BLOCK_SIZE + 4, GRID_HEIGHT * BLOCK_SIZE + 4), 2)
    
    # Draw the grid cells
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            cell_x = GRID_X_OFFSET + x * BLOCK_SIZE
            cell_y = GRID_Y_OFFSET + y * BLOCK_SIZE
            
            if grid[y][x]:
                pygame.draw.rect(screen, grid[y][x], (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)
            else:
                pygame.draw.rect(screen, BLACK, (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, GRAY, (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_tetromino(screen, tetromino):
    for y in range(len(tetromino.shape)):
        for x in range(len(tetromino.shape[y])):
            if tetromino.shape[y][x]:
                cell_x = GRID_X_OFFSET + (tetromino.x + x) * BLOCK_SIZE
                cell_y = GRID_Y_OFFSET + (tetromino.y + y) * BLOCK_SIZE
                pygame.draw.rect(screen, tetromino.color, (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_next_tetromino(screen, shape_index):
    shape = SHAPES[shape_index]
    color = COLORS[shape_index]
    
    # Position for the next tetromino preview
    next_x = SCREEN_WIDTH - 150
    next_y = 150
    
    # Draw the label
    next_label = font.render("Next:", True, WHITE)
    screen.blit(next_label, (next_x, next_y - 30))
    
    # Draw the shape
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                cell_x = next_x + x * BLOCK_SIZE
                cell_y = next_y + y * BLOCK_SIZE
                pygame.draw.rect(screen, color, (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE))
                pygame.draw.rect(screen, WHITE, (cell_x, cell_y, BLOCK_SIZE, BLOCK_SIZE), 1)

def clear_rows(grid):
    full_rows = []
    for y in range(GRID_HEIGHT):
        if all(grid[y]):
            full_rows.append(y)
    
    for row in full_rows:
        del grid[row]
        grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    
    return len(full_rows)

def draw_score(screen, score, level):
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(score_text, (50, 50))
    screen.blit(level_text, (50, 80))

def draw_game_over(screen):
    game_over_font = pygame.font.SysFont('Arial', 48)
    game_over_text = game_over_font.render("GAME OVER", True, RED)
    restart_text = font.render("Press R to restart", True, WHITE)
    
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 
                                SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 
                              SCREEN_HEIGHT // 2 + game_over_text.get_height()))

def main():
    grid = create_grid()
    
    # Game state
    game_over = False
    paused = False
    
    # Scoring
    score = 0
    level = 1
    lines_cleared = 0
    
    # Timing
    fall_speed = 0.5  # seconds per step
    fall_time = 0
    last_fall_time = pygame.time.get_ticks()
    
    # Create the first tetromino
    current_shape_index = random.randint(0, len(SHAPES) - 1)
    next_shape_index = random.randint(0, len(SHAPES) - 1)
    current_tetromino = Tetromino(GRID_WIDTH // 2 - 1, -2, current_shape_index)
    
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
                
                if game_over:
                    if event.key == K_r:
                        # Restart the game
                        main()
                        return
                    continue
                
                if event.key == K_p:
                    paused = not paused
                
                if not paused:
                    if event.key == K_LEFT:
                        current_tetromino.move(-1, 0, grid)
                    elif event.key == K_RIGHT:
                        current_tetromino.move(1, 0, grid)
                    elif event.key == K_DOWN:
                        current_tetromino.move(0, 1, grid)
                    elif event.key == K_UP:
                        current_tetromino.rotate(grid)
                    elif event.key == K_SPACE:
                        # Hard drop
                        while current_tetromino.move(0, 1, grid):
                            score += 1
        
        if game_over or paused:
            if game_over:
                draw_game_over(screen)
            pygame.display.update()
            continue
        
        # Move the tetromino down automatically
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - last_fall_time) / 1000.0
        fall_time += delta_time
        last_fall_time = current_time
        
        if fall_time >= fall_speed:
            fall_time = 0
            if not current_tetromino.move(0, 1, grid):
                # Lock the tetromino in place
                game_over = current_tetromino.lock(grid)
                
                if not game_over:
                    # Clear completed rows
                    rows_cleared = clear_rows(grid)
                    if rows_cleared > 0:
                        lines_cleared += rows_cleared
                        score += rows_cleared * rows_cleared * 100
                        
                        # Level up every 10 lines
                        level = lines_cleared // 10 + 1
                        fall_speed = max(0.05, 0.5 - (level - 1) * 0.05)
                    
                    # Create a new tetromino
                    current_shape_index = next_shape_index
                    next_shape_index = random.randint(0, len(SHAPES) - 1)
                    current_tetromino = Tetromino(GRID_WIDTH // 2 - 1, -2, current_shape_index)
        
        # Draw everything
        screen.fill(BLACK)
        draw_grid(screen, grid)
        draw_tetromino(screen, current_tetromino)
        draw_next_tetromino(screen, next_shape_index)
        draw_score(screen, score, level)
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
