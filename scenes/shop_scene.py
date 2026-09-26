if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame

from pygame.locals import (
    K_a,
    K_d,
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_RIGHT,
    K_s,
    K_UP,
    K_w,
    K_RETURN,
    KEYDOWN,
    QUIT
)

import customization
import habilidades
import logros


def cargar_icono(categoria):

    if categoria == "background":

        imagen = pygame.image.load(
            customization.obtener_asset(
                "background"
            )
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (55, 42)
        )

    elif categoria == "bug":

        imagen = pygame.image.load(
            customization.obtener_asset(
                "bug"
            )
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (48, 48)
        )

    elif categoria == "bullet":

        imagen = pygame.image.load(
            customization.obtener_asset(
                "bullet"
            )
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (55, 28)
        )

    elif categoria == "vida":

        imagen = pygame.image.load(
            "assets/heart.png"
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (46, 46)
        )

    elif categoria == "municion":

        imagen = pygame.image.load(
            "assets/bullet.png"
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (55, 28)
        )

    elif categoria == "recarga":

        imagen = pygame.image.load(
            "assets/jorge_reload.png"
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (48, 48)
        )

    elif categoria == "penetracion":

        imagen = pygame.image.load(
            "assets/bullet_rapid_fire.png"
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (55, 28)
        )

    elif categoria == "dano":

        imagen = pygame.image.load(
            "assets/proyectil_B.png"
        ).convert_alpha()

        return pygame.transform.scale(
            imagen,
            (46, 46)
        )


def gameloop(screen, coins):

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(True)

    # nueva visita = gasto parte desde 0
    logros.iniciar_visita_tienda()

    # por si ya estaba al maximo antes de actualizar el sistema
    logros.revisar_habilidades()


    font_titulo = pygame.font.Font(
        None,
        72
    )

    font_categoria = pygame.font.Font(
        None,
        31
    )

    font_info = pygame.font.Font(
        None,
        30
    )

    font_chica = pygame.font.Font(
        None,
        24
    )


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


    posiciones_y = [
        145,
        200,
        255,
        350,
        405,
        460,
        515,
        570,
    ]


    categoria_actual = 0


    while True:

        for event in pygame.event.get():

            if event.type == QUIT:

                return (
                    "quit",
                    coins
                )

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:

                    return (
                        "back",
                        coins
                    )

                if event.key in (
                    K_w,
                    K_UP
                ):

                    categoria_actual = (
                        categoria_actual - 1
                    ) % len(categorias)

                if event.key in (
                    K_s,
                    K_DOWN
                ):

                    categoria_actual = (
                        categoria_actual + 1
                    ) % len(categorias)


                categoria = categorias[
                    categoria_actual
                ]


                # cambiar cosmetic
                if categoria in [
                    "background",
                    "bug",
                    "bullet"
                ]:

                    if event.key in (
                        K_a,
                        K_LEFT
                    ):

                        customization.cambiar_asset(
                            categoria,
                            -1
                        )

                    if event.key in (
                        K_d,
                        K_RIGHT
                    ):

                        customization.cambiar_asset(
                            categoria,
                            1
                        )


                # comprar mejora
                if event.key == K_RETURN:

                    if categoria in [
                        "vida",
                        "municion",
                        "recarga",
                        "penetracion",
                        "dano"
                    ]:

                        coins_antes = coins

                        coins, compro = habilidades.comprar(
                            categoria,
                            coins
                        )

                        if compro:

                            gastado = (
                                coins_antes
                                - coins
                            )

                            # CLIENTE VIP
                            logros.registrar_gasto(
                                gastado
                            )

                            # vida / municion max
                            logros.revisar_habilidades()


        # ======================================
        # DIBUJO
        # ======================================

        background = pygame.image.load(
            customization.obtener_asset(
                "background"
            )
        ).convert()

        background = pygame.transform.scale(
            background,
            (
                screen.get_width(),
                screen.get_height()
            )
        )

        screen.blit(
            background,
            (0, 0)
        )


        sombra = pygame.Surface(
            (
                screen.get_width(),
                screen.get_height()
            ),
            pygame.SRCALPHA
        )

        sombra.fill(
            (0, 0, 0, 185)
        )

        screen.blit(
            sombra,
            (0, 0)
        )


        titulo = font_titulo.render(
            "TIENDA",
            True,
            (255, 215, 80)
        )

        screen.blit(
            titulo,
            titulo.get_rect(
                center=(
                    screen.get_width() // 2,
                    55
                )
            )
        )


        texto_coins = font_categoria.render(
            f"COINS: {coins}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            texto_coins,
            texto_coins.get_rect(
                topright=(
                    screen.get_width() - 35,
                    30
                )
            )
        )


        texto_custom = font_chica.render(
            "CUSTOMIZABLES",
            True,
            (170, 170, 170)
        )

        screen.blit(
            texto_custom,
            (60, 105)
        )


        texto_stats = font_chica.render(
            "MEJORAS",
            True,
            (170, 170, 170)
        )

        screen.blit(
            texto_stats,
            (60, 315)
        )


        # lista izquierda
        for i in range(
            len(categorias)
        ):

            categoria = categorias[i]

            y = posiciones_y[i]

            icono = cargar_icono(
                categoria
            )

            caja = pygame.Rect(
                55,
                y - 8,
                60,
                50
            )


            if i == categoria_actual:

                pygame.draw.rect(
                    screen,
                    (255, 215, 80),
                    caja,
                    2,
                    border_radius=8
                )

                color = (
                    255,
                    215,
                    80
                )

                texto = (
                    "> "
                    + nombres[i]
                )

            else:

                pygame.draw.rect(
                    screen,
                    (90, 90, 90),
                    caja,
                    1,
                    border_radius=8
                )

                color = (
                    220,
                    220,
                    220
                )

                texto = nombres[i]


            icono_rect = icono.get_rect(
                center=caja.center
            )

            screen.blit(
                icono,
                icono_rect
            )


            categoria_texto = (
                font_categoria.render(
                    texto,
                    True,
                    color
                )
            )

            screen.blit(
                categoria_texto,
                (130, y)
            )


        categoria = categorias[
            categoria_actual
        ]


        panel = pygame.Rect(
            555,
            135,
            390,
            500
        )

        pygame.draw.rect(
            screen,
            (20, 20, 25),
            panel,
            border_radius=18
        )

        pygame.draw.rect(
            screen,
            (100, 100, 110),
            panel,
            2,
            border_radius=18
        )


        # cosmetic
        if categoria in [
            "background",
            "bug",
            "bullet"
        ]:

            archivo = customization.obtener_asset(
                categoria
            )

            preview = pygame.image.load(
                archivo
            ).convert_alpha()


            if categoria == "background":

                preview = pygame.transform.scale(
                    preview,
                    (330, 245)
                )

            elif categoria == "bug":

                preview = pygame.transform.scale(
                    preview,
                    (190, 190)
                )

            else:

                preview = pygame.transform.scale(
                    preview,
                    (250, 100)
                )


            preview_rect = preview.get_rect(
                center=(
                    750,
                    330
                )
            )

            screen.blit(
                preview,
                preview_rect
            )


            numero = (
                customization.seleccion[
                    categoria
                ]
                + 1
            )

            cantidad = len(
                customization.ASSETS[
                    categoria
                ]
            )


            variante = font_categoria.render(
                f"{numero} / {cantidad}",
                True,
                (255, 255, 255)
            )

            screen.blit(
                variante,
                variante.get_rect(
                    center=(
                        750,
                        510
                    )
                )
            )


            ayuda = font_chica.render(
                "A / D para cambiar",
                True,
                (210, 210, 210)
            )

            screen.blit(
                ayuda,
                ayuda.get_rect(
                    center=(
                        750,
                        560
                    )
                )
            )


        # stats
        else:

            icono_grande = cargar_icono(
                categoria
            )

            if categoria in [
                "vida",
                "recarga",
                "dano"
            ]:

                icono_grande = pygame.transform.scale(
                    icono_grande,
                    (120, 120)
                )

            else:

                icono_grande = pygame.transform.scale(
                    icono_grande,
                    (180, 90)
                )


            screen.blit(
                icono_grande,
                icono_grande.get_rect(
                    center=(
                        750,
                        250
                    )
                )
            )


            nombre = font_categoria.render(
                nombres[
                    categoria_actual
                ],
                True,
                (255, 215, 80)
            )

            screen.blit(
                nombre,
                nombre.get_rect(
                    center=(
                        750,
                        340
                    )
                )
            )


            nivel = habilidades.niveles[
                categoria
            ]

            nivel_max = habilidades.maximos[
                categoria
            ]


            texto_nivel = font_info.render(
                f"NIVEL {nivel} / {nivel_max}",
                True,
                (255, 255, 255)
            )

            screen.blit(
                texto_nivel,
                texto_nivel.get_rect(
                    center=(
                        750,
                        385
                    )
                )
            )


            valor_actual = habilidades.texto_valor(
                categoria
            )


            actual = font_info.render(
                f"Actual: {valor_actual}",
                True,
                (220, 220, 220)
            )

            screen.blit(
                actual,
                actual.get_rect(
                    center=(
                        750,
                        425
                    )
                )
            )


            if nivel >= nivel_max:

                maximo = font_categoria.render(
                    "NIVEL MAXIMO",
                    True,
                    (255, 215, 80)
                )

                screen.blit(
                    maximo,
                    maximo.get_rect(
                        center=(
                            750,
                            510
                        )
                    )
                )

            else:

                siguiente = habilidades.texto_valor(
                    categoria,
                    nivel + 1
                )

                texto_siguiente = font_info.render(
                    f"Siguiente: {siguiente}",
                    True,
                    (130, 210, 255)
                )

                screen.blit(
                    texto_siguiente,
                    texto_siguiente.get_rect(
                        center=(
                            750,
                            465
                        )
                    )
                )


                precio = habilidades.costo(
                    categoria
                )


                if coins >= precio:

                    color_precio = (
                        100,
                        255,
                        100
                    )

                else:

                    color_precio = (
                        255,
                        100,
                        100
                    )


                texto_precio = font_categoria.render(
                    f"{precio} COINS",
                    True,
                    color_precio
                )

                screen.blit(
                    texto_precio,
                    texto_precio.get_rect(
                        center=(
                            750,
                            520
                        )
                    )
                )


                comprar = font_chica.render(
                    "ENTER para comprar",
                    True,
                    (220, 220, 220)
                )

                screen.blit(
                    comprar,
                    comprar.get_rect(
                        center=(
                            750,
                            565
                        )
                    )
                )


        controles = font_chica.render(
            "W/S seleccionar    A/D cambiar    ENTER comprar    ESC volver",
            True,
            (220, 220, 220)
        )

        screen.blit(
            controles,
            controles.get_rect(
                center=(
                    screen.get_width() // 2,
                    720
                )
            )
        )


        pygame.display.flip()

        clock.tick(60)