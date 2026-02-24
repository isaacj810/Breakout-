import pygame
import settings

import pygame

import pygame
import math

class Menu:
    def __init__(self):
        #fondo
        bg = pygame.image.load("assets/fondo_menú.png")
        self.background = pygame.transform.scale(bg, (1080, 720))

        #botón
        self.original_button = pygame.image.load("assets/boton_jugar.png")
        self.base_size = (200, 60)
        
        self.play_button = pygame.transform.scale(self.original_button, self.base_size)
        self.button_rect = self.play_button.get_rect(center=(540, 500))

        # Tiempo para la animación
        self.time = 0

    def draw(self, screen):
        # Fondo
        screen.blit(self.background, (0, 0))

        # Animación del botón
        self.time += 0.05
        scale = 1 + math.sin(self.time) * 0.05   

        new_width = int(self.base_size[0] * scale)
        new_height = int(self.base_size[1] * scale)

        self.play_button = pygame.transform.scale(
            self.original_button, (new_width, new_height)
        )

        self.button_rect = self.play_button.get_rect(center=(540, 500))

        # Dibujar botón
        screen.blit(self.play_button, self.button_rect)

    def check_click(self, mouse_pos):
        return self.button_rect.collidepoint(mouse_pos)
