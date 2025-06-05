import pygame
import sys
import random
import os
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

# Constants
DEFAULT_BOARD_SIZE = 4
TILE_SIZE = 100
MARGIN = 5
BACKGROUND_COLOR = (50, 50, 50)
TILE_COLOR = (100, 149, 237)  # Cornflower blue
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (70, 130, 180)  # Steel blue
BUTTON_HOVER_COLOR = (30, 144, 255)  # Dodger blue
BUTTON_TEXT_COLOR = (255, 255, 255)

# Image options
IMAGE_OPTIONS = ["Numbers"]

# Set up the clock
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 40, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 24, bold=True)
TINY_FONT = pygame.font.SysFont("Arial", 18)

# Create a simple sound for tile sliding
try:
    SLIDE_SOUND = pygame.mixer.Sound("slide.wav")
except (FileNotFoundError, pygame.error):
    # Create a very simple sound using a basic buffer
    buf = bytes([127] * 1000 + [0] * 1000) * 10
    SLIDE_SOUND = pygame.mixer.Sound(buffer=buf)
    SLIDE_SOUND.set_volume(0.3)


# Check for image files in the current directory
def find_image_files():
    image_files = []
    for file in os.listdir("."):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            image_files.append(file)
    return image_files


# Update image options with found files
IMAGE_OPTIONS.extend(find_image_files())


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=5)  # Border

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click


class SlidePuzzle:
    def __init__(self, board_size=DEFAULT_BOARD_SIZE):
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

        # For even-sized boards (4x4, 6x6)
        if self.board_size % 2 == 0:
            empty_row = self.empty_pos // self.board_size
            from_bottom = self.board_size - empty_row
            return (from_bottom % 2 == 0 and inversions % 2 == 1) or (
                from_bottom % 2 == 1 and inversions % 2 == 0
            )
        # For odd-sized boards (3x3, 5x5)
        else:
            return inversions % 2 == 0

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
            self.board[self.empty_pos], self.board[position] = (
                self.board[position],
                self.board[self.empty_pos],
            )
            self.empty_pos = position

            # Play slide sound
            if "SLIDE_SOUND" in globals() and SLIDE_SOUND:
                SLIDE_SOUND.play()

            return True
        return False

    def is_solved(self):
        """Check if the puzzle is solved"""
        return self.board == self.solved_state

    def get_tile_position(self, tile_value):
        """Get the position of a specific tile value"""
        return self.board.index(tile_value)


class Game:
    def __init__(self):
        self.state = "menu"  # "menu", "game", "win"
        self.board_size = DEFAULT_BOARD_SIZE
        self.puzzle = None
        self.window_size = None
        self.window = None
        self.current_image = "Numbers"
        self.images = {}  # Will store loaded images
        self.tile_images = {}  # Will store the split image tiles
        self.setup_window()

    def setup_window(self):
        # Set initial window size for menu
        self.window_size = 600
        self.window = pygame.display.set_mode((self.window_size, self.window_size))
        pygame.display.set_caption("Slide Puzzle")

    def resize_window(self):
        # Calculate window size based on board size
        game_area = self.board_size * (TILE_SIZE + MARGIN) + MARGIN
        # Add extra space for the buttons
        self.window_size = max(600, game_area)
        self.window = pygame.display.set_mode((self.window_size, self.window_size + 60))
        pygame.display.set_caption("Slide Puzzle")

    def create_size_buttons(self):
        buttons = []
        sizes = [3, 4, 5, 6]
        button_width = 100
        button_height = 60
        spacing = 20
        total_width = len(sizes) * button_width + (len(sizes) - 1) * spacing
        start_x = (self.window_size - total_width) // 2

        for i, size in enumerate(sizes):
            x = start_x + i * (button_width + spacing)
            y = self.window_size // 2
            text = f"{size}x{size}"
            button = Button(
                x,
                y,
                button_width,
                button_height,
                text,
                BUTTON_COLOR,
                BUTTON_HOVER_COLOR,
                BUTTON_TEXT_COLOR,
                SMALL_FONT,
            )
            buttons.append((button, size))

        return buttons

    def create_image_buttons(self):
        buttons = []
        images = IMAGE_OPTIONS

        # Calculate button dimensions based on number of options
        button_width = min(120, (self.window_size - 40) // max(len(images), 1))
        button_height = 40
        spacing = 10

        # If we have many images, we might need multiple rows
        max_buttons_per_row = (self.window_size - 40) // (button_width + spacing)
        rows = (
            len(images) + max_buttons_per_row - 1
        ) // max_buttons_per_row  # Ceiling division

        for i, image in enumerate(images):
            row = i // max_buttons_per_row
            col = i % max_buttons_per_row

            # Calculate position for this button
            x = 20 + col * (button_width + spacing)
            y = self.window_size // 2 + 100 + row * (button_height + spacing)

            # Truncate long filenames for display
            display_name = image
            if len(display_name) > 10 and display_name != "Numbers":
                display_name = display_name[:7] + "..."

            button = Button(
                x,
                y,
                button_width,
                button_height,
                display_name,
                BUTTON_COLOR,
                BUTTON_HOVER_COLOR,
                BUTTON_TEXT_COLOR,
                SMALL_FONT,
            )
            buttons.append((button, image))

        return buttons

    def create_menu_button(self):
        button_width = 100
        button_height = 40
        # Position in top left corner
        x = 10
        y = 10

        return Button(
            x,
            y,
            button_width,
            button_height,
            "Menu",
            BUTTON_COLOR,
            BUTTON_HOVER_COLOR,
            BUTTON_TEXT_COLOR,
            SMALL_FONT,
        )

    def load_image(self, image_name):
        """Load an image from file or use default for 'Numbers'"""
        if image_name == "Numbers":
            return None

        try:
            # Try to load the image file
            image = pygame.image.load(image_name)
            return image
        except pygame.error:
            print(f"Error loading image: {image_name}")
            return None

    def split_image(self, image_name):
        """Split the selected image into tiles"""
        if image_name == "Numbers":
            return {}  # No need to split for number tiles

        # Load the source image if not already loaded
        if image_name not in self.images:
            self.images[image_name] = self.load_image(image_name)

        source_img = self.images[image_name]
        if source_img is None:
            return {}

        # Scale the image to fit the board size
        board_pixel_size = self.board_size * TILE_SIZE
        scaled_img = pygame.transform.scale(
            source_img, (board_pixel_size, board_pixel_size)
        )

        # Split the image into tiles
        tiles = {}
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Create a surface for this tile
                tile_img = pygame.Surface((TILE_SIZE, TILE_SIZE))

                # Copy the portion of the image for this tile
                tile_img.blit(
                    scaled_img,
                    (0, 0),
                    (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                )

                # Store the tile image
                tile_num = row * self.board_size + col + 1
                tiles[tile_num] = tile_img

        return tiles

    def draw_menu(self):
        self.window.fill(BACKGROUND_COLOR)

        # Draw title
        title_text = FONT.render("Slide Puzzle", True, TEXT_COLOR)
        title_rect = title_text.get_rect(
            center=(self.window_size // 2, self.window_size // 4)
        )
        self.window.blit(title_text, title_rect)

        # Draw grid size instruction
        instruction_text = SMALL_FONT.render("Select Grid Size:", True, TEXT_COLOR)
        instruction_rect = instruction_text.get_rect(
            center=(self.window_size // 2, self.window_size // 3)
        )
        self.window.blit(instruction_text, instruction_rect)

        # Draw size buttons
        size_buttons = self.create_size_buttons()
        for button, _ in size_buttons:
            button.draw(self.window)

        # Draw image selection instruction
        image_text = SMALL_FONT.render("Select Image:", True, TEXT_COLOR)
        image_rect = image_text.get_rect(
            center=(self.window_size // 2, self.window_size // 2 + 70)
        )
        self.window.blit(image_text, image_rect)

        # Draw image buttons
        image_buttons = self.create_image_buttons()
        for button, _ in image_buttons:
            button.draw(self.window)

        # Draw current image indicator
        current_image_display = self.current_image
        if len(current_image_display) > 20 and current_image_display != "Numbers":
            current_image_display = current_image_display[:17] + "..."

        current_image_text = TINY_FONT.render(
            f"Current Image: {current_image_display}", True, TEXT_COLOR
        )
        current_image_rect = current_image_text.get_rect(
            center=(self.window_size // 2, self.window_size - 50)
        )
        self.window.blit(current_image_text, current_image_rect)

        pygame.display.update()
        return size_buttons, image_buttons

    def draw_board(self):
        # Fill background
        self.window.fill(BACKGROUND_COLOR)

        # Calculate the offset to center the board if window is larger
        game_area = self.board_size * (TILE_SIZE + MARGIN) + MARGIN
        offset_x = (self.window_size - game_area) // 2
        offset_y = (
            self.window_size - game_area
        ) // 2 + 30  # Add extra space at top for buttons

        for i in range(self.puzzle.total_tiles):
            tile_value = self.puzzle.board[i]

            if tile_value != self.puzzle.total_tiles:  # Don't draw the empty tile
                row, col = divmod(i, self.puzzle.board_size)
                x = offset_x + col * (TILE_SIZE + MARGIN) + MARGIN
                y = offset_y + row * (TILE_SIZE + MARGIN) + MARGIN

                # Draw tile based on the selected image style
                if self.current_image == "Numbers":
                    # Draw standard numbered tile
                    pygame.draw.rect(
                        self.window, TILE_COLOR, (x, y, TILE_SIZE, TILE_SIZE)
                    )

                    # Adjust font size based on board size
                    font_size = (
                        40
                        if self.board_size <= 4
                        else (30 if self.board_size == 5 else 25)
                    )
                    font = pygame.font.SysFont("Arial", font_size, bold=True)

                    # Draw number
                    text = font.render(str(tile_value), True, TEXT_COLOR)
                    text_rect = text.get_rect(
                        center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                    )
                    self.window.blit(text, text_rect)
                else:
                    # Draw image tile
                    if tile_value in self.tile_images:
                        self.window.blit(self.tile_images[tile_value], (x, y))

                        # Draw small number in corner for reference
                        small_font = pygame.font.SysFont("Arial", 16)
                        text = small_font.render(str(tile_value), True, (255, 255, 255))
                        text_rect = text.get_rect(
                            bottomright=(x + TILE_SIZE - 5, y + TILE_SIZE - 5)
                        )
                        self.window.blit(text, text_rect)
                    else:
                        # Fallback if image is not available
                        pygame.draw.rect(
                            self.window, TILE_COLOR, (x, y, TILE_SIZE, TILE_SIZE)
                        )
                        font = pygame.font.SysFont("Arial", 20)
                        text = font.render(str(tile_value), True, TEXT_COLOR)
                        text_rect = text.get_rect(
                            center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                        )
                        self.window.blit(text, text_rect)

        # Draw menu button in top left
        menu_button = self.create_menu_button()
        menu_button.draw(self.window)

        # Draw image name indicator
        image_display = self.current_image
        if len(image_display) > 20 and image_display != "Numbers":
            image_display = image_display[:17] + "..."

        style_text = TINY_FONT.render(f"Image: {image_display}", True, TEXT_COLOR)
        style_rect = style_text.get_rect(topleft=(120, 20))
        self.window.blit(style_text, style_rect)

        # Draw restart instruction
        restart_text = TINY_FONT.render("Press 'R' to restart", True, TEXT_COLOR)
        restart_rect = restart_text.get_rect(
            bottomright=(self.window_size - 10, self.window_size + 50)
        )
        self.window.blit(restart_text, restart_rect)

        pygame.display.update()
        return menu_button

    def draw_win_screen(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface(
            (self.window_size, self.window_size + 60), pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 128))
        self.window.blit(overlay, (0, 0))

        # Draw win message
        win_text = FONT.render("Puzzle Solved!", True, (255, 215, 0))
        text_rect = win_text.get_rect(
            center=(self.window_size // 2, self.window_size // 2 - 30)
        )
        self.window.blit(win_text, text_rect)

        # Draw restart instruction
        restart_text = SMALL_FONT.render(
            "Press R to restart or M for menu", True, (255, 255, 255)
        )
        restart_rect = restart_text.get_rect(
            center=(self.window_size // 2, self.window_size // 2 + 30)
        )
        self.window.blit(restart_text, restart_rect)

        pygame.display.update()

    def get_clicked_position(self, mouse_pos):
        """Convert mouse position to board position"""
        # Calculate the offset to center the board if window is larger
        game_area = self.board_size * (TILE_SIZE + MARGIN) + MARGIN
        offset_x = (self.window_size - game_area) // 2
        offset_y = (
            self.window_size - game_area
        ) // 2 + 30  # Add extra space at top for buttons

        x, y = mouse_pos
        x -= offset_x
        y -= offset_y

        # Check if click is within the board
        if x < 0 or x >= game_area or y < 0 or y >= game_area:
            return None

        col = x // (TILE_SIZE + MARGIN)
        row = y // (TILE_SIZE + MARGIN)

        # Check if click is on a tile, not on the margin
        if x % (TILE_SIZE + MARGIN) < MARGIN or y % (TILE_SIZE + MARGIN) < MARGIN:
            return None

        return row * self.board_size + col

    def start_game(self, board_size):
        self.board_size = board_size
        self.puzzle = SlidePuzzle(board_size)
        self.puzzle.shuffle()
        self.resize_window()

        # Split the image into tiles if using an image style
        if self.current_image != "Numbers":
            self.tile_images = self.split_image(self.current_image)
        else:
            self.tile_images = {}

        self.state = "game"

    def handle_menu_events(self):
        size_buttons, image_buttons = self.draw_menu()

        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            mouse_pos = pygame.mouse.get_pos()

            # Update button hover states
            for button, _ in size_buttons:
                button.update(mouse_pos)

            for button, _ in image_buttons:
                button.update(mouse_pos)

            if event.type == MOUSEBUTTONDOWN:
                # Check for grid size selection
                for button, size in size_buttons:
                    if button.is_clicked(mouse_pos, True):
                        self.start_game(size)
                        return True

                # Check for image selection
                for button, image in image_buttons:
                    if button.is_clicked(mouse_pos, True):
                        self.current_image = image
                        return True

        return True

    def handle_game_events(self):
        menu_button = self.draw_board()

        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            mouse_pos = pygame.mouse.get_pos()
            menu_button.update(mouse_pos)

            if event.type == MOUSEBUTTONDOWN:
                # Check if menu button was clicked
                if menu_button.is_clicked(mouse_pos, True):
                    self.state = "menu"
                    self.setup_window()
                    return True

                clicked_pos = self.get_clicked_position(mouse_pos)
                if clicked_pos is not None:
                    # Normal move
                    self.puzzle.move_tile(clicked_pos)

            if event.type == KEYDOWN:
                if event.key == K_r:
                    self.puzzle = SlidePuzzle(self.board_size)
                    self.puzzle.shuffle()
                elif event.key == K_m:
                    self.state = "menu"
                    self.setup_window()

        # Check for win condition
        if self.puzzle.is_solved():
            self.state = "win"

        return True

    def handle_win_events(self):
        self.draw_board()
        self.draw_win_screen()

        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            if event.type == KEYDOWN:
                if event.key == K_r:
                    self.puzzle = SlidePuzzle(self.board_size)
                    self.puzzle.shuffle()
                    self.state = "game"
                elif event.key == K_m:
                    self.state = "menu"
                    self.setup_window()

        return True

    def run(self):
        running = True

        while running:
            if self.state == "menu":
                running = self.handle_menu_events()
            elif self.state == "game":
                running = self.handle_game_events()
            elif self.state == "win":
                running = self.handle_win_events()

            CLOCK.tick(30)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
