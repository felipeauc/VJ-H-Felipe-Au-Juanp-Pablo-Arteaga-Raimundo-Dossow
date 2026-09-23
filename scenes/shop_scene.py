if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_a, K_d, K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_s, K_UP, K_w, KEYDOWN, QUIT

import customization


def gameloop(screen):

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(True)

    font_titulo = pygame.font.Font(None, 72)
    font_categoria = pygame.font.Font(None, 40)
    font_chica = pygame.font.Font(None, 27)

    categorias = ["background", "bug", "bullet"]
    nombres = ["FONDO", "ENEMIGO", "PROYECTIL"]

    categoria_actual = 0

    while True:

        for event in pygame.event.get():

            if event.type == QUIT:
                return "quit"

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    return "back"

                if event.key in (K_w, K_UP):
                    categoria_actual = (categoria_actual - 1) % len(categorias)

                if event.key in (K_s, K_DOWN):
                    categoria_actual = (categoria_actual + 1) % len(categorias)

                if event.key in (K_a, K_LEFT):
                    customization.cambiar_asset(categorias[categoria_actual], -1)

                if event.key in (K_d, K_RIGHT):
                    customization.cambiar_asset(categorias[categoria_actual], 1)

        background = pygame.image.load(customization.obtener_asset("background")).convert()
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))

        screen.blit(background, (0, 0))

        sombra = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 170))
        screen.blit(sombra, (0, 0))

        titulo = font_titulo.render("TIENDA", True, (255, 215, 80))
        screen.blit(titulo, titulo.get_rect(center=(screen.get_width() // 2, 80)))

        #---- FEATURE TIENDA - LISTA DE CATEGORIAS ----
        for i in range(len(categorias)):

            y = 220 + i * 90

            if i == categoria_actual:
                color = (255, 215, 80)
                texto = "> " + nombres[i]
            else:
                color = (220, 220, 220)
                texto = nombres[i]

            categoria_texto = font_categoria.render(texto, True, color)
            screen.blit(categoria_texto, (110, y))
        #----

        #---- FEATURE TIENDA - PREVIEW DEL ASSET ----
        categoria = categorias[categoria_actual]
        archivo = customization.obtener_asset(categoria)

        preview = pygame.image.load(archivo).convert_alpha()

        if categoria == "background":
            preview = pygame.transform.scale(preview, (360, 270))

        elif categoria == "bug":
            preview = pygame.transform.scale(preview, (150, 150))

        elif categoria == "bullet":
            preview = pygame.transform.scale(preview, (220, 80))

        preview_rect = preview.get_rect(center=(720, 350))
        screen.blit(preview, preview_rect)

        numero = customization.seleccion[categoria] + 1

        variante = font_categoria.render(f"{numero} / 5", True, (255, 255, 255))
        screen.blit(variante, variante.get_rect(center=(720, 520)))
        #----

        controles = font_chica.render("W/S: categoria     A/D: cambiar     ESC: volver", True, (220, 220, 220))
        screen.blit(controles, controles.get_rect(center=(screen.get_width() // 2, 700)))

        pygame.display.flip()
        clock.tick(60)