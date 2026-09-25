import pygame

from scenes import basic_scene, game_scene, game_scene_2, death_scene, shop_scene, logros_scene, notificaciones

ARCHIVO_GUARDADO = "progreso.txt"

def cargar_progreso():
    try:
        with open(ARCHIVO_GUARDADO, "r") as archivo:
            lineas = archivo.readlines()
            max_puntaje = int(lineas[0].strip())
            nivel_2_desbloqueado = lineas[1].strip() == "True"
            coins = int(lineas[2].strip())
            return max_puntaje, nivel_2_desbloqueado, coins
    except FileNotFoundError:
        return 0, False, 0

def guardar_progreso(max_puntaje, nivel_2_desbloqueado, coins):
    with open(ARCHIVO_GUARDADO, "w") as archivo:
        archivo.write(f"{max_puntaje}\n")
        archivo.write(f"{nivel_2_desbloqueado}\n")
        archivo.write(f"{coins}")

ARCHIVO_ESTADISTICAS = "estadisticas.txt"

def cargar_estadisticas():
    try:
        with open(ARCHIVO_ESTADISTICAS, "r") as archivo:
            lineas = archivo.readlines()
            nivel_vida = int(lineas[0].strip())
            nivel_balas = int(lineas[1].strip())
            return nivel_vida, nivel_balas
    except FileNotFoundError:
        return 0, 0

def guardar_estadisticas(nivel_vida, nivel_balas):
    with open(ARCHIVO_ESTADISTICAS, "w") as archivo:
        archivo.write(f"{nivel_vida}\n")
        archivo.write(f"{nivel_balas}")

ARCHIVO_LOGROS = "logros.txt"

def cargar_logros():
    try:
        with open(ARCHIVO_LOGROS, "r") as archivo:
            return [linea.strip() == "True" for linea in archivo.readlines()]
    except FileNotFoundError:
        return [False] * 12

def guardar_logros(logros):
    with open(ARCHIVO_LOGROS, "w") as archivo:
        for logro in logros:
            archivo.write(f"{logro}\n")

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

max_puntaje, nivel_2_desbloqueado, coins = cargar_progreso()
nivel_vida, nivel_balas = cargar_estadisticas()
logros = cargar_logros()

# ? Aqui se ejecutaran las escenas del juego en orden
running = True

while running:

    screen = pygame.display.get_surface()

    resultado_menu = basic_scene.gameloop(screen, nivel_2_desbloqueado)

    if resultado_menu == "quit":
        break

    if resultado_menu == "shop":

        screen = pygame.display.get_surface()
        resultado_tienda, coins, nivel_vida, nivel_balas = shop_scene.gameloop(screen, coins, nivel_vida, nivel_balas)

        guardar_progreso(max_puntaje, nivel_2_desbloqueado, coins)
        guardar_estadisticas(nivel_vida, nivel_balas)

        if nivel_vida >= 10 and not logros[4]:
            logros[4] = True
            notificaciones.mostrar(4)
        if nivel_balas >= 10 and not logros[5]:
            logros[5] = True 
            notificaciones.mostrar(5)

        guardar_logros(logros)

        if resultado_tienda == "quit":
            break

        continue
    if resultado_menu == "logros":

        screen = pygame.display.get_surface()
        resultado_logros = logros_scene.gameloop(screen, logros)

        if resultado_logros == "quit":
            break

        continue

    #---- FEATURE PROGRESION DE NIVELES - ELEGIR NIVEL ----
    
    if isinstance(resultado_menu, tuple):

        nivel_actual, cantidad_jugadores = resultado_menu
        jugando = True

        while jugando:

            screen = pygame.display.get_surface()

            if nivel_actual == "level1":
                resultado = game_scene.gameloop(screen, cantidad_jugadores, nivel_vida, nivel_balas)

            else:
                resultado = game_scene_2.gameloop(screen, cantidad_jugadores, nivel_vida, nivel_balas)

            screen = pygame.display.get_surface()

            #---- FEATURE MENU PAUSA - VOLVER AL MENU PRINCIPAL ----
            if resultado == "menu":
                jugando = False
                continue
            #----

            if isinstance(resultado, tuple) and resultado[0] == "dead":

                estadistica = resultado[1]
                coins += estadistica

                if estadistica > max_puntaje:
                    max_puntaje = estadistica
                
                if estadistica >= 500:
                    nivel_2_desbloqueado = True

                guardar_progreso(max_puntaje, nivel_2_desbloqueado, coins)

                logros[0] = True  # Primeros pasos (Jugar 1 partida)
                
                if estadistica >= 500 and not logros[1]:
                    logros[1] = True
                    notificaciones.mostrar(1)
                if estadistica >= 1000 and not logros[2]:
                    logros[2] = True
                    notificaciones.mostrar(2)
                if coins >= 100 and not logros[3]:
                    logros[3] = True 
                    notificaciones.mostrar(3)
                if estadistica < 10 and not logros[9]:
                    logros[9] = True 
                    notificaciones.mostrar(9)
                
                guardar_logros(logros)

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