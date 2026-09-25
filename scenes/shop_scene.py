if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame

from pygame.locals import (
    K_a,
    K_d,
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_RETURN,
    K_RIGHT,
    K_s,
    K_UP,
    K_w,
    KEYDOWN,
    QUIT,
)

import customization
import habilidades


def gameloop(screen, coins):

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(True)

    font_titulo = pygame.font.Font(None, 72)
    font_categoria = pygame.font.Font(None, 34)
    font_info = pygame.font.Font(None, 31)
    font_chica = pygame.font.Font(None, 24)


    # custom + MEJORAS
    categorias = [
        "background",
        "bug",
        "bullet",
        "vida",
        "municion",
        "recarga",
        "penetracion",
        "dano",
    ]


    nombres = [
        "FONDO",
        "ENEMIGO",
        "PROYECTIL",
        "VIDA",
        "MUNICION",
        "RECARGA",
        "PENETRACION",
        "DANO",
    ]


    categoria_actual = 0


    while True:

        for event in pygame.event.get():

            if event.type == QUIT:
                return ("quit", coins)


            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    return ("back", coins)


                # moverse por tienda
                if event.key in (K_w, K_UP):
                    categoria_actual = (categoria_actual - 1) % len(categorias)


                if event.key in (K_s, K_DOWN):
                    categoria_actual = (categoria_actual + 1) % len(categorias)


                categoria = categorias[categoria_actual]


                # los 3 primeros son cosmeticos
                if categoria in ["background", "bug", "bullet"]:

                    if event.key in (K_a, K_LEFT):
                        customization.cambiar_asset(categoria, -1)

                    if event.key in (K_d, K_RIGHT):
                        customization.cambiar_asset(categoria, 1)


                # comprar mejroas
                if event.key == K_RETURN:

                    if categoria in [
                        "vida",
                        "municion",
                        "recarga",
                        "penetracion",
                        "dano",
                    ]:

                        coins, compro = habilidades.comprar(
                            categoria,
                            coins
                        )


        background = pygame.image.load(
            customization.obtener_asset("background")
        ).convert()

        background = pygame.transform.scale(
            background,
            (screen.get_width(), screen.get_height())
        )

        screen.blit(background, (0, 0))


        sombra = pygame.Surface(
            (screen.get_width(), screen.get_height()),
            pygame.SRCALPHA
        )

        sombra.fill((0, 0, 0, 185))

        screen.blit(sombra, (0, 0))


        titulo = font_titulo.render(
            "TIENDA",
            True,
            (255, 215, 80)
        )

        screen.blit(
            titulo,
            titulo.get_rect(center=(screen.get_width() // 2, 60))
        )


        # coins arriba
        texto_coins = font_categoria.render(
            f"COINS: {coins}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            texto_coins,
            texto_coins.get_rect(
                topright=(screen.get_width() - 35, 30)
            )
        )


        # titulos de las dos partes
        texto_custom = font_chica.render(
            "CUSTOM",
            True,
            (170, 170, 170)
        )

        screen.blit(texto_custom, (80, 105))


        texto_mejoras = font_chica.render(
            "MEJORAS PERMANENTES",
            True,
            (170, 170, 170)
        )

        screen.blit(texto_mejoras, (80, 310))


        # lista
        posiciones_y = [
            140,
            195,
            250,
            345,
            400,
            455,
            510,
            565,
        ]


        for i in range(len(categorias)):

            y = posiciones_y[i]

            if i == categoria_actual:

                color = (255, 215, 80)
                texto = "> " + nombres[i]

            else:

                color = (220, 220, 220)
                texto = nombres[i]


            categoria_texto = font_categoria.render(
                texto,
                True,
                color
            )

            screen.blit(
                categoria_texto,
                (80, y)
            )


        categoria = categorias[categoria_actual]


        # =================================================
        # cosas customizables
        # =================================================
        if categoria in ["background", "bug", "bullet"]:

            archivo = customization.obtener_asset(
                categoria
            )

            preview = pygame.image.load(
                archivo
            ).convert_alpha()


            if categoria == "background":

                preview = pygame.transform.scale(
                    preview,
                    (360, 270)
                )


            elif categoria == "bug":

                preview = pygame.transform.scale(
                    preview,
                    (160, 160)
                )


            elif categoria == "bullet":

                preview = pygame.transform.scale(
                    preview,
                    (220, 80)
                )


            preview_rect = preview.get_rect(
                center=(750, 330)
            )

            screen.blit(
                preview,
                preview_rect
            )


            numero = customization.seleccion[categoria] + 1
            total = len(customization.ASSETS[categoria])


            variante = font_info.render(
                f"{numero} / {total}",
                True,
                (255, 255, 255)
            )


            screen.blit(
                variante,
                variante.get_rect(center=(750, 530))
            )


            ayuda = font_chica.render(
                "A / D para cambiar",
                True,
                (210, 210, 210)
            )

            screen.blit(
                ayuda,
                ayuda.get_rect(center=(750, 580))
            )


        # =================================================
        # habildiades
        # =================================================
        else:

            nivel = habilidades.niveles[categoria]
            nivel_maximo = habilidades.maximos[categoria]


            nombre_grande = font_categoria.render(
                nombres[categoria_actual],
                True,
                (255, 215, 80)
            )

            screen.blit(
                nombre_grande,
                nombre_grande.get_rect(center=(750, 220))
            )


            texto_nivel = font_info.render(
                f"NIVEL {nivel} / {nivel_maximo}",
                True,
                (255, 255, 255)
            )

            screen.blit(
                texto_nivel,
                texto_nivel.get_rect(center=(750, 285))
            )


            actual = habilidades.texto_valor(
                categoria
            )

            texto_actual = font_info.render(
                f"Actual: {actual}",
                True,
                (230, 230, 230)
            )

            screen.blit(
                texto_actual,
                texto_actual.get_rect(center=(750, 340))
            )


            if nivel >= nivel_maximo:

                texto_max = font_categoria.render(
                    "NIVEL MAXIMO",
                    True,
                    (255, 215, 80)
                )

                screen.blit(
                    texto_max,
                    texto_max.get_rect(center=(750, 430))
                )


            else:

                siguiente = habilidades.texto_valor(
                    categoria,
                    nivel + 1
                )

                texto_siguiente = font_info.render(
                    f"Siguiente: {siguiente}",
                    True,
                    (150, 220, 255)
                )

                screen.blit(
                    texto_siguiente,
                    texto_siguiente.get_rect(center=(750, 390))
                )


                precio = habilidades.costo(
                    categoria
                )


                if coins >= precio:
                    color_precio = (100, 255, 100)

                else:
                    color_precio = (255, 100, 100)


                texto_precio = font_categoria.render(
                    f"{precio} COINS",
                    True,
                    color_precio
                )

                screen.blit(
                    texto_precio,
                    texto_precio.get_rect(center=(750, 460))
                )


                comprar_texto = font_chica.render(
                    "ENTER para comprar",
                    True,
                    (220, 220, 220)
                )

                screen.blit(
                    comprar_texto,
                    comprar_texto.get_rect(center=(750, 520))
                )


        controles = font_chica.render(
            "W/S: seleccionar   A/D: cambiar custom   ENTER: comprar   ESC: volver",
            True,
            (220, 220, 220)
        )

        screen.blit(
            controles,
            controles.get_rect(
                center=(screen.get_width() // 2, 725)
            )
        )


        pygame.display.flip()

        clock.tick(60)