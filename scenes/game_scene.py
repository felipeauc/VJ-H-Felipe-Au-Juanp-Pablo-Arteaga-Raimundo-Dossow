if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

from elements import Crosshair, Enemy, Player, PowerUp


def gameloop(screen):
    # * Preparamos la escena de juego, cargando los elementos que se van a usar en el loop principal

    # ? Añadir fondo del display
    background_image = pygame.image.load("assets/background.png").convert()
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

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

    #---- FEATURE POWER UPS - ICONOS DE MUNICION ----
    icono_flecha = pygame.image.load("assets/bullet.png").convert_alpha()
    icono_flecha = pygame.transform.scale(icono_flecha, (44, 16))

    icono_flecha_sombra = icono_flecha.copy()
    icono_flecha_sombra.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    #----

    #---- FEATURE HABILIDAD ESPECIAL - ESTELAS DASH ----
    estelas_dash = []
    duracion_estela = 300
    #----

    # ? Crear el reloj del juego
    clock = pygame.time.Clock()

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

                #---- FEATURE HABILIDAD ESPECIAL - ACTIVAR DASH ----
                if event.key == K_SPACE:
                    resultado_dash = player.dash(pygame.key.get_pressed())

                    if resultado_dash is not None:
                        inicio, fin = resultado_dash
                        estelas_dash.append((inicio, fin, pygame.time.get_ticks()))
                #----

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
            player.shoot(pygame.mouse.get_pos())
        #----

        # ? Actualizar el estado interno de los sprites (posiciones, etc)
        pressed_keys = pygame.key.get_pressed()

        player.update(pressed_keys)
        enemies.update()
        crosshair.update()

        #---- FEATURE POWER UPS - ACTUALIZAR POWER UPS ----
        powerups.update()
        #----

        #---- FEATURE HABILIDAD ESPECIAL - DIBUJAR ESTELA DASH ----
        ahora = pygame.time.get_ticks()

        for estela in estelas_dash[:]:
            inicio, fin, tiempo_inicio = estela
            tiempo_pasado = ahora - tiempo_inicio

            if tiempo_pasado >= duracion_estela:
                estelas_dash.remove(estela)
                continue

            transparencia = int(200 * (1 - tiempo_pasado / duracion_estela))
            superficie_estela = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)

            pygame.draw.line(superficie_estela, (255, 180, 0, transparencia), inicio, fin, 30)
            pygame.draw.line(superficie_estela, (255, 245, 120, transparencia), inicio, fin, 9)

            screen.blit(superficie_estela, (0, 0))
        #----

        # ? Dibujar los sprites actualizados en la ventana
        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)

        #---- FEATURE POWER UPS - DIBUJAR POWER UPS ----
        for powerup in powerups:
            screen.blit(powerup.image, powerup.rect)
        #----

        # TODO (2.5): Dibujar las balas en la ventana
        for bullet in player.bullets:
            screen.blit(bullet.image, bullet.rect)

        #---- FEATURE POWER UPS - HUD DE MUNICION CON FLECHAS ----
        inicio_x = 20
        inicio_y = 20
        separacion = 8
        ancho_icono = icono_flecha.get_width()

        for i in range(player.max_disparos):

            x = inicio_x + i * (ancho_icono + separacion)
            posicion_icono = (x, inicio_y)

            if player.rapid_fire:
                screen.blit(icono_flecha, posicion_icono)

            elif i >= player.max_disparos - player.disparos:
                screen.blit(icono_flecha_sombra, posicion_icono)

            else:
                screen.blit(icono_flecha, posicion_icono)
        #----

        #---- FEATURE POWER UPS - BARRA DE RECARGA COMPACTA ----
        ancho_total = player.max_disparos * ancho_icono + (player.max_disparos - 1) * separacion

        barra_x = inicio_x
        barra_y = inicio_y + icono_flecha.get_height() + 6
        barra_alto = 5

        if player.sobrecalentado:

            tiempo_pasado = pygame.time.get_ticks() - player.inicio_sobrecalentamiento
            progreso = tiempo_pasado / player.tiempo_sobrecalentamiento
            progreso = max(0, min(1, progreso))

            pygame.draw.rect(screen, (35, 35, 40), (barra_x, barra_y, ancho_total, barra_alto), border_radius=3)
            pygame.draw.rect(screen, (255, 90, 55), (barra_x, barra_y, int(ancho_total * progreso), barra_alto), border_radius=3)
        #----

        #---- FEATURE POWER UPS - BARRA RAPID FIRE COMPACTA ----
        if player.rapid_fire:

            tiempo_restante = player.fin_rapid_fire - pygame.time.get_ticks()
            progreso = tiempo_restante / player.duracion_rapid_fire
            progreso = max(0, min(1, progreso))

            pygame.draw.rect(screen, (35, 35, 40), (barra_x, barra_y, ancho_total, barra_alto), border_radius=3)
            pygame.draw.rect(screen, (255, 205, 40), (barra_x, barra_y, int(ancho_total * progreso), barra_alto), border_radius=3)
        #----

        #---- FEATURE POWER UPS - RECOGER POWER UP ----
        powerups_recogidos = pygame.sprite.spritecollide(player, powerups, True)

        for powerup in powerups_recogidos:
            player.activar_powerup(powerup.tipo)
        #----

        # ? Calcular colisiones entre jugador y enemigos

        #---- FEATURE POWER UPS - ESCUDO CONTRA BUG ----
        enemigos_tocando = pygame.sprite.spritecollide(player, enemies, False)

        if enemigos_tocando:

            if player.escudo:
                player.escudo = False
                enemigos_tocando[0].kill()
                player.actualizar_apariencia()

            else:
                player.kill()
                pygame.mouse.set_visible(True)
                return "dead"
        #----

        # TODO (2.6): Calcular colisiones entre balas y enemigos
        pygame.sprite.groupcollide(player.bullets, enemies, True, True)

        screen.blit(crosshair.image, crosshair.rect)

        # ? Actualizar la ventana para reflejar todos los cambios
        pygame.display.flip()

        # ? Controlar la velocidad de fotogramas
        clock.tick(60)

    pygame.mouse.set_visible(True)

    return "quit"