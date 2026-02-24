import pygame
import random
import settings

pygame.init()
################################# FUENTE ##############################################

font_big = pygame.font.Font("assets/StackedStrong-Regular.otf", 72)
font_medium = pygame.font.Font("assets/StackedStrong-Regular.otf", 40)
font_small = pygame.font.Font("assets/StackedStrong-Regular.otf", 28)


# ============================= PALETA =============================
class Paddle:
    def __init__(self):
        self.image = pygame.image.load("assets/plataforma.png")
        self.image = pygame.transform.scale(self.image, (180, 30))

        self.rect = self.image.get_rect()
        self.rect.centerx = 540
        self.rect.y = 650

        self.speed = 8

        self.sticky = False
        self.stuck = False

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        # Mantener dentro de la pantalla
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1080:
            self.rect.right = 1080

    def draw(self, screen):
        screen.blit(self.image, self.rect)

# ============================= PELOTA =============================
class Ball:
    def __init__(self):
        self.image = pygame.image.load("assets/pelota.png")
        self.image = pygame.transform.scale(self.image, (24, 24))

        self.base_speed_x = 6
        self.base_speed_y = -6


        self.rect = self.image.get_rect()
        self.reset()
        self.damage = 1

        self.sticky = False
        self.stuck = False
        
    def reset(self):
        self.rect.center = (540, 500)
        self.speed_x = self.base_speed_x
        self.speed_y = self.base_speed_y

    def move(self):

        if self.stuck:
            return

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # ----- PARED IZQUIERDA -----
        if self.rect.left <= 0:
            self.rect.left = 0
            self.speed_x *= -1

        # ----- PARED DERECHA -----
        if self.rect.right >= 1080:
            self.rect.right = 1080
            self.speed_x *= -1

        # ----- TECHO -----
        if self.rect.top <= 0:
            self.rect.top = 0
            self.speed_y *= -1
    
    def check_paddle_collision(self, paddle):
        if self.rect.colliderect(paddle.rect):

            # 🔥 Si el poder sticky está activo
            if self.sticky:
                self.stuck = True
                self.speed_x = 0
                self.speed_y = 0
                self.rect.bottom = paddle.rect.top
                return

            # Rebote normal
            offset = (self.rect.centerx - paddle.rect.centerx)
            normalized = offset / (paddle.rect.width / 2)

            self.speed_x = normalized * 8
            self.speed_y = -abs(self.speed_y)

            self.rect.bottom = paddle.rect.top

        

    def is_lost(self):
        return self.rect.top > 720




    def draw(self, screen):
        screen.blit(self.image, self.rect)
# ============================= BLOQUES =============================
BLOCK_WIDTH = 90
BLOCK_HEIGHT = 36

class Block:
    def __init__(self, x, y, color, hits):
        self.hits = hits
        self.alive = True

        img1 = pygame.image.load(f"assets/bricks/{color}_1.png")
        img2 = pygame.image.load(f"assets/bricks/{color}_1.5.png")
        img3 = pygame.image.load(f"assets/bricks/{color}_2.png")

        self.image_normal = pygame.transform.scale(img1, (BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image_hit = pygame.transform.scale(img2, (BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image_damaged = pygame.transform.scale(img3, (BLOCK_WIDTH, BLOCK_HEIGHT))

        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))

    def hit(self, damage):
        self.hits -= damage

        if self.hits == 2:
            self.image = self.image_hit
        elif self.hits == 1:
            self.image = self.image_damaged

        if self.hits <= 0:
            self.alive = False

    def draw(self, screen):
        if self.alive:
            screen.blit(self.image, self.rect)


################################# FUNCION PARA CREAR EL NIVEL ##############################################

def create_level(layout):
    blocks = []

    start_x = 60
    start_y = 80
    gap = 6

    for row, line in enumerate(layout):
        for col, symbol in enumerate(line):
            if symbol != ".":
                data = BLOCK_TYPES[symbol]

                x = start_x + col * (BLOCK_WIDTH + gap)
                y = start_y + row * (BLOCK_HEIGHT + gap)

                blocks.append(Block(x, y, data["color"], data["hits"]))

    return blocks
################################# NIVELES ##############################################
# IMPORTANTE EN CADA FILA DEBE HABER EXACTAMENTE 10 CARACTERES, ES DECIR 10 BLOQUES
LEVEL_1 = [
   "..........",
    "ACCAFFACCA",
    "BOOBFFBOOB",
    "QAAPPPPPAQ",
    "HHGLLLLGHH",
  
 
    
]

LEVEL_2 = [
    "CMMCCCCMMC",
    "CSSSSSSSSC",
    "C.N.MM.N.C",
    "C..N..N..C",
    "C..MMMM..C",
    "CSSSSSSSSC",
    "CMMCCCCMMC",
]

LEVEL_3 = [
    "....DD....",
    "...DJJD...",
    "..DDDDDD..",
    ".DANNNNAD.",
    "DDDDMMDDDD",
    ".DANNNNAD.",
    "..DDJJDD..",
    "...DDDD...",
]

LEVEL_4 = [
   "....EE....",
    "A..EEEE..A",
    "..EEFFEE..",
    "...LEEL...",
    "A...EE...A",
    "...LEEL...",
    "..EEFFEE..",
    "A..EEEE..A",
]

LEVEL_5 = [
    "FFFFFFFFFF",
    "...JJJJ...",
    "GGGGGGGGGG",
    "..........",
    "FFFFFFFFFF",
    "...HHHH...",
    "GGGGGGGGGG",
    "..........",
    "FFFFFFFFFF",
]

LEVEL_6 = [
    "HHHH....QQ",
    "..HHHH....",
    "QQ..HHHH..",
    "......HHHH",
    "HHHH....QQ",
    "..HHHH....",   
    "....HHHH..",
    "QQ....HHHH",
]

LEVEL_7 = [
    "IIIIIIIIII",
    "I..JJJJ..I",
    "I..JKKJ..I",
    "I..JJJJ..I",
    "I...JJJJ..I",
    "I..JKKJ..I",
    "I..JJJJ..I",
    "IIIIIIIIII",

]

LEVEL_8 = [
    "LLLLLLLLLL",
    "L..MMMM..L",
    "L..M..M..L",
    "L..MMMM..L",
    "L..MMMM..L",
    "L..M..M..L",
    "L..MMMM..L",
    "LLLLLLLLLL",
]
LEVEL_9 = [
    "NNNNNNNNNN",
    "AS.OOOO.SA",
    "...OOOO...",
    "AS.OOOO.SA",
    "..OOOOOO...",
    "AS.OOOO.SA",
    "...OOOO...",
    "AS.OOOO.SA",
]

LEVEL_10 = [
    "PPPPPPPPPP",
    "PQQQQQQQQP",
    "PQRRRRRRQP",
    "PQQQQQQQQP",
    "PQQQQQQQQP",
    "PQRRRRRRQP",
    "PQQQQQQQQP",
    "PPPPPPPPPP",
]


# ============================= TIPOS DE BLOQUES =============================
BLOCK_TYPES = {
    "A": {"color": "rojo",   "hits": 2},
    "B": {"color": "amarillo",  "hits": 2},
    "C": {"color": "azul",   "hits": 2},
    "D": {"color": "azuloscuro",   "hits": 3},
    "F": {"color": "azulpantano",   "hits": 3},
    "G": {"color": "cian",   "hits": 3},
    "H": {"color": "gelatina",   "hits": 3},
    "I": {"color": "lima",   "hits": 2},
    "J": {"color": "marron",   "hits": 2},
    "K": {"color": "morado",   "hits": 2},
    "L": {"color": "naranja",   "hits": 2},
    "M": {"color": "naranjabrillante",   "hits": 3},
    "N": {"color": "negro",   "hits": 3},
    "O": {"color": "platiado",   "hits": 3},
    "P": {"color": "rosa",   "hits": 2},
    "Q": {"color": "verde",   "hits": 2},
    "R": {"color": "verdeclaro",   "hits": 3},
    "S": {"color": "violeta",   "hits": 2},
    
}

# ============================= OVERLAY DE NIVEL COMPLETADO Y GAME OVER =============================

def draw_overlay(screen, title_text, score_text):
    # Capa oscura
    overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(180)  # transparencia
    screen.blit(overlay, (0, 0))

    # Texto principal
    title_surface = font_big.render(title_text, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2 - 60))
    screen.blit(title_surface, title_rect)

    # Texto puntos
    score_surface = font_medium.render(score_text, True, (255, 255, 255))
    score_rect = score_surface.get_rect(center=(settings.WIDTH//2, settings.HEIGHT//2))
    screen.blit(score_surface, score_rect)