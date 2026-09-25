if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, KEYDOWN, MOUSEBUTTONDOWN, QUIT, K_RSHIFT
from pygame.math import Vector2

import customization

from elements import Crosshair, Enemy, Player, PowerUp, Player2, OndaExpansiva


def cambiar_modo_pantalla(pantalla_completa):

    if pantalla_completa:
        return pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)

    return pygame.display.set_mode((1024, 768))


# balas con penetracion contra los bichos normales
def procesar_balas(player, enemies, sonido_hit):

    puntos = 0

    for bala in player.bullets.sprites():

        golpeados = pygame.sprite.spritecollide(bala, enemies, False)

        for enemigo in golpeados:

            if enemigo in bala.enemigos_golpeados:
                continue

            bala.enemigos_golpeados.add(enemigo)

            enemigo.kill()
            puntos += 5

            sonido_hit.play()

            # kill ahora gasta una penetracion
            bala.kill()

            if not bala.alive():
                break

    return puntos


def gameloop(screen, cantidad_jugadores=1):

    # audio
    pygame.mixer.music.load("assets/background.ogg")
    pygame.mixer.music.set_volume(0.30)
    pygame.mixer.music.play(-1)

    sonido_powerup = pygame.mixer.Sound("assets/powerup.wav")
    sonido_damage = pygame.mixer.Sound("assets/damage.wav")
    sonido_hit = pygame.mixer.Sound("assets/hit.wav")

    sonido_powerup.set_volume(0.70)
    sonido_damage.set_volume(0.75)
    sonido_hit.set_volume(0.70)

    # fondo elegido en tienda
    background_image = pygame.image.load(customization.obtener_asset("background")).convert()
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    player = Player(screen)

    crosshair = Crosshair()
    pygame.mouse.set_visible(False)

    enemies = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    # coop
    dos_jugadores = cantidad_jugadores == 2

    player2 = Player2(screen)

    if dos_jugadores:
        all_sprites.add(player2)

    onda = OndaExpansiva()

    powerups = pygame.sprite.Group()

    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 600)

    ADDPOWERUP = pygame.USEREVENT + 2
    pygame.time.set_timer(ADDPOWERUP, 8000)

    # iconos balas
    icono_flecha = pygame.image.load(customization.obtener_asset("bullet")).convert_alpha()
    icono_flecha = pygame.transform.scale(icono_flecha, (44, 16))

    icono_flecha_sombra = icono_flecha.copy()
    icono_flecha_sombra.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    icono_flecha_rapid = pygame.image.load("assets/bullet_rapid_fire.png").convert_alpha()
    icono_flecha_rapid = pygame.transform.scale(icono_flecha_rapid, (44, 16))

    # corazones
    icono_corazon = pygame.image.load("assets/heart.png").convert_alpha()
    icono_corazon = pygame.transform.scale(icono_corazon, (34, 34))

    icono_corazon_shield = pygame.image.load("assets/heart_shield.png").convert_alpha()
    icono_corazon_shield = pygame.transform.scale(icono_corazon_shield, (34, 34))

    # dash trail
    estelas_dash = []
    duracion_estela = 300

    # pausa
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

    estadistica = 0
    ultimo_segundo = pygame.time.get_ticks()
    font_puntos = pygame.font.Font(None, 45)

    clock = pygame.time.Clock()

    while True:

        screen.blit(background_image, (0, 0))

        # ================= EVENTOS =================
        for event in pygame.event.get():

            if event.type == QUIT:
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)
                return "quit"

            # cosas menu pausa
            if pausado:

                reanudar = False

                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    reanudar = True

                if event.type == MOUSEBUTTONDOWN and event.button == 1:

                    if boton_reanudar.collidepoint(event.pos):
                        reanudar = True

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

                if reanudar:

                    tiempo_pausa = pygame.time.get_ticks() - inicio_pausa
                    ultimo_segundo += tiempo_pausa

                    if player.sobrecalentado:
                        player.inicio_sobrecalentamiento += tiempo_pausa

                    if player.rapid_fire:
                        player.fin_rapid_fire += tiempo_pausa

                    player.ultimo_dash += tiempo_pausa
                    player2.ultima_embestida += tiempo_pausa

                    if player2.furia:
                        player2.fin_furia += tiempo_pausa

                    for i in range(len(estelas_dash)):
                        inicio, fin, tiempo_inicio = estelas_dash[i]
                        estelas_dash[i] = (inicio, fin, tiempo_inicio + tiempo_pausa)

                    pausado = False
                    pygame.mixer.music.unpause()
                    pygame.mouse.set_visible(False)

                continue

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    pausado = True
                    inicio_pausa = pygame.time.get_ticks()
                    pygame.mixer.music.pause()
                    pygame.mouse.set_visible(True)

                # dash Jorge
                if event.key == K_SPACE and not player.caido:

                    resultado_dash = player.dash(pygame.key.get_pressed())

                    if resultado_dash is not None:
                        inicio, fin = resultado_dash
                        estelas_dash.append((inicio, fin, pygame.time.get_ticks()))

                # embestida pato
                if event.key == K_RSHIFT and dos_jugadores and not player2.caido:

                    resultado = player2.embestida(pygame.key.get_pressed())

                    if resultado is not None:

                        inicio, fin = resultado
                        estelas_dash.append((inicio, fin, pygame.time.get_ticks()))

                        golpeados = 0

                        for paso in range(11):

                            x = inicio[0] + (fin[0] - inicio[0]) * paso / 10
                            y = inicio[1] + (fin[1] - inicio[1]) * paso / 10

                            player2.rect.center = (x, y)

                            enemigos_golpeados = pygame.sprite.spritecollide(player2, enemies, True)
                            golpeados += len(enemigos_golpeados)

                        player2.rect.center = fin

                        if golpeados > 0:
                            estadistica += golpeados * 5
                            sonido_hit.play()

            elif event.type == ADDENEMY:

                new_enemy = Enemy(screen)

                enemies.add(new_enemy)
                all_sprites.add(new_enemy)

            elif event.type == ADDPOWERUP:

                if len(powerups) == 0:
                    powerups.add(PowerUp(screen))

            elif event.type == MOUSEBUTTONDOWN:

                if event.button == 1 and not player.caido:
                    player.shoot(pygame.mouse.get_pos())

        # ================= UPDATE =================
        if not pausado:

            if player.rapid_fire and pygame.mouse.get_pressed()[0] and not player.caido:
                player.shoot(pygame.mouse.get_pos())

            pressed_keys = pygame.key.get_pressed()

            if not player.caido:
                player.update(pressed_keys)

            else:
                player.bullets.update()

            if dos_jugadores and not player2.caido:
                player2.update(pressed_keys)

            enemies.update()
            powerups.update()
            crosshair.update()

            # onda coop
            cargando = dos_jugadores and not player.caido and not player2.caido and pressed_keys[K_SPACE] and pressed_keys[K_RSHIFT]

            centro_x = (player.rect.centerx + player2.rect.centerx) // 2
            centro_y = (player.rect.centery + player2.rect.centery) // 2

            if onda.update(cargando, (centro_x, centro_y)):

                estadistica += len(enemies) * 5

                for enemigo in enemies.sprites():
                    enemigo.kill()

            ahora = pygame.time.get_ticks()

            if ahora - ultimo_segundo >= 1000:
                estadistica += 1
                ultimo_segundo += 1000

        tiempo_visual = inicio_pausa if pausado else pygame.time.get_ticks()

        # trail dash
        for estela in estelas_dash[:]:

            inicio, fin, tiempo_inicio = estela
            pasado = tiempo_visual - tiempo_inicio

            if pasado >= duracion_estela:

                if not pausado:
                    estelas_dash.remove(estela)

                continue

            alpha = int(200 * (1 - pasado / duracion_estela))

            superficie = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.line(superficie, (255, 180, 0, alpha), inicio, fin, 30)
            pygame.draw.line(superficie, (255, 245, 120, alpha), inicio, fin, 9)

            screen.blit(superficie, (0, 0))

        # ================= DIBUJAR =================
        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)

        # barra revivir
        if dos_jugadores:

            for jugador in [player, player2]:

                if jugador.caido:

                    progreso = jugador.progreso_revivir / 300
                    x = jugador.rect.centerx - 40
                    y = jugador.rect.top - 14

                    pygame.draw.rect(screen, (30, 30, 35), (x, y, 80, 8), border_radius=4)
                    pygame.draw.rect(screen, (90, 230, 120), (x, y, int(80 * progreso), 8), border_radius=4)

        for powerup in powerups:
            screen.blit(powerup.image, powerup.rect)

        if onda.animacion > 0:
            screen.blit(onda.image, onda.rect)

        for bala in player.bullets:
            screen.blit(bala.image, bala.rect)

        # vida j1
        for i in range(player.vidas):

            x = 20 + i * 40

            if player.escudo:
                screen.blit(icono_corazon_shield, (x, 20))

            else:
                screen.blit(icono_corazon, (x, 20))

        # puntos
        texto_puntos = font_puntos.render(f"PUNTOS: {estadistica}", True, (255, 255, 255))
        sombra_puntos = font_puntos.render(f"PUNTOS: {estadistica}", True, (0, 0, 0))
        px = screen.get_width() - texto_puntos.get_width() - 20

        screen.blit(sombra_puntos, (px + 2, 22))
        screen.blit(texto_puntos, (px, 20))

        # municion
        for i in range(player.max_disparos):

            x = 20 + i * (icono_flecha.get_width() + 8)

            if player.rapid_fire:
                screen.blit(icono_flecha_rapid, (x, 62))

            elif i >= player.max_disparos - player.disparos:
                screen.blit(icono_flecha_sombra, (x, 62))

            else:
                screen.blit(icono_flecha, (x, 62))

        # barra dash
        mana_dash = min(1, (tiempo_visual - player.ultimo_dash) / player.cooldown_dash)

        pygame.draw.rect(screen, (30, 30, 35), (20, 90, 200, 9), border_radius=4)
        pygame.draw.rect(screen, (255, 200, 40), (20, 90, int(200 * mana_dash), 9), border_radius=4)

        # rapid fire
        if player.rapid_fire:

            restante = player.fin_rapid_fire - tiempo_visual
            progreso = max(0, min(1, restante / player.duracion_rapid_fire))

            pygame.draw.rect(screen, (35, 35, 40), (20, 106, 200, 5), border_radius=3)
            pygame.draw.rect(screen, (255, 205, 40), (20, 106, int(200 * progreso), 5), border_radius=3)

        # j2 hud
        if dos_jugadores:

            for i in range(player2.vidas):

                x = screen.get_width() - 54 - i * 40

                if player2.escudo:
                    screen.blit(icono_corazon_shield, (x, 65))

                else:
                    screen.blit(icono_corazon, (x, 65))

            barra_x = screen.get_width() - 220
            progreso = min(1, (tiempo_visual - player2.ultima_embestida) / player2.cooldown_embestida)

            color = (255, 120, 40) if player2.furia else (80, 180, 255)

            pygame.draw.rect(screen, (30, 30, 35), (barra_x, 105, 200, 9), border_radius=4)
            pygame.draw.rect(screen, color, (barra_x, 105, int(200 * progreso), 9), border_radius=4)

            # onda
            onda_x = screen.get_width() // 2 - 120

            if onda.espera > 0:
                progreso_onda = 1 - onda.espera / onda.cooldown
                color_onda = (110, 110, 120)

            elif onda.carga > 0:
                progreso_onda = onda.carga / onda.tiempo_carga
                color_onda = (255, 255, 255)

            else:
                progreso_onda = 1
                color_onda = (170, 90, 255)

            pygame.draw.rect(screen, (30, 30, 35), (onda_x, 24, 240, 12), border_radius=5)
            pygame.draw.rect(screen, color_onda, (onda_x, 24, int(240 * progreso_onda), 12), border_radius=5)

        # ================= COLISIONES =================
        if not pausado:

            # recoger powerup jorge
            if not player.caido:

                recogidos = pygame.sprite.spritecollide(player, powerups, True)

                for powerup in recogidos:
                    sonido_powerup.play()
                    player.activar_powerup(powerup.tipo)

            # powerup player2
            if dos_jugadores and not player2.caido:

                recogidos = pygame.sprite.spritecollide(player2, powerups, True)

                for powerup in recogidos:
                    sonido_powerup.play()
                    player2.activar_powerup(powerup.tipo)

            # choque jorge
            enemigos_tocando = pygame.sprite.spritecollide(player, enemies, False)

            if enemigos_tocando and not player.caido:

                enemigos_tocando[0].kill()

                if player.escudo:
                    player.escudo = False
                    player.actualizar_apariencia()

                else:
                    sonido_damage.play()

                    if player.recibir_dano():
                        player.caer()

            # choque pato
            if dos_jugadores and not player2.caido:

                enemigos_tocando_2 = pygame.sprite.spritecollide(player2, enemies, False)

                if enemigos_tocando_2:

                    enemigos_tocando_2[0].kill()

                    if player2.escudo:
                        player2.escudo = False
                        player2.actualizar_apariencia()

                    else:
                        sonido_damage.play()

                        if player2.recibir_dano():
                            player2.caer()

            # REVIVIR
            if dos_jugadores:

                for caido, rescatista in [(player, player2), (player2, player)]:

                    if caido.caido and not rescatista.caido:

                        distancia = (Vector2(caido.rect.center) - Vector2(rescatista.rect.center)).length()

                        if distancia < 110:
                            caido.progreso_revivir += 1

                        else:
                            caido.progreso_revivir = 0

                        if caido.progreso_revivir >= 300:
                            caido.revivir()
                            sonido_powerup.play()

            # GAME OVER
            if dos_jugadores:
                todos_caidos = player.caido and player2.caido

            else:
                todos_caidos = player.caido

            if todos_caidos:

                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)

                return ("dead", estadistica)

            # sistema nuevo de penetracion
            estadistica += procesar_balas(player, enemies, sonido_hit)

            screen.blit(crosshair.image, crosshair.rect)

        # ================= PAUSA VISUAL =================
        if pausado:

            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            titulo = font_pausa.render("PAUSA", True, (255, 215, 80))
            screen.blit(titulo, titulo.get_rect(center=(screen.get_width() // 2, 230)))

            texto_pantalla = "MODO VENTANA" if pantalla_completa else "PANTALLA COMPLETA"

            mouse = pygame.mouse.get_pos()

            botones = [
                (boton_reanudar, "REANUDAR"),
                (boton_inicio, "VOLVER AL INICIO"),
                (boton_pantalla, texto_pantalla),
                (boton_salir, "SALIR"),
            ]

            for boton, texto in botones:

                color = (255, 205, 60) if boton.collidepoint(mouse) else (40, 45, 55)

                pygame.draw.rect(screen, color, boton, border_radius=10)
                pygame.draw.rect(screen, (255, 215, 80), boton, 3, border_radius=10)

                render = font_boton.render(texto, True, (255, 255, 255))
                screen.blit(render, render.get_rect(center=boton.center))

        pygame.display.flip()
        clock.tick(60)