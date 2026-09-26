if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame

from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT
)

import customization
import logros


def gameloop(screen, logros_desbloqueados=None):

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(True)

    font_titulo = pygame.font.Font(
        None,
        62
    )

    font_nombre = pygame.font.Font(
        None,
        31
    )

    font_desc = pygame.font.Font(
        None,
        21
    )

    font_chica = pygame.font.Font(
        None,
        27
    )


    nombres = [
        "Primeros Pasos",
        "Piloto Veterano",
        "Leyenda Galáctica",
        "Primera Paga",
        "Tanque Espacial",
        "Arsenal Infinito",
        "Intocable",
        "Fortaleza Espacial",
        "Sobrecarga",
        "¿Eres nuevo?",
        "Pacifista",
        "Cliente VIP",
    ]


    descripciones = [
        "Juega tu primera partida.",
        "Supera los 500 puntos.",
        "Alcanza los 1000 puntos.",
        "Ten al menos 100 coins.",
        "Mejora la Vida al nivel máximo.",
        "Mejora la Munición al nivel máximo.",
        "Consigue 250 pts sin recibir daño.",
        "Recoge 3 escudos en una partida.",
        "Usa Rapid Fire durante una partida.",
        "Muere con menos de 10 puntos.",
        "Llega a 100 pts sin disparar.",
        "Gasta 500 coins en una visita.",
    ]


    while True:

        for event in pygame.event.get():

            if event.type == QUIT:
                return "quit"

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    return "back"


        # siempre leer el estado real
        estado = logros.obtener_estado()


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
            (0, 0, 0, 205)
        )

        screen.blit(
            sombra,
            (0, 0)
        )


        titulo = font_titulo.render(
            "LOGROS Y TROFEOS",
            True,
            (255, 215, 80)
        )

        screen.blit(
            titulo,
            titulo.get_rect(
                center=(
                    screen.get_width() // 2,
                    45
                )
            )
        )


        for i in range(12):

            if i < 6:

                x = 48

            else:

                x = 507

            y = (
                90
                + (i % 6) * 91
            )

            desbloqueado = estado[i]


            if desbloqueado:

                color_titulo = (
                    255,
                    215,
                    80
                )

                color_desc = (
                    220,
                    220,
                    220
                )

                texto_nombre = nombres[i]

                texto_desc = descripciones[i]

            else:

                color_titulo = (
                    105,
                    105,
                    105
                )

                color_desc = (
                    90,
                    90,
                    90
                )

                if i >= 9:

                    texto_nombre = (
                        "??? (Logro Oculto)"
                    )

                    texto_desc = (
                        "Sigue jugando para descubrirlo."
                    )

                else:

                    texto_nombre = (
                        nombres[i]
                        + " (Bloqueado)"
                    )

                    texto_desc = descripciones[i]


            sup_nombre = font_nombre.render(
                texto_nombre,
                True,
                color_titulo
            )

            sup_desc = font_desc.render(
                texto_desc,
                True,
                color_desc
            )

            screen.blit(
                sup_nombre,
                (x, y)
            )

            screen.blit(
                sup_desc,
                (x, y + 30)
            )


        controles = font_chica.render(
            "ESC: Volver al menú",
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