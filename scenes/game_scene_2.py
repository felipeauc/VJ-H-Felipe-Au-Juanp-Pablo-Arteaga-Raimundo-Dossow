if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, KEYDOWN, MOUSEBUTTONDOWN, QUIT

import customization

from elements import Crosshair, EnemyLevel2, Player, PowerUp


#---- FEATURE MENU PAUSA - CAMBIAR MODO DE PANTALLA ----
def cambiar_modo_pantalla(pantalla_completa):

    if pantalla_completa:
        screen = pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)

    else:
        screen = pygame.display.set_mode((1024, 768))

    return screen
#----


def gameloop(screen):
    # * Preparamos la escena de juego, cargando los elementos que se van a usar en el loop principal

    #---- FEATURE MUSICA Y SONIDO - MUSICA DE FONDO ----
    pygame.mixer.music.load("assets/background.ogg")
    pygame.mixer.music.set_volume(0.30)
    pygame.mixer.music.play(-1)

    sonido_powerup = pygame.mixer.Sound("assets/powerup.wav")
    sonido_damage = pygame.mixer.Sound("assets/damage.wav")
    sonido_hit = pygame.mixer.Sound("assets/hit.wav")

    sonido_powerup.set_volume(0.70)
    sonido_damage.set_volume(0.75)
    sonido_hit.set_volume(0.70)
    #----

    #---- FEATURE TIENDA - FONDO SELECCIONADO ----
    background_image = pygame.image.load(customization.obtener_asset("background")).convert()
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))
    #----

    # ? Crear la instancia de jugador
    player = Player(screen)

    #---- FEATURE MIRA ----
    crosshair = Crosshair()
    pygame.mouse.set_visible(False)
    #----

    # ? Crear los grupos de sprites
    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    #---- FEATURE PROGRESION DE NIVELES - DRAGONES NIVEL 2 ----
    enemigos_nivel2 = [
        "assets/bug_D.png",
        "assets/bug_G.png",
        "assets/bug_M.png",
        "assets/bug_S.png",
    ]

    indice_enemigo = 0
    #----

    #---- FEATURE POWER UPS - CREAR GRUPO DE POWER UPS ----
    powerups = pygame.sprite.Group()
    #----

    # ? Crear el generador de enemigos
    ADDENEMY = pygame.USEREVENT + 1

    #---- FEATURE PROGRESION DE NIVELES - DIFICULTAD NIVEL 2 ----
    pygame.time.set_timer(ADDENEMY, 450)
    #----

    #---- FEATURE POWER UPS - CREAR GENERADOR DE POWER UPS ----
    ADDPOWERUP = pygame.USEREVENT + 2
    pygame.time.set_timer(ADDPOWERUP, 8000)
    #----

    #---- FEATURE POWER UPS - ICONOS DE MUNICION ----
    icono_flecha = pygame.image.load(customization.obtener_asset("bullet")).convert_alpha()
    icono_flecha = pygame.transform.scale(icono_flecha, (44, 16))

    icono_flecha_sombra = icono_flecha.copy()
    icono_flecha_sombra.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    icono_flecha_rapid = pygame.image.load("assets/bullet_rapid_fire.png").convert_alpha()
    icono_flecha_rapid = pygame.transform.scale(icono_flecha_rapid, (44, 16))
    #----

    #---- FEATURE VIDAS DEL JUGADOR - ICONOS CORAZON ----
    icono_corazon = pygame.image.load("assets/heart.png").convert_alpha()
    icono_corazon = pygame.transform.scale(icono_corazon, (34, 34))

    icono_corazon_shield = pygame.image.load("assets/heart_shield.png").convert_alpha()
    icono_corazon_shield = pygame.transform.scale(icono_corazon_shield, (34, 34))
    #----

    #---- FEATURE HABILIDAD ESPECIAL - ESTELAS DASH ----
    estelas_dash = []
    duracion_estela = 300
    #----

    #---- FEATURE MENU PAUSA - CONFIGURACION ----
    pausado = False
    inicio_pausa = 0
    pantalla_completa = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)

    boton_reanudar = pygame.Rect(0, 0, 320, 60)
    boton_inicio = pygame.Rect(0, 0, 320, 60)
    boton_pantalla = pygame.Rect(0, 0, 320, 60)
    boton_salir = pygame.Rect(0, 0, 320, 60)

    boton_reanudar.center = (screen.get_width() // 2, 335)
    boton_inicio.center = (screen.get_width() // 2, 410)
    boton_pantalla.center = (screen.get_width() // 2, 485)
    boton_salir.center = (screen.get_width() // 2, 560)

    font_pausa = pygame.font.Font(None, 75)
    font_boton = pygame.font.Font(None, 35)
    #----

    estadistica = 0
    ultimo_segundo = pygame.time.get_ticks()
    font_puntos = pygame.font.Font(None, 45)

    # ? Crear el reloj del juego
    clock = pygame.time.Clock()

    running = True

    # * Loop principal del juego, todo lo que ocurre en el juego se hace dentro de este loop
    while running:

        # ? Dibujar la imagen de fondo en la ventana
        screen.blit(background_image, (0, 0))

        # Iteramos sobre cada evento en la cola
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)
                return "quit"

            #---- FEATURE MENU PAUSA - CONTROLES ----
            if pausado:

                if event.type == KEYDOWN:

                    if event.key == K_ESCAPE:

                        tiempo_pausa = pygame.time.get_ticks() - inicio_pausa

                        if player.sobrecalentado:
                            player.inicio_sobrecalentamiento += tiempo_pausa

                        if player.rapid_fire:
                            player.fin_rapid_fire += tiempo_pausa

                        player.ultimo_dash += tiempo_pausa

                        for i in range(len(estelas_dash)):
                            inicio, fin, tiempo_inicio = estelas_dash[i]
                            estelas_dash[i] = (inicio, fin, tiempo_inicio + tiempo_pausa)

                        pausado = False

                        pygame.mixer.music.unpause()
                        pygame.mouse.set_visible(False)

                if event.type == MOUSEBUTTONDOWN and event.button == 1:

                    if boton_reanudar.collidepoint(event.pos):

                        tiempo_pausa = pygame.time.get_ticks() - inicio_pausa

                        if player.sobrecalentado:
                            player.inicio_sobrecalentamiento += tiempo_pausa

                        if player.rapid_fire:
                            player.fin_rapid_fire += tiempo_pausa

                        player.ultimo_dash += tiempo_pausa

                        for i in range(len(estelas_dash)):
                            inicio, fin, tiempo_inicio = estelas_dash[i]
                            estelas_dash[i] = (inicio, fin, tiempo_inicio + tiempo_pausa)

                        pausado = False

                        pygame.mixer.music.unpause()
                        pygame.mouse.set_visible(False)

                    elif boton_inicio.collidepoint(event.pos):

                        pygame.mixer.music.stop()
                        pygame.mouse.set_visible(True)

                        return "menu"

                    elif boton_pantalla.collidepoint(event.pos):

                        pantalla_completa = not pantalla_completa
                        screen = cambiar_modo_pantalla(pantalla_completa)

                        background_image = pygame.image.load(customization.obtener_asset("background")).convert()
                        background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

                    elif boton_salir.collidepoint(event.pos):

                        pygame.mixer.music.stop()
                        pygame.mouse.set_visible(True)

                        return "quit"

                continue
            #----

            if event.type == KEYDOWN:

                #---- FEATURE MENU PAUSA - ACTIVAR PAUSA ----
                if event.key == K_ESCAPE:

                    pausado = True
                    inicio_pausa = pygame.time.get_ticks()

                    pygame.mixer.music.pause()
                    pygame.mouse.set_visible(True)
                #----

                #---- FEATURE HABILIDAD ESPECIAL - ACTIVAR DASH ----
                if event.key == K_SPACE:

                    resultado_dash = player.dash(pygame.key.get_pressed())

                    if resultado_dash is not None:
                        inicio, fin = resultado_dash
                        estelas_dash.append((inicio, fin, pygame.time.get_ticks()))
                #----

            #---- FEATURE PROGRESION DE NIVELES - GENERAR DRAGONES NIVEL 2 ----
            elif event.type == ADDENEMY:

                ruta_enemigo = enemigos_nivel2[indice_enemigo]
                indice_enemigo = (indice_enemigo + 1) % len(enemigos_nivel2)

                new_enemy = EnemyLevel2(screen, ruta_enemigo)

                enemies.add(new_enemy)
                all_sprites.add(new_enemy)
            #----

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

        if not pausado:

            #---- FEATURE POWER UPS - DISPARO AUTOMATICO RAPID FIRE ----
            if player.rapid_fire and pygame.mouse.get_pressed()[0]:
                player.shoot(pygame.mouse.get_pos())
            #----

            # ? Actualizar el estado interno de los sprites
            pressed_keys = pygame.key.get_pressed()

            player.update(pressed_keys)
            enemies.update()
            crosshair.update()

            #---- FEATURE POWER UPS - ACTUALIZAR POWER UPS ----
            powerups.update()
            #----

            ahora_puntos = pygame.time.get_ticks()

            if ahora_puntos - ultimo_segundo >= 1000:
                estadistica += 1
                ultimo_segundo += 1000

        #---- FEATURE MENU PAUSA - TIEMPO VISUAL CONGELADO ----
        if pausado:
            tiempo_visual = inicio_pausa

        else:
            tiempo_visual = pygame.time.get_ticks()
        #----

        #---- FEATURE HABILIDAD ESPECIAL - DIBUJAR ESTELA DASH ----
        for estela in estelas_dash[:]:

            inicio, fin, tiempo_inicio = estela
            tiempo_pasado = tiempo_visual - tiempo_inicio

            if tiempo_pasado >= duracion_estela:

                if not pausado:
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

        #---- FEATURE VIDAS DEL JUGADOR - HUD DE CORAZONES ----
        for i in range(player.vidas):

            x = 20 + i * 40

            if player.escudo:
                screen.blit(icono_corazon_shield, (x, 20))

            else:
                screen.blit(icono_corazon, (x, 20))
        #----

        sombra_puntos = font_puntos.render(f"PUNTOS: {estadistica}", True, (0, 0, 0))
        texto_puntos = font_puntos.render(f"PUNTOS: {estadistica}", True, (255, 255, 255))
        pos_x_puntos = screen.get_width() - texto_puntos.get_width() - 20

        screen.blit(sombra_puntos, (pos_x_puntos + 2, 22))
        screen.blit(texto_puntos, (pos_x_puntos, 20))

        #---- FEATURE POWER UPS - HUD DE MUNICION CON FLECHAS ----
        inicio_x = 20
        inicio_y = 62
        separacion = 8
        ancho_icono = icono_flecha.get_width()

        for i in range(player.max_disparos):

            x = inicio_x + i * (ancho_icono + separacion)
            posicion_icono = (x, inicio_y)

            if player.rapid_fire:
                screen.blit(icono_flecha_rapid, posicion_icono)

            elif i >= player.max_disparos - player.disparos:
                screen.blit(icono_flecha_sombra, posicion_icono)

            else:
                screen.blit(icono_flecha, posicion_icono)
        #----

        #---- FEATURE HABILIDAD ESPECIAL - BARRA DE MANA DASH ----
        mana_x = 20
        mana_y = 90
        mana_ancho = 200
        mana_alto = 9

        tiempo_dash = tiempo_visual - player.ultimo_dash
        mana_dash = min(1, tiempo_dash / player.cooldown_dash)

        pygame.draw.rect(screen, (30, 30, 35), (mana_x, mana_y, mana_ancho, mana_alto), border_radius=4)
        pygame.draw.rect(screen, (255, 200, 40), (mana_x, mana_y, int(mana_ancho * mana_dash), mana_alto), border_radius=4)
        #----

        #---- FEATURE POWER UPS - BARRA RAPID FIRE COMPACTA ----
        if player.rapid_fire:

            barra_x = 20
            barra_y = 106
            barra_ancho = 200
            barra_alto = 5

            tiempo_restante = player.fin_rapid_fire - tiempo_visual
            progreso = tiempo_restante / player.duracion_rapid_fire
            progreso = max(0, min(1, progreso))

            pygame.draw.rect(screen, (35, 35, 40), (barra_x, barra_y, barra_ancho, barra_alto), border_radius=3)
            pygame.draw.rect(screen, (255, 205, 40), (barra_x, barra_y, int(barra_ancho * progreso), barra_alto), border_radius=3)
        #----

        if not pausado:

            #---- FEATURE POWER UPS - RECOGER POWER UP ----
            powerups_recogidos = pygame.sprite.spritecollide(player, powerups, True)

            for powerup in powerups_recogidos:

                #---- FEATURE MUSICA Y SONIDO - SONIDO POWER UP ----
                sonido_powerup.play()
                #----

                player.activar_powerup(powerup.tipo)
            #----

            #---- FEATURE VIDAS DEL JUGADOR - DAÑO DE ENEMIGOS ----
            enemigos_tocando = pygame.sprite.spritecollide(player, enemies, False)

            if enemigos_tocando:

                enemigo = enemigos_tocando[0]
                enemigo.kill()

                if player.escudo:

                    player.escudo = False
                    player.actualizar_apariencia()

                else:

                    #---- FEATURE MUSICA Y SONIDO - SONIDO DE DAÑO ----
                    sonido_damage.play()
                    #----

                    murio = player.recibir_dano()

                    if murio:

                        player.kill()

                        pygame.mixer.music.stop()
                        pygame.mouse.set_visible(True)

                        return ("dead", estadistica)
            #----

            # TODO (2.6): Calcular colisiones entre balas y enemigos
            colisiones_balas = pygame.sprite.groupcollide(player.bullets, enemies, True, True)

            for lista_enemigos in colisiones_balas.values():
                estadistica += len(lista_enemigos) * 5

            #---- FEATURE MUSICA Y SONIDO - HIT DE FLECHA CONTRA BUG ----
            if colisiones_balas:
                sonido_hit.play()
            #----

            #---- FEATURE MIRA - DIBUJAR CROSSHAIR ----
            screen.blit(crosshair.image, crosshair.rect)
            #----

        #---- FEATURE MENU PAUSA - DIBUJAR PAUSA ----
        if pausado:

            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            titulo_pausa = font_pausa.render("PAUSA", True, (255, 215, 80))
            screen.blit(titulo_pausa, titulo_pausa.get_rect(center=(screen.get_width() // 2, 230)))

            if pantalla_completa:
                texto_pantalla = "MODO VENTANA"

            else:
                texto_pantalla = "PANTALLA COMPLETA"

            mouse = pygame.mouse.get_pos()

            botones = [
                (boton_reanudar, "REANUDAR"),
                (boton_inicio, "VOLVER AL INICIO"),
                (boton_pantalla, texto_pantalla),
                (boton_salir, "SALIR"),
            ]

            for boton, texto in botones:

                if boton.collidepoint(mouse):
                    color = (255, 205, 60)

                else:
                    color = (40, 45, 55)

                pygame.draw.rect(screen, color, boton, border_radius=10)
                pygame.draw.rect(screen, (255, 215, 80), boton, 3, border_radius=10)

                texto_render = font_boton.render(texto, True, (255, 255, 255))
                screen.blit(texto_render, texto_render.get_rect(center=boton.center))
        #----

        # ? Actualizar la ventana para reflejar todos los cambios
        pygame.display.flip()

        # ? Controlar la velocidad de fotogramas
        clock.tick(60)

    pygame.mixer.music.stop()
    pygame.mouse.set_visible(True)

    return "quit"