import pygame
import random
from elements import GameObject, ASSETS_DIR

POWER_TYPES = [
    "x2",
    "slow",
    "small_paddle",
    "fast_ball",
    "damage",
    "sticky"
]

class PowerUp(GameObject):
    def __init__(self, x, y):
        self.type = random.choice(POWER_TYPES)

        self.image = pygame.image.load(str(ASSETS_DIR / "powers" / f"power_{self.type}.png"))
        self.image = pygame.transform.scale(self.image, (32, 32))

        self.rect  = self.image.get_rect(center=(x, y))
        self.speed = 4

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def off_screen(self):
        from settings import HEIGHT
        return self.rect.top > HEIGHT