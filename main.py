import pygame

from scenes import basic_scene, game_scene, death_scene

# ? Inicializamos pygame
pygame.init()

# ? Definimos las medidas de nuestra pantalla
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# ? Creamos nuestro objeto pantalla
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# ? Aqui se ejecutaran las escenas del juego en orden
basic_scene.gameloop(screen)
while True:

    resultado = game_scene.gameloop(screen)

    if resultado == "dead":

        resultado_muerte = death_scene.gameloop(screen)

        if resultado_muerte == "retry":
            continue

    break
