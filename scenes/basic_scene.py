if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT


def gameloop(screen):

    # Inicializamos el reloj
    clock = pygame.time.Clock()

    running = True

    # Definimos la fuente y texto a usar
    font = pygame.font.Font(None, 48)
    line1 = font.render("Estamos en basic_scene", True, (255, 255, 255))
    line2 = font.render("Aprieta ESC para salir de esta escena", True, (255, 255, 255))

    # Definimos las posiciones de los textos
    line1_rect = line1.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 - 25)
    )

    line2_rect = line2.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 + 25)
    )

    # Iniciamos el loop principal de la escena inicial
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == QUIT:
                running = False

        # Limpiar pantalla (fondo negro)
        screen.fill((0, 0, 0))

        # Dibujar textos
        screen.blit(line1, line1_rect)
        screen.blit(line2, line2_rect)

        # Actualizar pantalla
        pygame.display.flip()

        # Limitar FPS
        clock.tick(30)
