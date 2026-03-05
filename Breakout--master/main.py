"""
Breakout - Módulo para Arcade Machine SDK
==========================================
Integra el juego Breakout como un módulo compatible con arcade-machine-sdk.
La clase BreakoutGame implementa la interfaz GameBase del SDK.
"""

import pygame
from pathlib import Path

from arcade_machine_sdk import GameBase, GameMeta

import settings
import elements
from menu import Menu
from game import Game

GAME_DIR   = Path(__file__).resolve().parent
ASSETS_DIR = GAME_DIR / "assets"


# ──────────────────────────────────────────────────────────────────────────────
# Metadatos del juego
# ──────────────────────────────────────────────────────────────────────────────
metadata = (
    GameMeta()
    .with_title("Breakout")
    .with_description("Juego clásico de Breakout con 10 niveles, poderes y efectos especiales.")
    .with_release_date("04/03/2026")
    .with_group_number(1)
    .add_tag("Arcade")
    .add_tag("Clásico")
    .add_author("Equipo Breakout")
)


# ──────────────────────────────────────────────────────────────────────────────
# Clase principal del módulo
# ──────────────────────────────────────────────────────────────────────────────
class BreakoutGame(GameBase):
    """
    Módulo Breakout para Arcade Machine SDK.

    Estados del juego:
        menu          → Pantalla principal
        info          → Pantalla de información / instrucciones
        game          → Juego en curso
        level_complete → Nivel completado
        game_over     → Partida perdida
    """

    def __init__(self, meta: GameMeta):
        super().__init__(meta)
        self._game_state   = "menu"
        self._menu         = None
        self._game         = None
        self._transitioning = False
        self._fade_alpha   = 0
        self._game_slide_y = settings.HEIGHT   # para animación de entrada

        # Recursos de UI (se cargan en start())
        self._font_big    = None
        self._font_medium = None
        self._info_image  = None

        self._button_menu     = None
        self._button_menu_rect     = None
        self._button_reiniciar     = None
        self._button_reiniciar_rect = None
        self._button_proximo       = None
        self._button_proximo_rect  = None
        self._button_info          = None
        self._button_info_rect     = None
        self._button_close         = None
        self._button_close_rect    = None

        self._click_sound = None

    # ── Ciclo de vida ─────────────────────────────────────────────────────────
    def start(self, surface: pygame.Surface) -> None:
        super().start(surface)

        # Garantizar que los submódulos de pygame estén inicializados
        # (el SDK puede no inicializarlos todos antes de llamar a start)
        if not pygame.font.get_init():
            pygame.font.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Fuentes
        self._font_big    = pygame.font.Font(str(ASSETS_DIR / "StackedStrong-Regular.otf"), 72)
        self._font_medium = pygame.font.Font(str(ASSETS_DIR / "StackedStrong-Regular.otf"), 40)

        # Pantallas
        self._menu = Menu()
        self._game = Game()
        self._game_state   = "menu"
        self._transitioning = False
        self._fade_alpha   = 0
        self._game_slide_y = settings.HEIGHT

        # Imagen de información
        info_raw = pygame.image.load(str(ASSETS_DIR / "pantalla_información.png"))
        self._info_image = pygame.transform.scale(info_raw, (settings.WIDTH, settings.HEIGHT))

        # Botones (tamaño adaptado a 1024x768)
        BW, BH = 150, 50

        def _load_btn(filename, size=None):
            img = pygame.image.load(str(ASSETS_DIR / filename))
            return pygame.transform.scale(img, size or (BW, BH))

        cx = settings.WIDTH // 2

        self._button_menu         = _load_btn("boton_menú.png")
        self._button_menu_rect    = self._button_menu.get_rect(center=(cx, settings.HEIGHT - 190))

        self._button_reiniciar    = _load_btn("boton_reiniciar.png")
        self._button_reiniciar_rect = self._button_reiniciar.get_rect(center=(cx, settings.HEIGHT - 270))

        self._button_proximo      = _load_btn("boton_próximo.png")
        self._button_proximo_rect = self._button_proximo.get_rect(center=(cx, settings.HEIGHT - 270))

        self._button_info         = _load_btn("boton_!.png", (50, 50))
        self._button_info_rect    = self._button_info.get_rect(topright=(settings.WIDTH - 20, 20))

        self._button_close        = _load_btn("boton_x.png", (50, 50))
        self._button_close_rect   = self._button_close.get_rect(topright=(settings.WIDTH - 20, 20))

        # Sonido
        self._click_sound = pygame.mixer.Sound(str(ASSETS_DIR / "music" / "click_boton.mp3"))
        self._click_sound.set_volume(0.7)

        # Música del menú
        self._play_menu_music()

    def stop(self) -> None:
        pygame.mixer.music.stop()
        super().stop()

    # ── Métodos obligatorios del SDK ─────────────────────────────────────────
    def handle_events(self, events: list) -> None:
        """Gestiona los eventos recibidos por el SDK (NO llamar pygame.event.get())."""
        for event in events:
            # Espacio → liberar pelota si está pegada
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self._game_state == "game" and self._game.ball.stuck:
                        self._game.ball.stuck   = False
                        self._game.ball.speed_y = -settings.BALL_SPEED

            # Clicks de ratón
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(pygame.mouse.get_pos())

    def update(self, dt: float) -> None:
        """Actualiza la lógica del juego. dt = tiempo en segundos desde el último frame."""
        if self._game_state == "menu":
            return

        if self._game_state == "game":
            if self._game_slide_y > 0:
                self._game_slide_y -= 20
                return

            self._game.update()
            self._game.handle_collisions()
            self._game.update_effects()

            if self._game.finished:
                self._game_state = "level_complete"
            if self._game.lost:
                self._game_state = "game_over"

        # Animación de fade de transición
        if self._transitioning:
            self._fade_alpha += 10
            if self._fade_alpha >= 255:
                self._fade_alpha   = 255
                self._transitioning = False
                self._game_state   = "game"

    def render(self) -> None:
        """Dibuja el frame actual. El SDK llama este método sin argumentos;
        la surface se obtiene de self.surface (propiedad de GameBase)."""
        surface = self.surface   # ← propiedad que el SDK asigna en start()

        if self._game_state == "menu":
            self._menu.draw(surface)
            surface.blit(self._button_info, self._button_info_rect)

        elif self._game_state == "info":
            surface.blit(self._info_image, (0, 0))
            surface.blit(self._button_close, self._button_close_rect)

        elif self._game_state == "game":
            if self._game_slide_y > 0:
                surface.blit(self._game.background, (0, self._game_slide_y))
            else:
                self._game.draw(surface)

            # Fade overlay al inicio
            if self._transitioning:
                fade_surf = pygame.Surface((settings.WIDTH, settings.HEIGHT))
                fade_surf.fill((0, 0, 0))
                fade_surf.set_alpha(self._fade_alpha)
                surface.blit(fade_surf, (0, 0))

        elif self._game_state == "level_complete":
            self._game.draw(surface)

            if self._game.level == len(self._game.levels) - 1:
                title      = "¡FELICIDADES!"
                score_text = f"Completaste el juego con {self._game.score} puntos"
            else:
                title      = "NIVEL COMPLETADO!"
                score_text = f"Puntos obtenidos: {self._game.score}"

            elements.draw_overlay(surface, title, score_text)

            if self._game.level < len(self._game.levels) - 1:
                surface.blit(self._button_proximo, self._button_proximo_rect)
            surface.blit(self._button_menu, self._button_menu_rect)

        elif self._game_state == "game_over":
            self._game.draw(surface)
            elements.draw_overlay(surface, "GAME OVER", f"Puntos obtenidos: {self._game.score}")
            surface.blit(self._button_reiniciar, self._button_reiniciar_rect)
            surface.blit(self._button_menu, self._button_menu_rect)

    # ── Helpers privados ──────────────────────────────────────────────────────
    def _play_menu_music(self):
        pygame.mixer.music.load(str(ASSETS_DIR / "music" / "musica_menu.mp3"))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def _handle_click(self, mouse_pos):
        if self._game_state == "menu":
            self._play_menu_music()

            if self._menu.check_click(mouse_pos):
                self._click_sound.play()
                pygame.mixer.music.fadeout(500)
                self._transitioning = True
                self._fade_alpha    = 0
                self._game_state    = "game"
                self._game_slide_y  = settings.HEIGHT

            if self._button_info_rect.collidepoint(mouse_pos):
                self._click_sound.play()
                self._game_state = "info"

        elif self._game_state == "info":
            if self._button_close_rect.collidepoint(mouse_pos):
                self._click_sound.play()
                self._game_state = "menu"

        elif self._game_state == "level_complete":
            if self._button_proximo_rect.collidepoint(mouse_pos):
                if self._game.level < len(self._game.levels) - 1:
                    self._click_sound.play()
                    self._game.next_level()
                    self._game_state = "game"

            if self._button_menu_rect.collidepoint(mouse_pos):
                self._click_sound.play()
                self._game = Game()
                self._game_state = "menu"
                self._play_menu_music()

        elif self._game_state == "game_over":
            if self._button_reiniciar_rect.collidepoint(mouse_pos):
                self._click_sound.play()
                self._game.restart_level()
                self._game_state = "game"

            if self._button_menu_rect.collidepoint(mouse_pos):
                self._click_sound.play()
                self._game = Game()
                self._game_state = "menu"
                self._play_menu_music()


# ──────────────────────────────────────────────────────────────────────────────
# Punto de entrada para ejecución independiente (desarrollo / pruebas)
# ──────────────────────────────────────────────────────────────────────────────
game = BreakoutGame(metadata)

if __name__ == "__main__":
    game.run_independently()
