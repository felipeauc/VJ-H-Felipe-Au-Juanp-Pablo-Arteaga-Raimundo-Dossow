if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

from elements import Crosshair, Enemy, Player, PowerUp


def gameloop(screen):
    # * Preparamos la escena de juego, cargando los elementos que se van a usar en el loop principal

    # ? Añadir fondo del display
    background_image = pygame.image.load("assets/background.png").convert()

    background_image = pygame.transform.scale(
        background_image,
        (
            screen.get_width(),
            screen.get_height(),
        )
    )

    # ? Crear la instancia de jugador
    player = Player(screen)

    crosshair = Crosshair()
    pygame.mouse.set_visible(False)

    # ? Crear los grupos de sprites
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    #---- FEATURE POWER UPS - CREAR GRUPO DE POWER UPS ----
    powerups = pygame.sprite.Group()
    #----

    # ? Crear el generador de enemigos
    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 600)

    #---- FEATURE POWER UPS - CREAR GENERADOR DE POWER UPS ----
    ADDPOWERUP = pygame.USEREVENT + 2
    pygame.time.set_timer(ADDPOWERUP, 8000)
    #----

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

            #---- FEATURE POWER UPS - GENERAR POWER UP ----
            elif event.type == ADDPOWERUP:

                if len(powerups) == 0:

                    new_powerup = PowerUp(screen)

                    powerups.add(new_powerup)
            #----

            # TODO (2.5): Disparar balas al hacer click con el mouse
            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1:

                    mouse_pos = pygame.mouse.get_pos()

                    player.shoot(mouse_pos)

        #---- FEATURE POWER UPS - DISPARO AUTOMATICO RAPID FIRE ----
        if player.rapid_fire and pygame.mouse.get_pressed()[0]:

            player.shoot(
                pygame.mouse.get_pos()
            )
        #----

        # ? Actualizar el estado interno de los sprites (posiciones, etc)
        pressed_keys = pygame.key.get_pressed()

        player.update(pressed_keys)
        enemies.update()
        crosshair.update()

        #---- FEATURE POWER UPS - ACTUALIZAR POWER UPS ----
        powerups.update()
        #----

        # ? Dibujar los sprites actualizados en la ventana
        for entity in all_sprites:

            screen.blit(
                entity.image,
                entity.rect
            )

        #---- FEATURE POWER UPS - DIBUJAR POWER UPS ----
        for powerup in powerups:

            screen.blit(
                powerup.image,
                powerup.rect
            )
        #----

        # TODO (2.5): Dibujar las balas en la ventana
        for bullet in player.bullets:

            screen.blit(
                bullet.image,
                bullet.rect
            )

        #---- FEATURE POWER UPS - DIBUJAR ESCUDO ACTIVO ----
        if player.escudo:

            pygame.draw.circle(
                screen,
                (0, 180, 255),
                player.rect.center,
                48,
                4,
            )
        #----

        #---- FEATURE POWER UPS - MOSTRAR RAPID FIRE ----
        if player.rapid_fire:

            tiempo_restante = (
                player.fin_rapid_fire
                - pygame.time.get_ticks()
            ) / 1000

            tiempo_restante = max(
                0,
                tiempo_restante
            )

            texto_timer = font_timer.render(
                f"RAPID FIRE: {tiempo_restante:.1f}s",
                True,
                (255, 255, 0),
            )

            screen.blit(
                texto_timer,
                (20, 20)
            )
        #----

        elif player.sobrecalentado:

            tiempo_pasado = (
                pygame.time.get_ticks()
                - player.inicio_sobrecalentamiento
            )

            tiempo_restante = (
                player.tiempo_sobrecalentamiento
                - tiempo_pasado
            ) / 1000

            tiempo_restante = max(
                0,
                tiempo_restante
            )

            texto_timer = font_timer.render(
                f"SOBRECALENTADO: {tiempo_restante:.1f}s",
                True,
                (255, 0, 0),
            )

            screen.blit(
                texto_timer,
                (20, 20)
            )

        else:

            texto_timer = font_timer.render(
                f"CALOR: {player.disparos}/{player.max_disparos}",
                True,
                (255, 255, 255),
            )

            screen.blit(
                texto_timer,
                (20, 20)
            )

        #---- FEATURE POWER UPS - MOSTRAR HUD ESCUDO ----
        if player.escudo:

            texto_escudo = font_timer.render(
                "ESCUDO",
                True,
                (0, 200, 255),
            )

            screen.blit(
                texto_escudo,
                (20, 55)
            )
        #----

        #---- FEATURE POWER UPS - RECOGER POWER UP ----
        powerups_recogidos = pygame.sprite.spritecollide(
            player,
            powerups,
            True,
        )

        for powerup in powerups_recogidos:

            player.activar_powerup(
                powerup.tipo
            )
        #----

        # ? Calcular colisiones entre jugador y enemigos

        #---- FEATURE POWER UPS - ESCUDO CONTRA BUG ----
        enemigos_tocando = pygame.sprite.spritecollide(
            player,
            enemies,
            False,
        )

        if enemigos_tocando:

            if player.escudo:

                player.escudo = False

                enemigos_tocando[0].kill()

            else:

                player.kill()

                pygame.mouse.set_visible(True)

                return "dead"
        #----

        # TODO (2.6): Calcular colisiones entre balas y enemigos
        pygame.sprite.groupcollide(
            player.bullets,
            enemies,
            True,
            True,
        )

        screen.blit(
            crosshair.image,
            crosshair.rect
        )

        # ? Actualizar la ventana para reflejar todos los cambios
        pygame.display.flip()

        # ? Controlar la velocidad de fotogramas
        clock.tick(60)

    pygame.mouse.set_visible(True)

    return "quit"