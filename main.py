import pygame

from scenes import basic_scene, game_scene, game_scene_2, death_scene, shop_scene

ARCHIVO_GUARDADO = "progreso.txt"

def cargar_progreso():
    try:
        with open(ARCHIVO_GUARDADO, "r") as archivo:
            lineas = archivo.readlines()
            max_puntaje = int(lineas[0].strip())
            nivel_2_desbloqueado = lineas[1].strip() == "True"
            return max_puntaje, nivel_2_desbloqueado
    except FileNotFoundError:
        return 0, False

def guardar_progreso(max_puntaje, nivel_2_desbloqueado):
    with open(ARCHIVO_GUARDADO, "w") as archivo:
        archivo.write(f"{max_puntaje}\n")
        archivo.write(f"{nivel_2_desbloqueado}\n")

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

max_puntaje, nivel_2_desbloqueado = cargar_progreso()

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
                    hubo_cambios = True
                else:
                    hubo_cambios = False

                if hubo_cambios:
                    guardar_progreso(max_puntaje, nivel_2_desbloqueado)

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