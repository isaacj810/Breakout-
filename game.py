import pygame
from elements import Paddle, Ball, Block, create_level
from elements import LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, LEVEL_6, LEVEL_7, LEVEL_8, LEVEL_9, LEVEL_10
from powers import PowerUp
import random



class Game:
    def __init__(self):
        bg = pygame.image.load("assets/fondo_juego.png")
        self.background = pygame.transform.scale(bg, (1080, 720))
        self.game_objects = []
        self.paddle = Paddle()
        self.ball = Ball()




  #////////////////////////// SISTEMA DE NIVELES /////////////////////////////
        self.levels = [LEVEL_1, LEVEL_2, LEVEL_3, LEVEL_4, LEVEL_5, LEVEL_6, LEVEL_7, LEVEL_8, LEVEL_9, LEVEL_10]
        self.level = 0
        self.blocks = create_level(self.levels[self.level])

        self.game_objects = [self.paddle, self.ball]
        self.game_objects.extend(self.blocks)
      

        self.score = 0
        self.level_start_score = 0
        self.font = pygame.font.Font("assets/StackedStrong-Regular.otf", 32)

        self.finished = False
        self.lost = False

        self.powerups = []
        self.active_effects = {}
        self.effect_duration = 10000  # 10 segundos en milisegundos

        self.power_sound = pygame.mixer.Sound("assets/music/sonido_powerup.mp3")
        self.power_sound.set_volume(0.7)
        self.hit_sound = pygame.mixer.Sound("assets/music/sonido_hit.mp3")
        self.hit_sound.set_volume(0.6)


    # -----------------------------
    def update(self):

        self.paddle.move()

        if self.ball.stuck:
            self.ball.rect.centerx = self.paddle.rect.centerx
            self.ball.rect.bottom = self.paddle.rect.top
        else:
            self.ball.move()
            self.ball.check_paddle_collision(self.paddle)

        if self.ball.is_lost():
            self.lost = True

        for power in self.powerups[:]:
            power.update()

            
            if power.rect.colliderect(self.paddle.rect):
                self.activate_power(power.type)
                self.powerups.remove(power)
                if power in self.game_objects:
                    self.game_objects.remove(power)
                self.power_sound.play()

            elif power.rect.top > 720:
                self.powerups.remove(power)
                if power in self.game_objects:
                    self.game_objects.remove(power)

        self.update_effects()
    # -----------------------------
    def handle_collisions(self):
        self.ball.check_paddle_collision(self.paddle)
        for block in self.blocks:
            if block.alive and self.ball.rect.colliderect(block.rect):
                self.hit_sound.play()
                self.ball.speed_y *= -1
                block.hit(self.ball.damage)

                if not block.alive:
                    points = 10
                    if "x2" in self.active_effects:
                        points *= 2
                    self.score += points

                    if random.random() < 0.1:
                        power = PowerUp(block.rect.centerx, block.rect.centery)
                        self.powerups.append(power)
                        self.game_objects.append(power)

        if self.is_level_complete():
            self.finished = True

    def restart_level(self):
        self.blocks = create_level(self.levels[self.level])
        self.game_objects = [self.paddle, self.ball]
        self.game_objects.extend(self.blocks)
        self.ball.reset()
        self.paddle.rect.centerx = 540

        self.score = self.level_start_score   # 🔥 restaurar puntos

        self.powerups.clear()
        self.active_effects.clear()

        self.lost = False
        self.finished = False
        self.active_effects.clear()        



    # -----------------------------
    def is_level_complete(self):
        for block in self.blocks:
            if block.alive:
                return False
        return True

    # -----------------------------
    def next_level(self):
        self.level += 1

        if self.level < len(self.levels):
            self.blocks = create_level(self.levels[self.level])
            self.game_objects = [self.paddle, self.ball]
            self.game_objects.extend(self.blocks)
            self.powerups.clear()
            self.level_start_score = self.score
        else:
            print("Juego completado")
            self.level = 0
            self.score = 0
            self.blocks = create_level(self.levels[self.level])
            self.powerups.clear()
            self.active_effects.clear()

        self.ball.reset()
        self.paddle.rect.centerx = 540
        self.finished = False


    # -----------------------------
    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        for obj in self.game_objects:
            obj.draw(screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 10))


    def activate_power(self, power_type):
        current_time = pygame.time.get_ticks()

        self.active_effects[power_type] = current_time

        if power_type == "x2":
            print("Multiplicador x2 activado")

        elif power_type == "slow":
            self.ball.speed_x *= 0.5
            self.ball.speed_y *= 0.5

        elif power_type == "small_paddle":
            center = self.paddle.rect.center
            self.paddle.image = pygame.transform.scale(
                pygame.image.load("assets/plataforma.png"),
                (120, 30)
            )
            self.paddle.rect = self.paddle.image.get_rect()
            self.paddle.rect.center = center

        elif power_type == "fast_ball":
            self.ball.speed_x *= 1.5
            self.ball.speed_y *= 1.5

        elif power_type == "damage":
            self.ball.damage = 3
        
        elif power_type == "sticky":
            self.ball.sticky = True

    def update_effects(self):
        current_time = pygame.time.get_ticks()

        for effect in list(self.active_effects):
            if current_time - self.active_effects[effect] > self.effect_duration:

                if effect == "slow":
                    self.ball.speed_x *= 2
                    self.ball.speed_y *= 2

                elif effect == "small_paddle":
                    center = self.paddle.rect.center
                    self.paddle.image = pygame.transform.scale(
                        pygame.image.load("assets/plataforma.png"),
                        (180, 30)
                    )
                    self.paddle.rect = self.paddle.image.get_rect()
                    self.paddle.rect.center = center

                elif effect == "fast_ball":
                    self.ball.speed_x /= 1.5
                    self.ball.speed_y /= 1.5

                elif effect == "damage":
                    self.ball.damage = 1

                elif effect == "sticky":
                    self.ball.sticky = False

                del self.active_effects[effect]

                