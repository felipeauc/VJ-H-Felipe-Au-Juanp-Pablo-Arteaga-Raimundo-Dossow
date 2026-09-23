if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, K_r, KEYDOWN, QUIT


def gameloop(screen):

    clock = pygame.time.Clock()

    pygame.mouse.set_visible(True)

    font_grande = pygame.font.Font(None, 100)
    font_chica = pygame.font.Font(None, 45)

    game_over = font_grande.render(
        "GAME OVER",
        True,
        (255, 0, 0),
    )

    volver = font_chica.render(
        "R - VOLVER A JUGAR",
        True,
        (255, 255, 255),
    )

    salir = font_chica.render(
        "ESC - SALIR",
        True,
        (255, 255, 255),
    )

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == QUIT:
                return "quit"

            if event.type == KEYDOWN:

                if event.key == K_r:
                    return "retry"

                if event.key == K_ESCAPE:
                    return "quit"

        screen.fill((0, 0, 0))

        screen.blit(
            game_over,
            game_over.get_rect(
                center=(screen.get_width() // 2, 250)
            ),
        )

        screen.blit(
            volver,
            volver.get_rect(
                center=(screen.get_width() // 2, 400)
            ),
        )

        screen.blit(
            salir,
            salir.get_rect(
                center=(screen.get_width() // 2, 460)
            ),
        )

        pygame.display.flip()

        clock.tick(60)