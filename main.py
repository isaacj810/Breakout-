import pygame
import sys
from menu import Menu
from game import Game
import elements

pygame.init()

WIDTH = 1080
HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")

icono = pygame.image.load("assets/icono.png")
pygame.display.set_icon(icono)

clock = pygame.time.Clock()

################################# FUENTE ##############################################

font_big = pygame.font.Font("assets/StackedStrong-Regular.otf", 72)
font_medium = pygame.font.Font("assets/StackedStrong-Regular.otf", 40)
font_small = pygame.font.Font("assets/StackedStrong-Regular.otf", 28)


################################# MUSICA ##############################################

pygame.mixer.init()
pygame.mixer.music.load("assets/music/musica_menu.mp3")
pygame.mixer.music.set_volume(0.5)  
pygame.mixer.music.play(-1)        

def play_menu_music():
    pygame.mixer.music.load("assets/music/musica_menu.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)

click_sound = pygame.mixer.Sound("assets/music/click_boton.mp3")
click_sound.set_volume(0.7)


################################# PANTALLAS ##############################################

menu = Menu()
game = Game()
game_state = "menu"   

# Variables para la transición
transitioning = False
fade_alpha = 0
game_y = 720   


info_image = pygame.image.load("assets/pantalla_información.png")
info_image = pygame.transform.scale(info_image, (1080, 720))


################################# BOTONES #############################################
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50

button_menu = pygame.image.load("assets/boton_menú.png")
button_menu = pygame.transform.scale(button_menu, (BUTTON_WIDTH, BUTTON_HEIGHT))
button_menu_rect = button_menu.get_rect(center=(540, 530))

button_reiniciar = pygame.image.load("assets/boton_reiniciar.png")
button_reiniciar = pygame.transform.scale(button_reiniciar, (BUTTON_WIDTH, BUTTON_HEIGHT))
button_reiniciar_rect = button_reiniciar.get_rect(center=(540, 450))

button_proximo = pygame.image.load("assets/boton_próximo.png")
button_proximo = pygame.transform.scale(button_proximo, (BUTTON_WIDTH, BUTTON_HEIGHT))
button_proximo_rect = button_proximo.get_rect(center=(540, 450))

button_info = pygame.image.load("assets/boton_!.png")
button_info = pygame.transform.scale(button_info, (50, 50))
button_info_rect = button_info.get_rect(topright=(1060, 20))

button_close = pygame.image.load("assets/boton_x.png")
button_close = pygame.transform.scale(button_close, (50, 50))
button_close_rect = button_close.get_rect(topright=(1060, 20))

################################# BUCLE PRINCIPAL ##############################################

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.ball.stuck:
                    game.ball.stuck = False
                    game.ball.speed_y = -6
                        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu":
                play_menu_music()
                if menu.check_click(pygame.mouse.get_pos()):
                    click_sound.play()
                    pygame.mixer.music.fadeout(500)
                    transitioning = True
                    fade_alpha = 0
                    game_state = "game"   
                    game_y = 720

                if button_info_rect.collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    game_state = "info"

            elif game_state == "info":
                if button_close_rect.collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    game_state = "menu"

            # ================= LEVEL COMPLETE =================
            elif game_state == "level_complete":

                if button_proximo_rect.collidepoint(pygame.mouse.get_pos()):
                    if game.level < 4:  
                        click_sound.play()
                        game.next_level()
                        game_state = "game"

                if button_menu_rect.collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    game = Game()
                    game_state = "menu"
                    play_menu_music()

            # ================= GAME OVER =================
            elif game_state == "game_over":

                if button_reiniciar_rect.collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    game.restart_level()
                    game_state = "game"

                if button_menu_rect.collidepoint(pygame.mouse.get_pos()):
                    click_sound.play()
                    game = Game()
                    game_state = "menu"
                    play_menu_music()


################################# MENU ##############################################
    if game_state == "menu":
        menu.draw(screen)
        screen.blit(button_info, button_info_rect)
    elif game_state == "info":
        screen.blit(info_image, (0, 0))
        screen.blit(button_close, button_close_rect)    

################################# JUEGO ##############################################
    elif game_state == "game":
        
        if game_y > 0:
            game_y -= 20
            screen.blit(game.background, (0, game_y))
        else:
            game.update()
            game.handle_collisions()
            game.update_effects() 
            game.draw(screen)

            if game.finished:
                game_state = "level_complete"

            if game.lost:
                game_state = "game_over"

################################# PANTALLA PROXIMO NIVEL #####################################
    elif game_state == "level_complete":
        game.draw(screen)

        if game.level == 4:  
            title = "FELICIDADES!"
            score_text = f"Completaste el juego con {game.score} puntos"
            elements.draw_overlay(screen, title, score_text)
        else:
            title = "NIVEL COMPLETADO!"
            score_text = f"Puntos obtenidos: {game.score}"
            elements.draw_overlay(screen, title, score_text)
            screen.blit(button_proximo, button_proximo_rect)
       
        screen.blit(button_menu, button_menu_rect)

        
################################# PANTALLAGAME OVER ##########################################
    elif game_state == "game_over":
        game.draw(screen)
        title = "GAME OVER"
        score_text = f"Puntos obtenidos: {game.score}" 

        elements.draw_overlay(screen, title, score_text)
        screen.blit(button_reiniciar, button_reiniciar_rect)
        screen.blit(button_menu, button_menu_rect)
 

################################# TRANSICION DE FONDO ##########################################
    

    if transitioning:
        fade_alpha += 10

        if fade_alpha >= 255:
            fade_alpha = 255
            transitioning = False
            game_state = "game"

        fade_surface = pygame.Surface((1080, 720))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))

    


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
