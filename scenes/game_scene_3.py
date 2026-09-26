if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random
import pygame

from pygame.locals import K_ESCAPE, K_SPACE, K_RETURN, KEYDOWN, MOUSEBUTTONDOWN, QUIT, K_RSHIFT
from pygame.math import Vector2

import customization

from elements import Crosshair, EnemyLevel2, Player, PowerUp, Player2, OndaExpansiva, Boss


def cambiar_modo_pantalla(pantalla_completa):
    if pantalla_completa:
        return pygame.display.set_mode((1024, 768), pygame.FULLSCREEN)

    return pygame.display.set_mode((1024, 768))


def hacer_dano(jugador, sonido):
    # inmunidad del Player 2 en dash y 360
    if hasattr(jugador, "es_inmortal") and jugador.es_inmortal():
        return

    if jugador.escudo:
        jugador.escudo = False
        jugador.actualizar_apariencia()

    else:
        sonido.play()

        if jugador.recibir_dano():
            jugador.caer()


def procesar_balas_grupo(player, grupo, sonido_hit, puntos_muerte=5):
    puntos = 0

    for bala in player.bullets.sprites():
        golpeados = pygame.sprite.spritecollide(bala, grupo, False)

        for enemigo in golpeados:
            if enemigo in bala.enemigos_golpeados:
                continue

            bala.enemigos_golpeados.add(enemigo)

            if hasattr(enemigo, "recibir_dano"):
                murio = enemigo.recibir_dano(bala.dano)

            else:
                enemigo.kill()
                murio = True

            sonido_hit.play()

            if murio:
                puntos += puntos_muerte

            bala.kill()

            if not bala.alive():
                break

    return puntos


# permite dispararle a proyectiles Y meteoritos
def procesar_balas_peligros(player, proyectiles_boss, meteoritos, sonido_hit):
    for bala in player.bullets.sprites():
        bala_terminada = False

        for grupo in [proyectiles_boss, meteoritos]:
            golpeados = pygame.sprite.spritecollide(bala, grupo, False)

            for peligro in golpeados:
                if peligro in bala.enemigos_golpeados:
                    continue

                bala.enemigos_golpeados.add(peligro)
                peligro.recibir_dano(bala.dano)

                sonido_hit.play()

                # usa la penetracion de la flecha
                bala.kill()

                if not bala.alive():
                    bala_terminada = True
                    break

            if bala_terminada:
                break


def procesar_balas_boss(player, boss, sonido_hit):
    if boss is None or not boss.alive() or boss.fase_meteoritos:
        return

    for bala in player.bullets.sprites():
        if boss in bala.enemigos_golpeados:
            continue

        if bala.rect.colliderect(boss.rect):
            bala.enemigos_golpeados.add(boss)

            boss.recibir_dano(bala.dano)
            sonido_hit.play()

            bala.kill()


def ataque_360(player2, enemies, subdragones, boss, boss_aparecio, proyectiles_boss, meteoritos, centro, radio, sonido_hit):
    puntos = 0
    pego = False

    # enemigos normales
    if not boss_aparecio:
        for enemigo in enemies.sprites():
            distancia = Vector2(enemigo.rect.center).distance_to(centro)
            radio_enemigo = max(enemigo.rect.width, enemigo.rect.height) / 2

            if distancia <= radio + radio_enemigo:
                murio = enemigo.recibir_dano(player2.dano_360)
                pego = True

                if murio:
                    puntos += 5

    # subdragones
    for enemigo in subdragones.sprites():
        distancia = Vector2(enemigo.rect.center).distance_to(centro)
        radio_enemigo = max(enemigo.rect.width, enemigo.rect.height) / 2

        if distancia <= radio + radio_enemigo:
            murio = enemigo.recibir_dano(player2.dano_360)
            pego = True

            if murio:
                puntos += 8

    # limpiar proyectiles boss
    for proyectil in proyectiles_boss.sprites():
        distancia = Vector2(proyectil.rect.center).distance_to(centro)

        if distancia <= radio + 20:
            proyectil.kill()
            pego = True

    # romper meteoritos
    for meteorito in meteoritos.sprites():
        distancia = Vector2(meteorito.rect.center).distance_to(centro)
        radio_meteorito = max(meteorito.rect.width, meteorito.rect.height) / 2

        if distancia <= radio + radio_meteorito:
            meteorito.recibir_dano(player2.dano_360)
            pego = True

    # pegar boss
    if boss is not None and boss.alive() and not boss.fase_meteoritos:
        distancia = Vector2(boss.rect.center).distance_to(centro)
        radio_boss = max(boss.rect.width, boss.rect.height) / 2

        if distancia <= radio + radio_boss:
            boss.recibir_dano(player2.dano_360_boss)
            pego = True

    if pego:
        sonido_hit.play()

    return puntos


def gameloop(screen, cantidad_jugadores=1):
    pygame.mixer.music.load("assets/background.ogg")
    pygame.mixer.music.set_volume(0.30)
    pygame.mixer.music.play(-1)

    sonido_powerup = pygame.mixer.Sound("assets/powerup.wav")
    sonido_damage = pygame.mixer.Sound("assets/damage.wav")
    sonido_hit = pygame.mixer.Sound("assets/hit.wav")

    sonido_powerup.set_volume(0.70)
    sonido_damage.set_volume(0.75)
    sonido_hit.set_volume(0.70)

    background_image = pygame.image.load("assets/background_n3.png").convert()
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    player = Player(screen)
    player2 = Player2(screen)

    dos_jugadores = cantidad_jugadores == 2

    crosshair = Crosshair()
    pygame.mouse.set_visible(False)

    enemies = pygame.sprite.Group()
    subdragones = pygame.sprite.Group()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    if dos_jugadores:
        all_sprites.add(player2)

    onda = OndaExpansiva()

    powerups = pygame.sprite.Group()

    proyectiles_enemigos = pygame.sprite.Group()
    proyectiles_boss = pygame.sprite.Group()
    meteoritos = pygame.sprite.Group()

    boss = None
    boss_group = pygame.sprite.Group()

    boss_aparecio = False

    victoria = False
    inicio_victoria = 0

    ADDENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDENEMY, 400)

    ADDPOWERUP = pygame.USEREVENT + 2
    pygame.time.set_timer(ADDPOWERUP, 8000)

    icono_flecha = pygame.image.load(customization.obtener_asset("bullet")).convert_alpha()
    icono_flecha = pygame.transform.scale(icono_flecha, (44, 16))

    icono_flecha_sombra = icono_flecha.copy()
    icono_flecha_sombra.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)

    icono_flecha_rapid = pygame.image.load("assets/bullet_rapid_fire.png").convert_alpha()
    icono_flecha_rapid = pygame.transform.scale(icono_flecha_rapid, (44, 16))

    icono_corazon = pygame.image.load("assets/heart.png").convert_alpha()
    icono_corazon = pygame.transform.scale(icono_corazon, (34, 34))

    icono_corazon_shield = pygame.image.load("assets/heart_shield.png").convert_alpha()
    icono_corazon_shield = pygame.transform.scale(icono_corazon_shield, (34, 34))

    font_puntos = pygame.font.Font(None, 45)
    font_boss = pygame.font.Font(None, 34)
    font_fase = pygame.font.Font(None, 26)
    font_aviso = pygame.font.Font(None, 50)
    font_victoria = pygame.font.Font(None, 85)
    font_habilidad = pygame.font.Font(None, 20)
    font_pausa = pygame.font.Font(None, 75)
    font_boton = pygame.font.Font(None, 35)

    estelas_dash = []
    duracion_estela = 300

    estadistica = 0
    ultimo_segundo = pygame.time.get_ticks()

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

    clock = pygame.time.Clock()

    while True:
        screen.blit(background_image, (0, 0))

        # ==================================================
        # EVENTOS
        # ==================================================

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)
                return "quit"

            # PAUSA
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

                        background_image = pygame.image.load("assets/background_n3.png").convert()
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
                    player2.ultimo_360 += tiempo_pausa

                    if player2.inmortal_hasta > inicio_pausa:
                        player2.inmortal_hasta += tiempo_pausa

                    if player2.mostrando_360:
                        player2.inicio_efecto_360 += tiempo_pausa
                        player2.fin_efecto_360 += tiempo_pausa

                    if player2.furia:
                        player2.fin_furia += tiempo_pausa

                    if boss is not None and boss.alive():
                        boss.ajustar_pausa(tiempo_pausa)

                    for i in range(len(estelas_dash)):
                        inicio, fin, tiempo_inicio = estelas_dash[i]
                        estelas_dash[i] = (inicio, fin, tiempo_inicio + tiempo_pausa)

                    pausado = False
                    pygame.mixer.music.unpause()
                    pygame.mouse.set_visible(False)

                continue

            # TECLAS
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pausado = True
                    inicio_pausa = pygame.time.get_ticks()

                    pygame.mixer.music.pause()
                    pygame.mouse.set_visible(True)

                # Jorge dash
                if event.key == K_SPACE and not player.caido:
                    resultado = player.dash(pygame.key.get_pressed())

                    if resultado is not None:
                        inicio, fin = resultado
                        estelas_dash.append((inicio, fin, pygame.time.get_ticks()))

                # Player 2 dash
                if event.key == K_RSHIFT and dos_jugadores and not player2.caido:
                    resultado = player2.embestida(pygame.key.get_pressed())

                    if resultado is not None:
                        inicio, fin = resultado
                        estelas_dash.append((inicio, fin, pygame.time.get_ticks()))

                        golpeados = set()

                        # revisar todo el trayecto del dash
                        for paso in range(11):
                            x = inicio[0] + (fin[0] - inicio[0]) * paso / 10
                            y = inicio[1] + (fin[1] - inicio[1]) * paso / 10

                            player2.rect.center = (x, y)

                            for enemigo in pygame.sprite.spritecollide(player2, subdragones, False):
                                golpeados.add(enemigo)

                            if not boss_aparecio:
                                for enemigo in pygame.sprite.spritecollide(player2, enemies, False):
                                    golpeados.add(enemigo)

                        player2.rect.center = fin

                        pego = False

                        for enemigo in golpeados:
                            if enemigo.alive():
                                murio = enemigo.recibir_dano(player2.dano_embestida)
                                pego = True

                                if murio:
                                    if enemigo in subdragones:
                                        estadistica += 8
                                    else:
                                        estadistica += 5

                        # revisar si el dash atraviesa al boss
                        if boss is not None and boss.alive() and not boss.fase_meteoritos:
                            for paso in range(11):
                                x = inicio[0] + (fin[0] - inicio[0]) * paso / 10
                                y = inicio[1] + (fin[1] - inicio[1]) * paso / 10

                                player2.rect.center = (x, y)

                                if player2.rect.colliderect(boss.rect):
                                    boss.recibir_dano(player2.dano_embestida_boss)
                                    pego = True
                                    break

                            player2.rect.center = fin

                        if pego:
                            sonido_hit.play()

                # Player 2 360
                if event.key == K_RETURN and dos_jugadores and not player2.caido:
                    ataque = player2.usar_360()

                    if ataque is not None:
                        centro, radio = ataque

                        estadistica += ataque_360(
                            player2,
                            enemies,
                            subdragones,
                            boss,
                            boss_aparecio,
                            proyectiles_boss,
                            meteoritos,
                            centro,
                            radio,
                            sonido_hit
                        )

            # ENEMIGOS ANTES DEL BOSS
            elif event.type == ADDENEMY and not boss_aparecio:
                tipo = random.choices(["normal", "S", "G", "M", "D"], weights=[45, 25, 14, 10, 6], k=1)[0]

                enemigo = EnemyLevel2(screen, tipo)

                enemies.add(enemigo)
                all_sprites.add(enemigo)

            elif event.type == ADDPOWERUP:
                if len(powerups) == 0:
                    powerups.add(PowerUp(screen))

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and not player.caido:
                    player.shoot(pygame.mouse.get_pos())

        # ==================================================
        # UPDATE
        # ==================================================

        if not pausado and not victoria:
            if player.rapid_fire and pygame.mouse.get_pressed()[0] and not player.caido:
                player.shoot(pygame.mouse.get_pos())

            pressed_keys = pygame.key.get_pressed()

            if not player.caido:
                player.update(pressed_keys)

            else:
                player.bullets.update()

            if dos_jugadores and not player2.caido:
                player2.update(pressed_keys)

            objetivos = []

            if not player.caido:
                objetivos.append(player.rect.center)

            if dos_jugadores and not player2.caido:
                objetivos.append(player2.rect.center)

            if not boss_aparecio:
                enemies.update(player.rect.center, proyectiles_enemigos)

            subdragones.update(objetivos)

            proyectiles_enemigos.update()
            proyectiles_boss.update()
            meteoritos.update()

            powerups.update()
            crosshair.update()

            if boss is not None and boss.alive():
                boss.update(objetivos, proyectiles_boss, meteoritos, subdragones)

            # onda cooperativa
            cargando = dos_jugadores and not player.caido and not player2.caido and pressed_keys[K_SPACE] and pressed_keys[K_RSHIFT]

            centro_onda = (
                (player.rect.centerx + player2.rect.centerx) // 2,
                (player.rect.centery + player2.rect.centery) // 2
            )

            if onda.update(cargando, centro_onda):
                estadistica += len(subdragones) * 8

                for enemigo in subdragones.sprites():
                    enemigo.kill()

                if boss is not None and boss.alive() and not boss.fase_meteoritos:
                    boss.recibir_dano(5)

                else:
                    estadistica += len(enemies) * 5

                    for enemigo in enemies.sprites():
                        enemigo.kill()

                    proyectiles_enemigos.empty()

            ahora = pygame.time.get_ticks()

            if ahora - ultimo_segundo >= 1000:
                estadistica += 1
                ultimo_segundo += 1000

            # aparece boss a 300 pts
            if estadistica >= 300 and not boss_aparecio:
                boss_aparecio = True

                pygame.time.set_timer(ADDENEMY, 0)

                for enemigo in enemies.sprites():
                    enemigo.kill()

                proyectiles_enemigos.empty()

                boss = Boss(screen)
                boss_group.add(boss)

        tiempo_visual = inicio_pausa if pausado else pygame.time.get_ticks()

        # ==================================================
        # ESTELA PLAYER DASH
        # ==================================================

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

        # ==================================================
        # DIBUJO
        # ==================================================

        for entity in all_sprites:
            screen.blit(entity.image, entity.rect)

        for dragon in subdragones:
            screen.blit(dragon.image, dragon.rect)

        for jefe in boss_group:
            screen.blit(jefe.image, jefe.rect)

        if dos_jugadores:
            player2.dibujar_360(screen)

        # revive
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

        for proyectil in proyectiles_enemigos:
            screen.blit(proyectil.image, proyectil.rect)

        for proyectil in proyectiles_boss:
            screen.blit(proyectil.image, proyectil.rect)

        for meteorito in meteoritos:
            screen.blit(meteorito.image, meteorito.rect)

        # ==================================================
        # HUD J1
        # ==================================================

        for i in range(player.vidas):
            x = 20 + i * 40
            icono = icono_corazon_shield if player.escudo else icono_corazon
            screen.blit(icono, (x, 20))

        texto_puntos = font_puntos.render(f"PUNTOS: {estadistica}", True, (255, 255, 255))
        sombra = font_puntos.render(f"PUNTOS: {estadistica}", True, (0, 0, 0))

        px = screen.get_width() - texto_puntos.get_width() - 20

        screen.blit(sombra, (px + 2, 22))
        screen.blit(texto_puntos, (px, 20))

        # ammo
        for i in range(player.max_disparos):
            x = 20 + i * (icono_flecha.get_width() + 8)

            if player.rapid_fire:
                icono = icono_flecha_rapid

            elif i >= player.max_disparos - player.disparos:
                icono = icono_flecha_sombra

            else:
                icono = icono_flecha

            screen.blit(icono, (x, 62))

        # dash Jorge
        progreso_dash_j1 = min(1, (tiempo_visual - player.ultimo_dash) / player.cooldown_dash)

        pygame.draw.rect(screen, (30, 30, 35), (20, 90, 200, 9), border_radius=4)
        pygame.draw.rect(screen, (255, 200, 40), (20, 90, int(200 * progreso_dash_j1), 9), border_radius=4)

        # ==================================================
        # HUD PLAYER 2
        # ==================================================

        if dos_jugadores:
            for i in range(player2.vidas):
                x = screen.get_width() - 54 - i * 40
                icono = icono_corazon_shield if player2.escudo else icono_corazon
                screen.blit(icono, (x, 65))

            barra_x = screen.get_width() - 220

            progreso_dash = min(1, (tiempo_visual - player2.ultima_embestida) / player2.cooldown_embestida)
            progreso_360 = player2.progreso_360()

            screen.blit(font_habilidad.render("SHIFT", True, (220, 220, 220)), (barra_x - 48, 101))

            pygame.draw.rect(screen, (30, 30, 35), (barra_x, 105, 200, 8), border_radius=4)
            pygame.draw.rect(screen, (80, 180, 255), (barra_x, 105, int(200 * progreso_dash), 8), border_radius=4)

            screen.blit(font_habilidad.render("ENTER", True, (220, 220, 220)), (barra_x - 52, 118))

            pygame.draw.rect(screen, (30, 30, 35), (barra_x, 122, 200, 8), border_radius=4)
            pygame.draw.rect(screen, (120, 230, 255), (barra_x, 122, int(200 * progreso_360), 8), border_radius=4)

        # ==================================================
        # BOSS HUD
        # ==================================================

        if not boss_aparecio:
            faltan = max(0, 300 - estadistica)

            tiempo = pygame.time.get_ticks()

            if faltan <= 50:
                texto_alerta = f"PELIGRO: BOSS EN {faltan}"
                color = (255, 40, 40) if (tiempo // 250) % 2 == 0 else (120, 0, 0)
            else:
                texto_alerta = f"BOSS EN {faltan} PTS"
                color = (255, 180, 50)

            sombra = font_boss.render(texto_alerta, True, (20, 5, 5))
            screen.blit(sombra, sombra.get_rect(center=(screen.get_width() // 2 + 2, 102)))

            aviso = font_boss.render(texto_alerta, True, color)
            screen.blit(aviso, aviso.get_rect(center=(screen.get_width() // 2, 100)))

        if boss is not None and boss.alive():
            porcentaje = max(0, boss.vidas / boss.max_vidas)
            barra_x = screen.get_width() // 2 - 250

            pygame.draw.rect(screen, (30, 30, 35), (barra_x, 52, 500, 22), border_radius=6)
            pygame.draw.rect(screen, (210, 35, 35), (barra_x, 52, int(500 * porcentaje), 22), border_radius=6)
            pygame.draw.rect(screen, (255, 210, 90), (barra_x, 52, 500, 22), 3, border_radius=6)

            texto_boss = font_boss.render(f"DRAGON KING  {boss.vidas:g}/{boss.max_vidas:g}", True, (255, 255, 255))
            screen.blit(texto_boss, texto_boss.get_rect(center=(screen.get_width() // 2, 35)))

            texto_fase = font_fase.render(f"FASE {boss.fase_actual} / 5", True, (255, 190, 80))
            screen.blit(texto_fase, texto_fase.get_rect(center=(screen.get_width() // 2, 87)))

            # aviso del dash
            if boss.yendo_esquina_dash:
                aviso_dash = font_fase.render("EL DRAGON BUSCA UNA ESQUINA...", True, (255, 180, 70))
                screen.blit(aviso_dash, aviso_dash.get_rect(center=(screen.get_width() // 2, 115)))

            elif boss.preparando_embestida:
                aviso_dash = font_aviso.render("DASH!", True, (255, 70, 50))
                screen.blit(aviso_dash, aviso_dash.get_rect(center=(screen.get_width() // 2, 125)))

        if boss is not None and boss.alive() and boss.fase_meteoritos:
            aviso = font_aviso.render("SOBREVIVE", True, (255, 90, 50))
            screen.blit(aviso, aviso.get_rect(center=(screen.get_width() // 2, 120)))

        # ==================================================
        # COLISIONES
        # ==================================================

        if not pausado and not victoria:
            # PRIMERO las flechas destruyen ataques
            procesar_balas_peligros(player, proyectiles_boss, meteoritos, sonido_hit)

            # proyectiles normales a J1
            if not player.caido:
                impactos = pygame.sprite.spritecollide(player, proyectiles_enemigos, True)

                for proyectil in impactos:
                    if proyectil.tipo == "M":
                        player.aplicar_slow()

                    elif proyectil.tipo == "D":
                        hacer_dano(player, sonido_damage)

            # proyectiles normales a J2
            if dos_jugadores and not player2.caido:
                impactos = pygame.sprite.spritecollide(player2, proyectiles_enemigos, True)

                for proyectil in impactos:
                    if proyectil.tipo == "D":
                        hacer_dano(player2, sonido_damage)

            # balas boss a J1
            if not player.caido:
                impactos = pygame.sprite.spritecollide(player, proyectiles_boss, True)

                if impactos:
                    hacer_dano(player, sonido_damage)

            # balas boss a J2
            if dos_jugadores and not player2.caido:
                impactos = pygame.sprite.spritecollide(player2, proyectiles_boss, True)

                if impactos:
                    hacer_dano(player2, sonido_damage)

            # meteoritos J1
            if not player.caido:
                impactos = pygame.sprite.spritecollide(player, meteoritos, True)

                if impactos:
                    hacer_dano(player, sonido_damage)

            # meteoritos J2
            if dos_jugadores and not player2.caido:
                impactos = pygame.sprite.spritecollide(player2, meteoritos, True)

                if impactos:
                    hacer_dano(player2, sonido_damage)

            # subdragones J1
            if not player.caido:
                tocando = pygame.sprite.spritecollide(player, subdragones, True)

                if tocando:
                    hacer_dano(player, sonido_damage)

            # subdragones J2
            if dos_jugadores and not player2.caido:
                tocando = pygame.sprite.spritecollide(player2, subdragones, True)

                if tocando:
                    hacer_dano(player2, sonido_damage)

            # dragones normales antes boss
            if not boss_aparecio and not player.caido:
                tocando = pygame.sprite.spritecollide(player, enemies, False)

                if tocando:
                    tocando[0].kill()
                    hacer_dano(player, sonido_damage)

            if not boss_aparecio and dos_jugadores and not player2.caido:
                tocando = pygame.sprite.spritecollide(player2, enemies, False)

                if tocando:
                    tocando[0].kill()
                    hacer_dano(player2, sonido_damage)

            # ==================================================
            # DASH DEL BOSS
            # no se detiene al golpear, sigue hasta el borde
            # ==================================================

            if boss is not None and boss.alive() and boss.en_embestida:
                if not player.caido and player.rect.colliderect(boss.rect) and player not in boss.golpeados_embestida:
                    boss.golpeados_embestida.add(player)
                    hacer_dano(player, sonido_damage)

                if dos_jugadores and not player2.caido and player2.rect.colliderect(boss.rect) and player2 not in boss.golpeados_embestida:
                    boss.golpeados_embestida.add(player2)
                    hacer_dano(player2, sonido_damage)

            # powerups
            if not player.caido:
                for powerup in pygame.sprite.spritecollide(player, powerups, True):
                    sonido_powerup.play()
                    player.activar_powerup(powerup.tipo)

            if dos_jugadores and not player2.caido:
                for powerup in pygame.sprite.spritecollide(player2, powerups, True):
                    sonido_powerup.play()
                    player2.activar_powerup(powerup.tipo)

            # revive
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

            # flechas enemigos pre boss
            if not boss_aparecio:
                estadistica += procesar_balas_grupo(player, enemies, sonido_hit, 5)

            # flechas subdragones
            estadistica += procesar_balas_grupo(player, subdragones, sonido_hit, 8)

            # flechas boss
            procesar_balas_boss(player, boss, sonido_hit)

            # GAME OVER
            todos_caidos = player.caido and player2.caido if dos_jugadores else player.caido

            if todos_caidos:
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)

                return ("dead", estadistica)

            # BOSS MUERTO
            if boss_aparecio and boss is not None and not boss.alive() and not victoria:
                victoria = True
                inicio_victoria = pygame.time.get_ticks()

                proyectiles_boss.empty()
                proyectiles_enemigos.empty()
                meteoritos.empty()
                subdragones.empty()

                estadistica += 300

            screen.blit(crosshair.image, crosshair.rect)

        # ==================================================
        # VICTORIA
        # ==================================================

        if victoria:
            overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))

            screen.blit(overlay, (0, 0))

            texto = font_victoria.render("BOSS DERROTADO", True, (255, 215, 80))
            screen.blit(texto, texto.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2)))

            if pygame.time.get_ticks() - inicio_victoria >= 2500:
                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)

                return ("victory", estadistica)

        # ==================================================
        # PAUSA
        # ==================================================

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
                (boton_salir, "SALIR")
            ]

            for boton, texto in botones:
                color = (255, 205, 60) if boton.collidepoint(mouse) else (40, 45, 55)

                pygame.draw.rect(screen, color, boton, border_radius=10)
                pygame.draw.rect(screen, (255, 215, 80), boton, 3, border_radius=10)

                render = font_boton.render(texto, True, (255, 255, 255))
                screen.blit(render, render.get_rect(center=boton.center))

        pygame.display.flip()
        clock.tick(60)