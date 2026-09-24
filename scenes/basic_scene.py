if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

import customization


def gameloop(screen):

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

    # Iniciamos el loop principal de la escena inicial
    while running:

        for event in pygame.event.get():

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "quit"

            elif event.type == QUIT:
                return "quit"

            #---- FEATURE MENU INICIO - CLICK BOTONES ----
            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    if boton_jugar.collidepoint(event.pos):
                        return "play"

                    if boton_tienda.collidepoint(event.pos):
                        return "shop"

                    if boton_salir.collidepoint(event.pos):
                        return "quit"
            #----

        # Limpiar pantalla (fondo negro)

        #---- FEATURE MENU INICIO - FONDO PERSONALIZADO ----
        background = pygame.image.load(customization.obtener_asset("Inicio_Back")).convert()
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
        screen.blit(background, (0, 0))

        sombra = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 145))
        screen.blit(sombra, (0, 0))
        #----

        #---- FEATURE MENU INICIO - DIBUJAR BOTONES ----
        mouse = pygame.mouse.get_pos()

        for boton, texto in [
            (boton_jugar, "JUGAR"),
            (boton_tienda, "TIENDA"),
            (boton_salir, "SALIR"),
        ]:

            if boton.collidepoint(mouse):
                color = (255, 205, 60)
            else:
                color = (40, 45, 55)

            pygame.draw.rect(screen, color, boton, border_radius=10)
            pygame.draw.rect(screen, (255, 215, 80), boton, 3, border_radius=10)

            texto_render = font.render(texto, True, (255, 255, 255))
            screen.blit(texto_render, texto_render.get_rect(center=boton.center))
        #----

        # Actualizar pantalla
        pygame.display.flip()

        # Limitar FPS
        clock.tick(60)