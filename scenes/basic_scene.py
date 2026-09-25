if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

import customization


def gameloop(screen, nivel_2_desbloqueado=True):

    # Inicializamos el reloj
    clock = pygame.time.Clock()

    running = True

    pygame.mouse.set_visible(True)

    # Definimos la fuente y texto a usar
    font_titulo = pygame.font.Font(None, 85)
    font = pygame.font.Font(None, 45)

    #---- FEATURE MENU INICIO - BOTONES ----
    boton_jugar = pygame.Rect(0, 0, 280, 65)
    boton_tienda = pygame.Rect(0, 0, 280, 65)
    boton_salir = pygame.Rect(0, 0, 280, 65)

    boton_jugar.center = (screen.get_width() // 2, 360)
    boton_tienda.center = (screen.get_width() // 2, 450)
    boton_salir.center = (screen.get_width() // 2, 540)
    #----

    #---- FEATURE PROGRESION DE NIVELES - SELECCION DE NIVEL ----
    seleccionando_nivel = False

    boton_nivel1 = pygame.Rect(0, 0, 280, 60)
    boton_nivel2 = pygame.Rect(0, 0, 280, 60)
    boton_nivel3 = pygame.Rect(0, 0, 280, 60)
    boton_volver_nivel = pygame.Rect(0, 0, 280, 60)

    boton_nivel1.center = (screen.get_width() // 2, 300)
    boton_nivel2.center = (screen.get_width() // 2, 380)
    boton_nivel3.center = (screen.get_width() // 2, 460)
    boton_volver_nivel.center = (screen.get_width() // 2, 540)
    #----

    #---- FEATURE COOPERATIVO - SELECCION DE JUGADORES ----
    seleccionando_jugadores = False
    cantidad_jugadores = 1

    boton_1_jugador = pygame.Rect(0, 0, 280, 65)
    boton_2_jugadores = pygame.Rect(0, 0, 280, 65)
    boton_volver_jugadores = pygame.Rect(0, 0, 280, 65)

    boton_1_jugador.center = (screen.get_width() // 2, 360)
    boton_2_jugadores.center = (screen.get_width() // 2, 450)
    boton_volver_jugadores.center = (screen.get_width() // 2, 540)
    #----

    # Iniciamos el loop principal de la escena inicial
    while running:

        for event in pygame.event.get():

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:

                    if seleccionando_nivel:
                        seleccionando_nivel = False
                        seleccionando_jugadores = True

                    elif seleccionando_jugadores:
                        seleccionando_jugadores = False

                    else:
                        return "quit"

            elif event.type == QUIT:
                return "quit"

            #---- FEATURE MENU INICIO - CLICK BOTONES ----
            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if not seleccionando_nivel and not seleccionando_jugadores:

                        if boton_jugar.collidepoint(event.pos):
                            seleccionando_jugadores = True

                        elif boton_tienda.collidepoint(event.pos):
                            return "shop"

                        elif boton_salir.collidepoint(event.pos):
                            return "quit"

                    #---- FEATURE COOPERATIVO - ELEGIR JUGADORES ----
                    elif seleccionando_jugadores:

                        if boton_1_jugador.collidepoint(event.pos):

                            cantidad_jugadores = 1
                            seleccionando_jugadores = False
                            seleccionando_nivel = True

                        elif boton_2_jugadores.collidepoint(event.pos):

                            cantidad_jugadores = 2
                            seleccionando_jugadores = False
                            seleccionando_nivel = True

                        elif boton_volver_jugadores.collidepoint(event.pos):
                            seleccionando_jugadores = False
                    #----

                    elif seleccionando_nivel:

                        #---- FEATURE PROGRESION DE NIVELES - ELEGIR NIVEL ----
                        if boton_nivel1.collidepoint(event.pos):
                            return ("level1", cantidad_jugadores)

                        elif boton_nivel2.collidepoint(event.pos) and nivel_2_desbloqueado:
                            return ("level2", cantidad_jugadores)

                        elif boton_nivel3.collidepoint(event.pos):
                            return ("level3", cantidad_jugadores)

                        elif boton_volver_nivel.collidepoint(event.pos):

                            seleccionando_nivel = False
                            seleccionando_jugadores = True
                        #----
            #----

        #---- FEATURE MENU INICIO - FONDO PERSONALIZADO ----
        background = pygame.image.load(customization.obtener_asset("Inicio_Back")).convert()
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))

        screen.blit(background, (0, 0))

        sombra = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 145))

        screen.blit(sombra, (0, 0))
        #----

        #---- FEATURE PROGRESION DE NIVELES - BOTONES DEL MENU ----
        if seleccionando_nivel:

            if nivel_2_desbloqueado:
                texto_n2 = "NIVEL 2"

            else:
                texto_n2 = "NIVEL 2 (500 pts)"

            botones = [
                (boton_nivel1, "NIVEL 1"),
                (boton_nivel2, texto_n2),
                (boton_nivel3, "NIVEL 3"),
                (boton_volver_nivel, "VOLVER"),
            ]

        #---- FEATURE COOPERATIVO - BOTONES DE JUGADORES ----
        elif seleccionando_jugadores:

            botones = [
                (boton_1_jugador, "1 JUGADOR"),
                (boton_2_jugadores, "2 JUGADORES"),
                (boton_volver_jugadores, "VOLVER"),
            ]
        #----

        else:

            botones = [
                (boton_jugar, "JUGAR"),
                (boton_tienda, "TIENDA"),
                (boton_salir, "SALIR"),
            ]
        #----

        #---- FEATURE MENU INICIO - DIBUJAR BOTONES ----
        mouse = pygame.mouse.get_pos()

        for boton, texto in botones:

            if seleccionando_nivel and boton == boton_nivel2 and not nivel_2_desbloqueado:

                color = (30, 30, 30)
                borde = (80, 80, 80)
                color_texto = (120, 120, 120)

            else:

                color_texto = (255, 255, 255)
                borde = (255, 215, 80)

                if boton.collidepoint(mouse):
                    color = (255, 205, 60)

                else:
                    color = (40, 45, 55)

            pygame.draw.rect(screen, color, boton, border_radius=10)
            pygame.draw.rect(screen, borde, boton, 3, border_radius=10)

            texto_render = font.render(texto, True, color_texto)
            screen.blit(texto_render, texto_render.get_rect(center=boton.center))
        #----

        pygame.display.flip()
        clock.tick(60)