import pygame

from scenes import (
    basic_scene,
    game_scene,
    game_scene_2,
    game_scene_3,
    death_scene,
    shop_scene,
    logros_scene,
    notificaciones
)

import habilidades


ARCHIVO_GUARDADO = "progreso.txt"
ARCHIVO_LOGROS = "logros.txt"


# progreso general
def cargar_progreso():

    try:

        with open(ARCHIVO_GUARDADO, "r") as archivo:
            lineas = archivo.readlines()

        max_puntaje = int(lineas[0].strip())
        nivel_2_desbloqueado = lineas[1].strip() == "True"
        coins = int(lineas[2].strip())

        return max_puntaje, nivel_2_desbloqueado, coins

    except (FileNotFoundError, ValueError, IndexError):

        return 0, False, 0


def guardar_progreso(max_puntaje, nivel_2_desbloqueado, coins):

    with open(ARCHIVO_GUARDADO, "w") as archivo:

        archivo.write(f"{max_puntaje}\n")
        archivo.write(f"{nivel_2_desbloqueado}\n")
        archivo.write(f"{coins}")


# LOGROS
def cargar_logros():

    try:

        with open(ARCHIVO_LOGROS, "r") as archivo:
            logros = [
                linea.strip() == "True"
                for linea in archivo.readlines()
            ]

        # por si el archivo viejo tiene menos logros
        while len(logros) < 12:
            logros.append(False)

        return logros[:12]

    except FileNotFoundError:

        return [False] * 12


def guardar_logros(logros):

    with open(ARCHIVO_LOGROS, "w") as archivo:

        for logro in logros:
            archivo.write(f"{logro}\n")

# iniciar pygame
pygame.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

max_puntaje, nivel_2_desbloqueado, coins = cargar_progreso()

logros = cargar_logros()

running = True


while running:

    screen = pygame.display.get_surface()

    resultado_menu = basic_scene.gameloop(
        screen,
        nivel_2_desbloqueado
    )


    # salir
    if resultado_menu == "quit":
        break


    # ==========================================
    # TIENDA
    # ==========================================

    if resultado_menu == "shop":

        screen = pygame.display.get_surface()

        resultado_tienda, coins = shop_scene.gameloop(
            screen,
            coins
        )


        guardar_progreso(
            max_puntaje,
            nivel_2_desbloqueado,
            coins
        )


        # logro vida al maximo
        if (
            habilidades.niveles["vida"]
            >= habilidades.maximos["vida"]
            and not logros[4]
        ):

            logros[4] = True
            notificaciones.mostrar(4)


        # logro municion al max
        if (
            habilidades.niveles["municion"]
            >= habilidades.maximos["municion"]
            and not logros[5]
        ):

            logros[5] = True
            notificaciones.mostrar(5)


        guardar_logros(logros)


        if resultado_tienda == "quit":
            break


        continue


    # ==========================================
    # LOGROS
    # ==========================================

    if resultado_menu == "logros":

        screen = pygame.display.get_surface()

        resultado_logros = logros_scene.gameloop(
            screen,
            logros
        )


        if resultado_logros == "quit":
            break


        continue


    # ==========================================
    # ELEGIR NIVEL
    # ==========================================

    if isinstance(resultado_menu, tuple):

        nivel_actual, cantidad_jugadores = resultado_menu

        jugando = True


        while jugando:

            screen = pygame.display.get_surface()


            # NIVEL 1
            if nivel_actual == "level1":

                resultado = game_scene.gameloop(
                    screen,
                    cantidad_jugadores
                )


            # NIVEL 2
            elif nivel_actual == "level2":

                resultado = game_scene_2.gameloop(
                    screen,
                    cantidad_jugadores
                )


            # NIVEL 3
            elif nivel_actual == "level3":

                resultado = game_scene_3.gameloop(
                    screen,
                    cantidad_jugadores
                )


            else:

                jugando = False
                continue


            screen = pygame.display.get_surface()


            # ======================================
            # VOLVER AL MENU
            # ======================================

            if resultado == "menu":

                jugando = False
                continue


            # ======================================
            # VICTORIA BOSS
            # ======================================

            if (
                isinstance(resultado, tuple)
                and resultado[0] == "victory"
            ):

                estadistica = resultado[1]

                coins += estadistica


                if estadistica > max_puntaje:
                    max_puntaje = estadistica


                # primera partida
                if not logros[0]:

                    logros[0] = True
                    notificaciones.mostrar(0)


                # 500 puntos
                if estadistica >= 500 and not logros[1]:

                    logros[1] = True
                    notificaciones.mostrar(1)


                # 1000 puntos
                if estadistica >= 1000 and not logros[2]:

                    logros[2] = True
                    notificaciones.mostrar(2)


                # 100 coins
                if coins >= 100 and not logros[3]:

                    logros[3] = True
                    notificaciones.mostrar(3)


                guardar_progreso(
                    max_puntaje,
                    nivel_2_desbloqueado,
                    coins
                )


                guardar_logros(logros)


                jugando = False
                continue


            # ======================================
            # MUERTE
            # ======================================

            if (
                isinstance(resultado, tuple)
                and resultado[0] == "dead"
            ):

                estadistica = resultado[1]

                coins += estadistica


                if estadistica > max_puntaje:
                    max_puntaje = estadistica


                # desbloquear nivel 2
                if estadistica >= 500:
                    nivel_2_desbloqueado = True


                guardar_progreso(
                    max_puntaje,
                    nivel_2_desbloqueado,
                    coins
                )


                # ------------------------------
                # CHECK LOGROS
                # ------------------------------

                # primera partida
                if not logros[0]:

                    logros[0] = True
                    notificaciones.mostrar(0)


                # 500 pts
                if estadistica >= 500 and not logros[1]:

                    logros[1] = True
                    notificaciones.mostrar(1)


                # 1000 pts
                if estadistica >= 1000 and not logros[2]:

                    logros[2] = True
                    notificaciones.mostrar(2)


                # tener 100 coins
                if coins >= 100 and not logros[3]:

                    logros[3] = True
                    notificaciones.mostrar(3)


                # morir con menos de 10
                if estadistica < 10 and not logros[9]:

                    logros[9] = True
                    notificaciones.mostrar(9)


                guardar_logros(logros)


                # pantalla de muerte
                resultado_muerte = death_scene.gameloop(
                    screen,
                    estadistica
                )


                if resultado_muerte == "retry":
                    continue


                if resultado_muerte == "quit":
                    running = False


                jugando = False


            # ======================================
            # CERRAR JUEGO
            # ======================================

            elif resultado == "quit":

                running = False
                jugando = False


pygame.quit()