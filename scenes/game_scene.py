if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

from elements import Enemy, Player
from elements.crosshair import Crosshair

def gameloop(screen):
    # * Preparamos la escena de juego, cargando los elementos que se van a usar en el loop principal

    # ? Añadir fondo del display
    background_image = pygame.image.load("assets/background.png").convert()

    # ? Crear la instancia de jugador
    player = Player(screen)

    crosshair = Crosshair()
    pygame.mouse.set_visible(False)

    # ? Crear los grupos de sprites
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # ? Crear el generador de enemigos
    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 600)

    # ? Crear el reloj del juego
    clock = pygame.time.Clock()
    font_timer = pygame.font.Font(None, 36)

    running = True  # variable booleana para manejar el loop

    # * Loop principal del juego, todo lo que ocurre en el juego se hace dentro de este loop
    while running:
        # ? Dibujar la imagen de fondo en la ventana
        screen.blit(background_image, (0, 0))

        # Iteramos sobre cada evento en la cola
        for event in pygame.event.get():
            if event.type == KEYDOWN:  # se presiono una tecla?
                if event.key == K_ESCAPE:  # era la tecla de escape?
                    running = False  # terminamos el loop

            elif event.type == QUIT:  # fue un click al cierre de la ventana?
                running = False  # terminamos el loop

            # ? Generar enemigos
            elif event.type == ADDENEMY:
                new_enemy = Enemy(screen)
                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

            # TODO (2.5): Disparar balas al hacer click con el mouse
            elif event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                player.shoot(mouse_pos)

        # ? Actualizar el estado interno de los sprites (posiciones, etc)
        pressed_keys = pygame.key.get_pressed()
        player.update(pressed_keys)
        enemies.update()
        crosshair.update()

        # ? Dibujar los sprites actualizados en la ventana
        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)

        # TODO (2.5): Dibujar las balas en la ventana
        for bullet in player.bullets:
            screen.blit(bullet.image, bullet.rect)

        if player.sobrecalentado:

            tiempo_pasado = pygame.time.get_ticks() - player.inicio_sobrecalentamiento

            tiempo_restante = (
                player.tiempo_sobrecalentamiento - tiempo_pasado
            ) / 1000

            tiempo_restante = max(0, tiempo_restante)

            texto_timer = font_timer.render(
                f"SOBRECALENTADO: {tiempo_restante:.1f}s",
                True,
                (255, 0, 0),
            )

            screen.blit(texto_timer, (20, 20))

        else:

            texto_timer = font_timer.render(
                f"CALOR: {player.disparos}/{player.max_disparos}",
                True,
                (255, 255, 255),
            )

            screen.blit(texto_timer, (20, 20))

        screen.blit(crosshair.image, crosshair.rect)

        # ? Calcular colisiones entre jugador y enemigos
        if pygame.sprite.spritecollideany(player, enemies):
            player.kill()
            pygame.mouse.set_visible(True)
            return "dead"

        # TODO (2.6): Calcular colisiones entre balas y enemigos
        pygame.sprite.groupcollide(
            player.bullets,
            enemies,
            True,
            True,
        )

        # ? Actualizar la ventana para reflejar todos los cambios
        pygame.display.flip()

        # ? Controlar la velocidad de fotogramas
        clock.tick(60)
