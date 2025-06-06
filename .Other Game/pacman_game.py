import pygame
import sys
import random
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 40
PACMAN_SIZE = 30
GHOST_SIZE = 30
DOT_SIZE = 8
POWER_DOT_SIZE = 16
WALL_COLOR = (0, 0, 139)  # Dark blue
BACKGROUND_COLOR = (0, 0, 0)  # Black
PACMAN_COLOR = (255, 255, 0)  # Yellow
GHOST_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 255),  # Cyan
    (255, 184, 255),  # Pink
    (255, 184, 82)  # Orange
]
VULNERABLE_GHOST_COLOR = (0, 0, 255)  # Blue
DOT_COLOR = (255, 255, 255)  # White
POWER_DOT_COLOR = (255, 255, 255)  # White
TEXT_COLOR = (255, 255, 255)  # White
SCORE_POS = (20, 10)
LIVES_POS = (SCREEN_WIDTH - 150, 10)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PacMan Game')
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# Sound effects
try:
    chomp_sound = pygame.mixer.Sound('chomp.wav')
    power_dot_sound = pygame.mixer.Sound('power_dot.wav')
    ghost_eat_sound = pygame.mixer.Sound('ghost_eat.wav')
    death_sound = pygame.mixer.Sound('death.wav')
except:
    # Create simple sounds if files not found
    chomp_sound = pygame.mixer.Sound(buffer=bytes([127] * 300 + [0] * 300))
    power_dot_sound = pygame.mixer.Sound(buffer=bytes([200] * 600 + [0] * 600))
    ghost_eat_sound = pygame.mixer.Sound(buffer=bytes([200] * 400 + [0] * 400))
    death_sound = pygame.mixer.Sound(buffer=bytes([200] * 800 + [0] * 800))

# Game map
# 0 = empty, 1 = wall, 2 = dot, 3 = power dot, 4 = ghost spawn
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
    [1, 3, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 4, 4, 1, 1, 0, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
    [1, 3, 2, 1, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 1, 2, 3, 1],
    [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Calculate offset to center the map
MAP_WIDTH = len(game_map[0]) * CELL_SIZE
MAP_HEIGHT = len(game_map) * CELL_SIZE
OFFSET_X = (SCREEN_WIDTH - MAP_WIDTH) // 2
OFFSET_Y = (SCREEN_HEIGHT - MAP_HEIGHT) // 2 + 20  # Extra space for score

class PacMan:
    def __init__(self):
        self.x = 10
        self.y = 15
        self.direction = (0, 0)  # (dx, dy)
        self.next_direction = (0, 0)
        self.speed = 1
        self.lives = 3
        self.score = 0
        self.power_mode = False
        self.power_timer = 0
        
        # Find a valid starting position with a dot
        for y in range(len(game_map)):
            for x in range(len(game_map[0])):
                if game_map[y][x] == 2:
                    self.x = x
                    self.y = y
                    return
    
    def update(self, ghosts):
        # Try to change direction if requested
        if self.next_direction != (0, 0):
            next_x = self.x + self.next_direction[0]
            next_y = self.y + self.next_direction[1]
            
            # Check if the next position is valid (not a wall)
            if 0 <= next_x < len(game_map[0]) and 0 <= next_y < len(game_map):
                if game_map[next_y][next_x] != 1:
                    self.direction = self.next_direction
        
        # Move in the current direction
        next_x = self.x + self.direction[0]
        next_y = self.y + self.direction[1]
        
        # Check if the next position is valid (not a wall)
        if 0 <= next_x < len(game_map[0]) and 0 <= next_y < len(game_map):
            if game_map[next_y][next_x] != 1:
                self.x = next_x
                self.y = next_y
                
                # Check if PacMan ate a dot
                if game_map[self.y][self.x] == 2:
                    game_map[self.y][self.x] = 0
                    self.score += 10
                    chomp_sound.play()
                
                # Check if PacMan ate a power dot
                elif game_map[self.y][self.x] == 3:
                    game_map[self.y][self.x] = 0
                    self.score += 50
                    self.power_mode = True
                    self.power_timer = 300  # 5 seconds at 60 FPS
                    power_dot_sound.play()
        
        # Update power mode timer
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
        
        # Check for ghost collisions
        self.check_ghost_collisions(ghosts)
    
    def check_ghost_collisions(self, ghosts):
        for ghost in ghosts:
            if self.x == ghost.x and self.y == ghost.y:
                if self.power_mode:
                    # Eat the ghost
                    ghost.reset()
                    self.score += 200
                    ghost_eat_sound.play()
                else:
                    # PacMan dies
                    self.lives -= 1
                    death_sound.play()
                    self.reset()
                    for g in ghosts:
                        g.reset()
                    pygame.time.delay(1000)  # Pause for a second
                    break
    
    def reset(self):
        # Reset PacMan to starting position
        for y in range(len(game_map)):
            for x in range(len(game_map[0])):
                if game_map[y][x] == 2:
                    self.x = x
                    self.y = y
                    self.direction = (0, 0)
                    self.next_direction = (0, 0)
                    return
    
    def draw(self):
        # Calculate pixel position
        x = OFFSET_X + self.x * CELL_SIZE + CELL_SIZE // 2
        y = OFFSET_Y + self.y * CELL_SIZE + CELL_SIZE // 2
        
        # Draw PacMan as a circle with a mouth
        angle = 0
        if self.direction == (1, 0):  # Right
            angle = 0
        elif self.direction == (-1, 0):  # Left
            angle = 180
        elif self.direction == (0, -1):  # Up
            angle = 90
        elif self.direction == (0, 1):  # Down
            angle = 270
        
        # Animation for mouth opening/closing
        mouth_angle = 45 + 15 * (pygame.time.get_ticks() % 400 > 200)
        
        pygame.draw.circle(screen, PACMAN_COLOR, (x, y), PACMAN_SIZE // 2)
        
        # Draw the mouth (a triangle cut out from the circle)
        if self.direction != (0, 0):
            mouth_points = [
                (x, y),
                (x + PACMAN_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(angle - mouth_angle).x,
                 y + PACMAN_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(angle - mouth_angle).y),
                (x + PACMAN_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(angle + mouth_angle).x,
                 y + PACMAN_SIZE // 2 * pygame.math.Vector2(1, 0).rotate(angle + mouth_angle).y)
            ]
            pygame.draw.polygon(screen, BACKGROUND_COLOR, mouth_points)

class Ghost:
    def __init__(self, color_idx, x=10, y=10):
        self.color_idx = color_idx
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.direction = (0, 0)
        self.speed = 0.75
        self.move_timer = 0
        
        # Find the ghost spawn area
        for y in range(len(game_map)):
            for x in range(len(game_map[0])):
                if game_map[y][x] == 4:
                    self.original_x = x
                    self.original_y = y
                    self.x = x
                    self.y = y
                    return
    
    def reset(self):
        self.x = self.original_x
        self.y = self.original_y
        self.direction = (0, 0)
        self.move_timer = 0
    
    def update(self, pacman):
        self.move_timer += self.speed
        if self.move_timer < 1:
            return
        
        self.move_timer = 0
        
        # Decide on a direction
        possible_directions = []
        
        # Check all four directions
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            next_x = self.x + dx
            next_y = self.y + dy
            
            # Check if the next position is valid (not a wall)
            if 0 <= next_x < len(game_map[0]) and 0 <= next_y < len(game_map):
                if game_map[next_y][next_x] != 1:
                    # Don't go back the way we came unless we have to
                    if (dx, dy) != (-self.direction[0], -self.direction[1]) or len(possible_directions) == 0:
                        possible_directions.append((dx, dy))
        
        if possible_directions:
            if pacman.power_mode:
                # Run away from PacMan
                best_direction = None
                max_distance = -1
                
                for dx, dy in possible_directions:
                    next_x = self.x + dx
                    next_y = self.y + dy
                    distance = (next_x - pacman.x) ** 2 + (next_y - pacman.y) ** 2
                    
                    if distance > max_distance:
                        max_distance = distance
                        best_direction = (dx, dy)
                
                self.direction = best_direction
            else:
                # Chase PacMan with some randomness
                if random.random() < 0.75:  # 75% chance to chase
                    best_direction = None
                    min_distance = float('inf')
                    
                    for dx, dy in possible_directions:
                        next_x = self.x + dx
                        next_y = self.y + dy
                        distance = (next_x - pacman.x) ** 2 + (next_y - pacman.y) ** 2
                        
                        if distance < min_distance:
                            min_distance = distance
                            best_direction = (dx, dy)
                    
                    self.direction = best_direction
                else:
                    # Random movement
                    self.direction = random.choice(possible_directions)
        
        # Move in the chosen direction
        self.x += self.direction[0]
        self.y += self.direction[1]
    
    def draw(self, pacman):
        # Calculate pixel position
        x = OFFSET_X + self.x * CELL_SIZE + CELL_SIZE // 2
        y = OFFSET_Y + self.y * CELL_SIZE + CELL_SIZE // 2
        
        # Choose color based on power mode
        if pacman.power_mode:
            color = VULNERABLE_GHOST_COLOR
            # Blink when power mode is about to end
            if pacman.power_timer < 60 and pacman.power_timer % 10 < 5:
                color = GHOST_COLORS[self.color_idx]
        else:
            color = GHOST_COLORS[self.color_idx]
        
        # Draw ghost body (circle for simplicity)
        pygame.draw.circle(screen, color, (x, y), GHOST_SIZE // 2)
        
        # Draw eyes
        eye_offset = 5
        if self.direction == (1, 0):  # Right
            eye_pos = [(x + eye_offset, y - eye_offset), (x + eye_offset, y + eye_offset)]
        elif self.direction == (-1, 0):  # Left
            eye_pos = [(x - eye_offset, y - eye_offset), (x - eye_offset, y + eye_offset)]
        elif self.direction == (0, -1):  # Up
            eye_pos = [(x - eye_offset, y - eye_offset), (x + eye_offset, y - eye_offset)]
        elif self.direction == (0, 1):  # Down
            eye_pos = [(x - eye_offset, y + eye_offset), (x + eye_offset, y + eye_offset)]
        else:
            eye_pos = [(x - eye_offset, y - eye_offset), (x + eye_offset, y - eye_offset)]
        
        for ex, ey in eye_pos:
            pygame.draw.circle(screen, (255, 255, 255), (ex, ey), 4)  # White eye
            pygame.draw.circle(screen, (0, 0, 0), (ex + 1, ey + 1), 2)  # Black pupil

def draw_map():
    for y in range(len(game_map)):
        for x in range(len(game_map[0])):
            cell_x = OFFSET_X + x * CELL_SIZE
            cell_y = OFFSET_Y + y * CELL_SIZE
            
            if game_map[y][x] == 1:  # Wall
                pygame.draw.rect(screen, WALL_COLOR, (cell_x, cell_y, CELL_SIZE, CELL_SIZE))
            elif game_map[y][x] == 2:  # Dot
                pygame.draw.circle(screen, DOT_COLOR, 
                                  (cell_x + CELL_SIZE // 2, cell_y + CELL_SIZE // 2), 
                                  DOT_SIZE // 2)
            elif game_map[y][x] == 3:  # Power Dot
                pygame.draw.circle(screen, POWER_DOT_COLOR, 
                                  (cell_x + CELL_SIZE // 2, cell_y + CELL_SIZE // 2), 
                                  POWER_DOT_SIZE // 2)
                # Make power dots blink
                if pygame.time.get_ticks() % 500 < 250:
                    pygame.draw.circle(screen, BACKGROUND_COLOR, 
                                      (cell_x + CELL_SIZE // 2, cell_y + CELL_SIZE // 2), 
                                      POWER_DOT_SIZE // 4)

def draw_ui(pacman):
    # Draw score
    score_text = font.render(f"Score: {pacman.score}", True, TEXT_COLOR)
    screen.blit(score_text, SCORE_POS)
    
    # Draw lives
    lives_text = font.render(f"Lives: {pacman.lives}", True, TEXT_COLOR)
    screen.blit(lives_text, LIVES_POS)

def check_win_condition():
    # Check if all dots and power dots are eaten
    for y in range(len(game_map)):
        for x in range(len(game_map[0])):
            if game_map[y][x] in [2, 3]:  # Dot or Power Dot
                return False
    return True

def game_over_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text, text_rect)
    
    score_text = font.render(f"Final Score: {pacman.score}", True, TEXT_COLOR)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(score_text, score_rect)
    
    restart_text = font.render("Press SPACE to play again or ESC to quit", True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return True  # Restart
                elif event.key == K_ESCAPE:
                    return False  # Quit

def win_screen():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    win_text = font.render("YOU WIN!", True, (255, 255, 0))
    text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(win_text, text_rect)
    
    score_text = font.render(f"Final Score: {pacman.score}", True, TEXT_COLOR)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(score_text, score_rect)
    
    restart_text = font.render("Press SPACE to play again or ESC to quit", True, TEXT_COLOR)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(restart_text, restart_rect)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    return True  # Restart
                elif event.key == K_ESCAPE:
                    return False  # Quit

def reset_game():
    global game_map
    # Reset the map
    game_map = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
        [1, 3, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 3, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1],
        [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0],
        [1, 1, 1, 1, 2, 1, 0, 1, 1, 4, 4, 1, 1, 0, 1, 2, 1, 1, 1, 1],
        [0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
        [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
        [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0],
        [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
        [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
        [1, 3, 2, 1, 2, 2, 2, 2, 2, 0, 0, 2, 2, 2, 2, 2, 1, 2, 3, 1],
        [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
        [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    
    # Create new game objects
    pacman = PacMan()
    ghosts = [Ghost(i) for i in range(4)]
    
    return pacman, ghosts

# Main game loop
def main():
    global pacman, ghosts
    
    pacman, ghosts = reset_game()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_UP:
                    pacman.next_direction = (0, -1)
                elif event.key == K_RIGHT:
                    pacman.next_direction = (1, 0)
                elif event.key == K_DOWN:
                    pacman.next_direction = (0, 1)
                elif event.key == K_LEFT:
                    pacman.next_direction = (-1, 0)
                elif event.key == K_ESCAPE:
                    running = False
        
        # Update game state
        pacman.update(ghosts)
        for ghost in ghosts:
            ghost.update(pacman)
        
        # Check win/lose conditions
        if pacman.lives <= 0:
            if game_over_screen():
                pacman, ghosts = reset_game()
            else:
                running = False
        
        if check_win_condition():
            if win_screen():
                pacman, ghosts = reset_game()
            else:
                running = False
        
        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        draw_map()
        pacman.draw()
        for ghost in ghosts:
            ghost.draw(pacman)
        draw_ui(pacman)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
