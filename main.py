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

import logros


ARCHIVO_GUARDADO = "progreso.txt"


def cargar_progreso():

    try:

        with open(
            ARCHIVO_GUARDADO,
            "r"
        ) as archivo:

            lineas = archivo.readlines()

        max_puntaje = int(
            lineas[0].strip()
        )

        nivel_2_desbloqueado = (
            lineas[1].strip()
            == "True"
        )

        coins = int(
            lineas[2].strip()
        )

        return (
            max_puntaje,
            nivel_2_desbloqueado,
            coins
        )

    except (
        FileNotFoundError,
        ValueError,
        IndexError
    ):

        return (
            0,
            False,
            0
        )


def guardar_progreso(
    max_puntaje,
    nivel_2_desbloqueado,
    coins
):

    with open(
        ARCHIVO_GUARDADO,
        "w"
    ) as archivo:

        archivo.write(
            f"{max_puntaje}\n"
        )

        archivo.write(
            f"{nivel_2_desbloqueado}\n"
        )

        archivo.write(
            f"{coins}"
        )


# ==========================================
# PYGAME
# ==========================================

pygame.init()

if not pygame.mixer.get_init():
    pygame.mixer.init()


SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

screen = pygame.display.set_mode(
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
)


# esto permite que las notificaciones
# aparezcan en TODAS las escenas
notificaciones.instalar_overlay()


# conecta Player y Player2 al sistema de logros
logros.instalar_hooks()


max_puntaje, nivel_2_desbloqueado, coins = (
    cargar_progreso()
)


# comprobar progreso que ya existia
logros.revisar_historico(
    max_puntaje,
    coins
)


running = True


while running:

    screen = pygame.display.get_surface()


    resultado_menu = basic_scene.gameloop(
        screen,
        nivel_2_desbloqueado
    )


    # ======================================
    # SALIR
    # ======================================

    if resultado_menu == "quit":
        break


    # ======================================
    # TIENDA
    # ======================================

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


        if resultado_tienda == "quit":
            break


        continue


    # ======================================
    # LOGROS
    # ======================================

    if resultado_menu == "logros":

        screen = pygame.display.get_surface()

        resultado_logros = logros_scene.gameloop(
            screen
        )


        if resultado_logros == "quit":
            break


        continue


    # ======================================
    # NIVEL
    # ======================================

    if isinstance(
        resultado_menu,
        tuple
    ):

        nivel_actual, cantidad_jugadores = (
            resultado_menu
        )

        jugando = True


        while jugando:

            screen = pygame.display.get_surface()


            # cada retry cuenta como una nueva partida
            logros.iniciar_partida()


            if nivel_actual == "level1":

                resultado = game_scene.gameloop(
                    screen,
                    cantidad_jugadores
                )


            elif nivel_actual == "level2":

                resultado = game_scene_2.gameloop(
                    screen,
                    cantidad_jugadores
                )


            elif nivel_actual == "level3":

                resultado = game_scene_3.gameloop(
                    screen,
                    cantidad_jugadores
                )


            else:

                jugando = False

                continue


            screen = pygame.display.get_surface()


            # ==================================
            # MENU
            # ==================================

            if resultado == "menu":

                jugando = False

                continue


            # ==================================
            # VICTORIA
            # ==================================

            if (
                isinstance(
                    resultado,
                    tuple
                )
                and resultado[0]
                == "victory"
            ):

                estadistica = resultado[1]


                # revisar logros de esa partida
                logros.finalizar_partida(
                    estadistica,
                    murio=False
                )


                coins += estadistica


                # logro de coins
                logros.revisar_coins(
                    coins
                )


                if estadistica > max_puntaje:

                    max_puntaje = (
                        estadistica
                    )


                if estadistica >= 500:

                    nivel_2_desbloqueado = True


                guardar_progreso(
                    max_puntaje,
                    nivel_2_desbloqueado,
                    coins
                )


                jugando = False

                continue


            # ==================================
            # MUERTE
            # ==================================

            if (
                isinstance(
                    resultado,
                    tuple
                )
                and resultado[0]
                == "dead"
            ):

                estadistica = resultado[1]


                # revisa los 12 logros
                logros.finalizar_partida(
                    estadistica,
                    murio=True
                )


                coins += estadistica


                logros.revisar_coins(
                    coins
                )


                if estadistica > max_puntaje:

                    max_puntaje = (
                        estadistica
                    )


                if estadistica >= 500:

                    nivel_2_desbloqueado = True


                guardar_progreso(
                    max_puntaje,
                    nivel_2_desbloqueado,
                    coins
                )


                resultado_muerte = death_scene.gameloop(
                    screen,
                    estadistica
                )


                if resultado_muerte == "retry":

                    continue


                if resultado_muerte == "quit":

                    running = False


                jugando = False


            elif resultado == "quit":

                running = False
                jugando = False


pygame.quit()