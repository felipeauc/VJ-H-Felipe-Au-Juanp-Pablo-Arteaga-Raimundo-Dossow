if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_a, K_d, K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_s, K_UP, K_w, K_RETURN, KEYDOWN, QUIT
import customization

def gameloop(screen, coins, nivel_vida, nivel_balas):

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(True)

    font_titulo = pygame.font.Font(None, 72)
    font_categoria = pygame.font.Font(None, 40)
    font_chica = pygame.font.Font(None, 27)

    # Agregamos las mejoras directamente a las listas
    categorias = ["background", "bug", "bullet", "vida", "balas"]
    nombres = ["FONDO", "ENEMIGO", "PROYECTIL", "MEJORA DE VIDA", "MEJORA DE MUNICIÓN"]

    categoria_actual = 0

    while True:

        costo_vida = round(200 * (1.5 ** nivel_vida))
        costo_balas = round(100 * (1.5 ** nivel_balas))

        for event in pygame.event.get():

            if event.type == QUIT:
                return ("quit", coins, nivel_vida, nivel_balas)

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    return ("back", coins, nivel_vida, nivel_balas)

                if event.key in (K_w, K_UP):
                    categoria_actual = (categoria_actual - 1) % len(categorias)

                if event.key in (K_s, K_DOWN):
                    categoria_actual = (categoria_actual + 1) % len(categorias)

                categoria = categorias[categoria_actual]

                # Controles para cosméticos
                if categoria in ["background", "bug", "bullet"]:
                    if event.key in (K_a, K_LEFT):
                        customization.cambiar_asset(categoria, -1)

                    if event.key in (K_d, K_RIGHT):
                        customization.cambiar_asset(categoria, 1)
                
                # Controles para comprar mejoras
                if event.key == K_RETURN:
                    if categoria == "vida" and coins >= costo_vida and nivel_vida < 10:
                        coins -= costo_vida
                        nivel_vida += 1

                    elif categoria == "balas" and coins >= costo_balas and nivel_balas < 10:
                        coins -= costo_balas
                        nivel_balas += 1


        background = pygame.image.load(customization.obtener_asset("background")).convert()
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))

        screen.blit(background, (0, 0))

        sombra = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 170))
        screen.blit(sombra, (0, 0))

        titulo = font_titulo.render("TIENDA", True, (255, 215, 80))
        screen.blit(titulo, titulo.get_rect(center=(screen.get_width() // 2, 80)))
        
        # Mostramos las monedas en la esquina superior derecha
        texto_coins = font_categoria.render(f"COINS: {coins}", True, (255, 255, 255))
        screen.blit(texto_coins, texto_coins.get_rect(topright=(screen.get_width() - 40, 40)))

        #---- FEATURE TIENDA - LISTA DE CATEGORIAS ----
        for i in range(len(categorias)):
            
            # Ajustamos la altura inicial a 180 para que entren los 5 items
            y = 180 + i * 90

            if i == categoria_actual:
                color = (255, 215, 80)
                texto = "> " + nombres[i]
            else:
                color = (220, 220, 220)
                texto = nombres[i]

            categoria_texto = font_categoria.render(texto, True, color)
            screen.blit(categoria_texto, (110, y))
        #----

        #---- FEATURE TIENDA - PREVIEW DEL ASSET Y MEJORAS ----
        categoria = categorias[categoria_actual]

        if categoria in ["background", "bug", "bullet"]:
            
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

        elif categoria == "vida":
            
            icono = pygame.image.load("assets/heart.png").convert_alpha()
            icono = pygame.transform.scale(icono, (100, 100))
            screen.blit(icono, icono.get_rect(center=(720, 320)))
            
            if nivel_vida >= 10:
                texto_maximo = font_categoria.render("NIVEL MÁXIMO", True, (255, 215, 80))
                screen.blit(texto_maximo, texto_maximo.get_rect(center=(720, 445)))
            else:
                texto_nivel = font_categoria.render(f"Nivel Actual: {nivel_vida}", True, (255, 255, 255))
                color_costo = (100, 255, 100) if coins >= costo_vida else (255, 100, 100)
                texto_costo = font_categoria.render(f"Mejorar: {costo_vida} Coins", True, color_costo)
                
                screen.blit(texto_nivel, texto_nivel.get_rect(center=(720, 420)))
                screen.blit(texto_costo, texto_costo.get_rect(center=(720, 470)))

        elif categoria == "balas":
            
            icono = pygame.image.load("assets/bullet.png").convert_alpha()
            icono = pygame.transform.scale(icono, (180, 60))
            screen.blit(icono, icono.get_rect(center=(720, 320)))
            
            if nivel_balas >= 10:
                texto_maximo = font_categoria.render("NIVEL MÁXIMO", True, (255, 215, 80))
                screen.blit(texto_maximo, texto_maximo.get_rect(center=(720, 445)))
            else:
                texto_nivel = font_categoria.render(f"Nivel Actual: {nivel_balas}", True, (255, 255, 255))
                color_costo = (100, 255, 100) if coins >= costo_balas else (255, 100, 100)
                texto_costo = font_categoria.render(f"Mejorar: {costo_balas} Coins", True, color_costo)
                
                screen.blit(texto_nivel, texto_nivel.get_rect(center=(720, 420)))
                screen.blit(texto_costo, texto_costo.get_rect(center=(720, 470)))
        #----

        controles = font_chica.render("W/S: seleccionar   A/D: cambiar   ENTER: comprar   ESC: volver", True, (220, 220, 220))
        screen.blit(controles, controles.get_rect(center=(screen.get_width() // 2, 700)))

        pygame.display.flip()
        clock.tick(60)