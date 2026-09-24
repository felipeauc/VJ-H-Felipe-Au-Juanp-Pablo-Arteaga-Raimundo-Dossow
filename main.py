import pygame

from scenes import basic_scene, game_scene, game_scene_2, death_scene, shop_scene


# ? Inicializamos pygame
pygame.init()

#---- FEATURE MUSICA Y SONIDO - INICIALIZAR AUDIO ----
if not pygame.mixer.get_init():
    pygame.mixer.init()
#----

# ? Definimos las medidas de nuestra pantalla
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# ? Creamos nuestro objeto pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

nivel_2_desbloqueado = False

# ? Aqui se ejecutaran las escenas del juego en orden
running = True

while running:

    screen = pygame.display.get_surface()

    resultado_menu = basic_scene.gameloop(screen, nivel_2_desbloqueado)

    if resultado_menu == "quit":
        break

    if resultado_menu == "shop":

        screen = pygame.display.get_surface()
        resultado_tienda = shop_scene.gameloop(screen)

        if resultado_tienda == "quit":
            break

        continue

    #---- FEATURE PROGRESION DE NIVELES - ELEGIR NIVEL ----
    if resultado_menu == "level1" or resultado_menu == "level2":

        nivel_actual = resultado_menu
        jugando = True

        while jugando:

            screen = pygame.display.get_surface()

            if nivel_actual == "level1":
                resultado = game_scene.gameloop(screen)

            else:
                resultado = game_scene_2.gameloop(screen)

            screen = pygame.display.get_surface()

            #---- FEATURE MENU PAUSA - VOLVER AL MENU PRINCIPAL ----
            if resultado == "menu":
                jugando = False
                continue
            #----

            if isinstance(resultado, tuple) and resultado[0] == "dead":
                estadistica = resultado[1]
                
                if estadistica >= 500:
                    nivel_2_desbloqueado = True

                resultado_muerte = death_scene.gameloop(screen, estadistica)

                if resultado_muerte == "retry":
                    continue

                if resultado_muerte == "quit":
                    running = False

                jugando = False

            elif resultado == "quit":
                running = False
                jugando = False
    #----

pygame.quit()