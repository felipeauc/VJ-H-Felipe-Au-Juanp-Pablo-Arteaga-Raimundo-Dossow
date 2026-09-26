if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_a, K_d, K_DOWN, K_ESCAPE, K_LEFT, K_RIGHT, K_s, K_UP, K_w, K_RETURN, KEYDOWN, QUIT

import customization
import habilidades

try:
    import logros
except ImportError:
    logros = None


_cache_iconos = {}


def imagen_cache(archivo, tamano):
    clave = (archivo, tamano)

    if clave not in _cache_iconos:
        imagen = pygame.image.load(archivo).convert_alpha()
        _cache_iconos[clave] = pygame.transform.scale(imagen, tamano)

    return _cache_iconos[clave]


def cargar_icono(categoria):
    if categoria == "background":
        return imagen_cache(customization.obtener_asset("background"), (55, 42))

    if categoria == "bug":
        return imagen_cache(customization.obtener_asset("bug"), (48, 48))

    if categoria == "bullet":
        return imagen_cache(customization.obtener_asset("bullet"), (55, 28))

    if categoria == "vida":
        return imagen_cache("assets/heart.png", (46, 46))

    if categoria == "municion":
        return imagen_cache("assets/bullet.png", (55, 28))

    if categoria == "recarga":
        return imagen_cache("assets/jorge_reload.png", (48, 48))

    if categoria == "penetracion":
        return imagen_cache("assets/bullet_rapid_fire.png", (55, 28))

    if categoria == "dano":
        return imagen_cache("assets/proyectil_B.png", (46, 46))

    if categoria == "tamano":
        return imagen_cache("assets/jorge.png", (46, 46))


def gameloop(screen, coins):
    clock = pygame.time.Clock()

    pygame.mouse.set_visible(True)

    if logros is not None:
        logros.iniciar_visita_tienda()
        logros.revisar_habilidades()

    font_titulo = pygame.font.Font(None, 72)
    font_categoria = pygame.font.Font(None, 29)
    font_info = pygame.font.Font(None, 29)
    font_chica = pygame.font.Font(None, 23)

    categorias = ["background", "bug", "bullet", "vida", "municion", "recarga", "penetracion", "dano", "tamano"]
    nombres = ["FONDO", "ENEMIGO", "PROYECTIL", "VIDA", "MUNICION", "RECARGA", "PENETRACION", "DANO", "TAMAÑO"]

    posiciones_y = [135, 185, 235, 325, 375, 425, 475, 525, 575]

    categoria_actual = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return ("quit", coins)

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return ("back", coins)

                if event.key in (K_w, K_UP):
                    categoria_actual = (categoria_actual - 1) % len(categorias)

                if event.key in (K_s, K_DOWN):
                    categoria_actual = (categoria_actual + 1) % len(categorias)

                categoria = categorias[categoria_actual]

                if categoria in ["background", "bug", "bullet"]:
                    if event.key in (K_a, K_LEFT):
                        customization.cambiar_asset(categoria, -1)

                    if event.key in (K_d, K_RIGHT):
                        customization.cambiar_asset(categoria, 1)

                if event.key == K_RETURN and categoria in ["vida", "municion", "recarga", "penetracion", "dano", "tamano"]:
                    coins_antes = coins
                    coins, compro = habilidades.comprar(categoria, coins)

                    if compro and logros is not None:
                        logros.registrar_gasto(coins_antes - coins)
                        logros.revisar_habilidades()

        background = pygame.image.load(customization.obtener_asset("background")).convert()
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))

        screen.blit(background, (0, 0))

        sombra = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 185))

        screen.blit(sombra, (0, 0))

        titulo = font_titulo.render("TIENDA", True, (255, 215, 80))
        screen.blit(titulo, titulo.get_rect(center=(screen.get_width() // 2, 55)))

        texto_coins = font_categoria.render(f"COINS: {coins}", True, (255, 255, 255))
        screen.blit(texto_coins, texto_coins.get_rect(topright=(screen.get_width() - 35, 30)))

        screen.blit(font_chica.render("CUSTOMIZABLES", True, (170, 170, 170)), (55, 95))
        screen.blit(font_chica.render("MEJORAS", True, (170, 170, 170)), (55, 285))

        for i, categoria in enumerate(categorias):
            y = posiciones_y[i]
            icono = cargar_icono(categoria)

            caja = pygame.Rect(50, y - 8, 60, 45)

            if i == categoria_actual:
                pygame.draw.rect(screen, (255, 215, 80), caja, 2, border_radius=8)

                color = (255, 215, 80)
                texto = "> " + nombres[i]

            else:
                pygame.draw.rect(screen, (90, 90, 90), caja, 1, border_radius=8)

                color = (220, 220, 220)
                texto = nombres[i]

            screen.blit(icono, icono.get_rect(center=caja.center))
            screen.blit(font_categoria.render(texto, True, color), (125, y))

        categoria = categorias[categoria_actual]

        panel = pygame.Rect(555, 125, 390, 510)

        pygame.draw.rect(screen, (20, 20, 25), panel, border_radius=18)
        pygame.draw.rect(screen, (100, 100, 110), panel, 2, border_radius=18)

        if categoria in ["background", "bug", "bullet"]:
            archivo = customization.obtener_asset(categoria)
            preview = pygame.image.load(archivo).convert_alpha()

            if categoria == "background":
                preview = pygame.transform.scale(preview, (330, 245))

            elif categoria == "bug":
                preview = pygame.transform.scale(preview, (190, 190))

            else:
                preview = pygame.transform.scale(preview, (250, 100))

            screen.blit(preview, preview.get_rect(center=(750, 325)))

            numero = customization.seleccion[categoria] + 1
            cantidad = len(customization.ASSETS[categoria])

            variante = font_categoria.render(f"{numero} / {cantidad}", True, (255, 255, 255))
            screen.blit(variante, variante.get_rect(center=(750, 510)))

            ayuda = font_chica.render("A / D para cambiar", True, (210, 210, 210))
            screen.blit(ayuda, ayuda.get_rect(center=(750, 560)))

        else:
            icono_grande = cargar_icono(categoria)

            if categoria in ["vida", "recarga", "dano", "tamano"]:
                icono_grande = pygame.transform.scale(icono_grande, (120, 120))
            else:
                icono_grande = pygame.transform.scale(icono_grande, (180, 90))

            screen.blit(icono_grande, icono_grande.get_rect(center=(750, 235)))

            nombre = font_categoria.render(nombres[categoria_actual], True, (255, 215, 80))
            screen.blit(nombre, nombre.get_rect(center=(750, 330)))

            nivel = habilidades.niveles[categoria]
            nivel_max = habilidades.maximos[categoria]

            texto_nivel = font_info.render(f"NIVEL {nivel} / {nivel_max}", True, (255, 255, 255))
            screen.blit(texto_nivel, texto_nivel.get_rect(center=(750, 375)))

            actual = font_info.render(f"Actual: {habilidades.texto_valor(categoria)}", True, (220, 220, 220))
            screen.blit(actual, actual.get_rect(center=(750, 415)))

            if nivel >= nivel_max:
                maximo = font_categoria.render("NIVEL MAXIMO", True, (255, 215, 80))
                screen.blit(maximo, maximo.get_rect(center=(750, 505)))

            else:
                siguiente = font_info.render(f"Siguiente: {habilidades.texto_valor(categoria, nivel + 1)}", True, (130, 210, 255))
                screen.blit(siguiente, siguiente.get_rect(center=(750, 455)))

                precio = habilidades.costo(categoria)
                color_precio = (100, 255, 100) if coins >= precio else (255, 100, 100)

                texto_precio = font_categoria.render(f"{precio} COINS", True, color_precio)
                screen.blit(texto_precio, texto_precio.get_rect(center=(750, 510)))

                comprar = font_chica.render("ENTER para comprar", True, (220, 220, 220))
                screen.blit(comprar, comprar.get_rect(center=(750, 555)))

        controles = font_chica.render("W/S seleccionar    A/D cambiar    ENTER comprar    ESC volver", True, (220, 220, 220))
        screen.blit(controles, controles.get_rect(center=(screen.get_width() // 2, 720)))

        pygame.display.flip()
        clock.tick(60)