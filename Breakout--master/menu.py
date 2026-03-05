import pygame
import math
import settings
from pathlib import Path

GAME_DIR   = Path(__file__).resolve().parent
ASSETS_DIR = GAME_DIR / "assets"


class Menu:
    def __init__(self):
        bg = pygame.image.load(str(ASSETS_DIR / "fondo_menú.png"))
        self.background = pygame.transform.scale(bg, (settings.WIDTH, settings.HEIGHT))

        self.original_button = pygame.image.load(str(ASSETS_DIR / "boton_jugar.png"))
        self.base_size = (200, 60)

        self.play_button  = pygame.transform.scale(self.original_button, self.base_size)
        self.button_rect  = self.play_button.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 220))

        self.time = 0

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        self.time += 0.05
        scale = 1 + math.sin(self.time) * 0.05

        new_width  = int(self.base_size[0] * scale)
        new_height = int(self.base_size[1] * scale)

        self.play_button = pygame.transform.scale(self.original_button, (new_width, new_height))
        self.button_rect = self.play_button.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT - 220))

        screen.blit(self.play_button, self.button_rect)

    def check_click(self, mouse_pos):
        return self.button_rect.collidepoint(mouse_pos)
