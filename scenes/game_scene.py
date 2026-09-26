if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame

from pygame.locals import (
    K_ESCAPE,
    K_SPACE,
    K_RETURN,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    QUIT,
    K_RSHIFT
)

from pygame.math import Vector2

import customization

from elements import (
    Crosshair,
    Enemy,
    Player,
    PowerUp,
    Player2,
    OndaExpansiva
)


def cambiar_modo_pantalla(pantalla_completa):

    if pantalla_completa:
        return pygame.display.set_mode(
            (1024, 768),
            pygame.FULLSCREEN
        )

    return pygame.display.set_mode(
        (1024, 768)
    )


def hacer_dano(jugador, sonido):

    # el Player2 tiene invulnerabilidad durante dash / 360
    if hasattr(jugador, "es_inmortal") and jugador.es_inmortal():
        return

    if jugador.escudo:

        jugador.escudo = False
        jugador.actualizar_apariencia()

    else:

        sonido.play()

        if jugador.recibir_dano():
            jugador.caer()


def procesar_balas(player, enemies, sonido_hit):

    puntos = 0

    for bala in player.bullets.sprites():

        golpeados = pygame.sprite.spritecollide(
            bala,
            enemies,
            False
        )

        for enemigo in golpeados:

            if enemigo in bala.enemigos_golpeados:
                continue

            bala.enemigos_golpeados.add(enemigo)

            enemigo.kill()

            puntos += 5

            sonido_hit.play()

            bala.kill()

            if not bala.alive():
                break

    return puntos


def gameloop(screen, cantidad_jugadores=1):

    pygame.mixer.music.load(
        "assets/background.ogg"
    )

    pygame.mixer.music.set_volume(0.30)
    pygame.mixer.music.play(-1)

    sonido_powerup = pygame.mixer.Sound(
        "assets/powerup.wav"
    )

    sonido_damage = pygame.mixer.Sound(
        "assets/damage.wav"
    )

    sonido_hit = pygame.mixer.Sound(
        "assets/hit.wav"
    )

    sonido_powerup.set_volume(0.70)
    sonido_damage.set_volume(0.75)
    sonido_hit.set_volume(0.70)

    background_image = pygame.image.load(
        customization.obtener_asset("background")
    ).convert()

    background_image = pygame.transform.scale(
        background_image,
        (
            screen.get_width(),
            screen.get_height()
        )
    )

    player = Player(screen)

    crosshair = Crosshair()

    pygame.mouse.set_visible(False)

    enemies = pygame.sprite.Group()

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

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

    icono_flecha = pygame.image.load(
        customization.obtener_asset("bullet")
    ).convert_alpha()

    icono_flecha = pygame.transform.scale(
        icono_flecha,
        (44, 16)
    )

    icono_flecha_sombra = icono_flecha.copy()

    icono_flecha_sombra.fill(
        (0, 0, 0, 255),
        special_flags=pygame.BLEND_RGBA_MULT
    )

    icono_flecha_rapid = pygame.image.load(
        "assets/bullet_rapid_fire.png"
    ).convert_alpha()

    icono_flecha_rapid = pygame.transform.scale(
        icono_flecha_rapid,
        (44, 16)
    )

    icono_corazon = pygame.image.load(
        "assets/heart.png"
    ).convert_alpha()

    icono_corazon = pygame.transform.scale(
        icono_corazon,
        (34, 34)
    )

    icono_corazon_shield = pygame.image.load(
        "assets/heart_shield.png"
    ).convert_alpha()

    icono_corazon_shield = pygame.transform.scale(
        icono_corazon_shield,
        (34, 34)
    )

    estelas_dash = []
    duracion_estela = 300

    pausado = False
    inicio_pausa = 0

    pantalla_completa = bool(
        pygame.display.get_surface().get_flags()
        & pygame.FULLSCREEN
    )

    boton_reanudar = pygame.Rect(
        0, 0, 320, 60
    )

    boton_inicio = pygame.Rect(
        0, 0, 320, 60
    )

    boton_pantalla = pygame.Rect(
        0, 0, 320, 60
    )

    boton_salir = pygame.Rect(
        0, 0, 320, 60
    )

    boton_reanudar.center = (
        screen.get_width() // 2,
        335
    )

    boton_inicio.center = (
        screen.get_width() // 2,
        410
    )

    boton_pantalla.center = (
        screen.get_width() // 2,
        485
    )

    boton_salir.center = (
        screen.get_width() // 2,
        560
    )

    font_pausa = pygame.font.Font(
        None,
        75
    )

    font_boton = pygame.font.Font(
        None,
        35
    )

    font_puntos = pygame.font.Font(
        None,
        45
    )

    font_habilidad = pygame.font.Font(
        None,
        20
    )

    estadistica = 0

    ultimo_segundo = pygame.time.get_ticks()

    clock = pygame.time.Clock()

    recibio_dano = False
    escudos_recogidos = 0
    uso_rapid_fire = False
    balas_disparadas = 0

    while True:

        screen.blit(
            background_image,
            (0, 0)
        )

        for event in pygame.event.get():

            if event.type == QUIT:

                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)

                return "quit"

            # ===========================
            # PAUSA
            # ===========================

            if pausado:

                reanudar = False

                if (
                    event.type == KEYDOWN
                    and event.key == K_ESCAPE
                ):
                    reanudar = True

                if (
                    event.type == MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    if boton_reanudar.collidepoint(
                        event.pos
                    ):
                        reanudar = True

                    elif boton_inicio.collidepoint(
                        event.pos
                    ):

                        pygame.mixer.music.stop()
                        pygame.mouse.set_visible(True)

                        return "menu"

                    elif boton_pantalla.collidepoint(
                        event.pos
                    ):

                        pantalla_completa = not pantalla_completa

                        screen = cambiar_modo_pantalla(
                            pantalla_completa
                        )

                        background_image = pygame.image.load(
                            customization.obtener_asset(
                                "background"
                            )
                        ).convert()

                        background_image = pygame.transform.scale(
                            background_image,
                            (
                                screen.get_width(),
                                screen.get_height()
                            )
                        )

                    elif boton_salir.collidepoint(
                        event.pos
                    ):

                        pygame.mixer.music.stop()
                        pygame.mouse.set_visible(True)

                        return "quit"

                if reanudar:

                    tiempo_pausa = (
                        pygame.time.get_ticks()
                        - inicio_pausa
                    )

                    ultimo_segundo += tiempo_pausa

                    if player.sobrecalentado:
                        player.inicio_sobrecalentamiento += tiempo_pausa

                    if player.rapid_fire:
                        player.fin_rapid_fire += tiempo_pausa

                    player.ultimo_dash += tiempo_pausa

                    player2.ultima_embestida += tiempo_pausa
                    player2.ultimo_360 += tiempo_pausa

                    # si estaba invulnerable al entrar a pausa,
                    # se conserva ese tiempo
                    if player2.inmortal_hasta > inicio_pausa:
                        player2.inmortal_hasta += tiempo_pausa

                    if player2.mostrando_360:

                        player2.inicio_efecto_360 += tiempo_pausa
                        player2.fin_efecto_360 += tiempo_pausa

                    if player2.furia:
                        player2.fin_furia += tiempo_pausa

                    for i in range(
                        len(estelas_dash)
                    ):

                        inicio, fin, tiempo_inicio = estelas_dash[i]

                        estelas_dash[i] = (
                            inicio,
                            fin,
                            tiempo_inicio + tiempo_pausa
                        )

                    pausado = False

                    pygame.mixer.music.unpause()
                    pygame.mouse.set_visible(False)

                continue

            # ===========================
            # TECLAS
            # ===========================

            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:

                    pausado = True
                    inicio_pausa = pygame.time.get_ticks()

                    pygame.mixer.music.pause()
                    pygame.mouse.set_visible(True)

                # dash Jorge
                if (
                    event.key == K_SPACE
                    and not player.caido
                ):

                    resultado = player.dash(
                        pygame.key.get_pressed()
                    )

                    if resultado is not None:

                        inicio, fin = resultado

                        estelas_dash.append(
                            (
                                inicio,
                                fin,
                                pygame.time.get_ticks()
                            )
                        )

                # dash Player 2
                if (
                    event.key == K_RSHIFT
                    and dos_jugadores
                    and not player2.caido
                ):

                    resultado = player2.embestida(
                        pygame.key.get_pressed()
                    )

                    if resultado is not None:

                        inicio, fin = resultado

                        estelas_dash.append(
                            (
                                inicio,
                                fin,
                                pygame.time.get_ticks()
                            )
                        )

                        golpeados = set()

                        for paso in range(11):

                            x = (
                                inicio[0]
                                + (fin[0] - inicio[0])
                                * paso / 10
                            )

                            y = (
                                inicio[1]
                                + (fin[1] - inicio[1])
                                * paso / 10
                            )

                            player2.rect.center = (
                                x,
                                y
                            )

                            enemigos_dash = pygame.sprite.spritecollide(
                                player2,
                                enemies,
                                False
                            )

                            for enemigo in enemigos_dash:
                                golpeados.add(enemigo)

                        player2.rect.center = fin

                        for enemigo in golpeados:

                            if enemigo.alive():

                                enemigo.kill()
                                estadistica += 5

                        if golpeados:
                            sonido_hit.play()

                # ENTER = ataque 360
                if (
                    event.key == K_RETURN
                    and dos_jugadores
                    and not player2.caido
                ):

                    ataque = player2.usar_360()

                    if ataque is not None:

                        centro, radio = ataque

                        matados = 0

                        for enemigo in enemies.sprites():

                            distancia = Vector2(
                                enemigo.rect.center
                            ).distance_to(
                                centro
                            )

                            radio_enemigo = (
                                max(
                                    enemigo.rect.width,
                                    enemigo.rect.height
                                )
                                / 2
                            )

                            if (
                                distancia
                                <= radio + radio_enemigo
                            ):

                                enemigo.kill()

                                matados += 1

                        if matados > 0:

                            estadistica += (
                                matados * 5
                            )

                            sonido_hit.play()

            # ===========================
            # ENEMIGOS
            # ===========================

            elif event.type == ADDENEMY:

                enemigo = Enemy(screen)

                enemies.add(enemigo)
                all_sprites.add(enemigo)

            elif event.type == ADDPOWERUP:

                if len(powerups) == 0:

                    powerups.add(
                        PowerUp(screen)
                    )

            elif event.type == MOUSEBUTTONDOWN:

                if (
                    event.button == 1
                    and not player.caido
                ):

                    player.shoot(
                        pygame.mouse.get_pos()
                    )
                balas_disparadas += 1

        # ===============================
        # UPDATE
        # ===============================

        if not pausado:

            if (
                player.rapid_fire
                and pygame.mouse.get_pressed()[0]
                and not player.caido
            ):

                player.shoot(
                    pygame.mouse.get_pos()
                )

            pressed_keys = pygame.key.get_pressed()

            if not player.caido:
                player.update(pressed_keys)

            else:
                player.bullets.update()

            if (
                dos_jugadores
                and not player2.caido
            ):
                player2.update(pressed_keys)

            enemies.update()
            powerups.update()
            crosshair.update()

            cargando = (
                dos_jugadores
                and not player.caido
                and not player2.caido
                and pressed_keys[K_SPACE]
                and pressed_keys[K_RSHIFT]
            )

            centro_onda = (
                (
                    player.rect.centerx
                    + player2.rect.centerx
                ) // 2,
                (
                    player.rect.centery
                    + player2.rect.centery
                ) // 2
            )

            if onda.update(
                cargando,
                centro_onda
            ):

                estadistica += (
                    len(enemies) * 5
                )

                for enemigo in enemies.sprites():
                    enemigo.kill()

            ahora = pygame.time.get_ticks()

            if ahora - ultimo_segundo >= 1000:

                estadistica += 1
                ultimo_segundo += 1000

        if pausado:
            tiempo_visual = inicio_pausa

        else:
            tiempo_visual = pygame.time.get_ticks()

        # ===============================
        # ESTELA DASH
        # ===============================

        for estela in estelas_dash[:]:

            inicio, fin, tiempo_inicio = estela

            tiempo_pasado = (
                tiempo_visual - tiempo_inicio
            )

            if tiempo_pasado >= duracion_estela:

                if not pausado:
                    estelas_dash.remove(estela)

                continue

            transparencia = int(
                200
                * (
                    1
                    - tiempo_pasado
                    / duracion_estela
                )
            )

            superficie_estela = pygame.Surface(
                (
                    screen.get_width(),
                    screen.get_height()
                ),
                pygame.SRCALPHA
            )

            pygame.draw.line(
                superficie_estela,
                (
                    255,
                    180,
                    0,
                    transparencia
                ),
                inicio,
                fin,
                30
            )

            pygame.draw.line(
                superficie_estela,
                (
                    255,
                    245,
                    120,
                    transparencia
                ),
                inicio,
                fin,
                9
            )

            screen.blit(
                superficie_estela,
                (0, 0)
            )

        # ===============================
        # DIBUJO
        # ===============================

        for entity in all_sprites:

            screen.blit(
                entity.image,
                entity.rect
            )

        if dos_jugadores:
            player2.dibujar_360(screen)

        # revive
        if dos_jugadores:

            for jugador in [
                player,
                player2
            ]:

                if jugador.caido:

                    progreso = (
                        jugador.progreso_revivir
                        / 300
                    )

                    barra_x = (
                        jugador.rect.centerx - 40
                    )

                    barra_y = (
                        jugador.rect.top - 14
                    )

                    pygame.draw.rect(
                        screen,
                        (30, 30, 35),
                        (
                            barra_x,
                            barra_y,
                            80,
                            8
                        ),
                        border_radius=4
                    )

                    pygame.draw.rect(
                        screen,
                        (90, 230, 120),
                        (
                            barra_x,
                            barra_y,
                            int(80 * progreso),
                            8
                        ),
                        border_radius=4
                    )

        for powerup in powerups:

            screen.blit(
                powerup.image,
                powerup.rect
            )

        if onda.animacion > 0:

            screen.blit(
                onda.image,
                onda.rect
            )

        for bullet in player.bullets:

            screen.blit(
                bullet.image,
                bullet.rect
            )

        if player.vidas < player.max_vidas:
            recibio_dano = True

        # VIDA J1
        for i in range(player.vidas):

            x = 20 + i * 40

            if player.escudo:
                escudos_recogidos += 1
                icono = icono_corazon_shield

            else:
                icono = icono_corazon

            screen.blit(
                icono,
                (x, 20)
            )

        # puntos
        sombra_puntos = font_puntos.render(
            f"PUNTOS: {estadistica}",
            True,
            (0, 0, 0)
        )

        texto_puntos = font_puntos.render(
            f"PUNTOS: {estadistica}",
            True,
            (255, 255, 255)
        )

        pos_x = (
            screen.get_width()
            - texto_puntos.get_width()
            - 20
        )

        screen.blit(
            sombra_puntos,
            (pos_x + 2, 22)
        )

        screen.blit(
            texto_puntos,
            (pos_x, 20)
        )

        # MUNICION
        for i in range(
            player.max_disparos
        ):

            x = (
                20
                + i
                * (
                    icono_flecha.get_width()
                    + 8
                )
            )

            if player.rapid_fire:
                uso_rapid_fire = True
                icono = icono_flecha_rapid

            elif (
                i
                >= player.max_disparos
                - player.disparos
            ):
                icono = icono_flecha_sombra

            else:
                icono = icono_flecha

            screen.blit(
                icono,
                (x, 62)
            )

        # barra dash J1
        progreso_dash = min(
            1,
            (
                tiempo_visual
                - player.ultimo_dash
            )
            / player.cooldown_dash
        )

        pygame.draw.rect(
            screen,
            (30, 30, 35),
            (20, 90, 200, 9),
            border_radius=4
        )

        pygame.draw.rect(
            screen,
            (255, 200, 40),
            (
                20,
                90,
                int(200 * progreso_dash),
                9
            ),
            border_radius=4
        )

        # ===============================
        # HUD PLAYER 2
        # ===============================

        if dos_jugadores:

            if player2.vidas < player2.max_vidas:
                recibio_dano = True
            
            for i in range(player2.vidas):

                x = (
                    screen.get_width()
                    - 54
                    - i * 40
                )

                if player2.escudo:
                    escudos_recogidos += 1
                    icono = icono_corazon_shield

                else:
                    icono = icono_corazon

                screen.blit(
                    icono,
                    (x, 65)
                )

            barra_x = (
                screen.get_width() - 220
            )

            progreso_dash2 = min(
                1,
                (
                    tiempo_visual
                    - player2.ultima_embestida
                )
                / player2.cooldown_embestida
            )

            color_dash = (
                (255, 120, 40)
                if player2.furia
                else (80, 180, 255)
            )

            screen.blit(
                font_habilidad.render(
                    "SHIFT",
                    True,
                    (220, 220, 220)
                ),
                (
                    barra_x - 48,
                    101
                )
            )

            pygame.draw.rect(
                screen,
                (30, 30, 35),
                (
                    barra_x,
                    105,
                    200,
                    8
                ),
                border_radius=4
            )

            pygame.draw.rect(
                screen,
                color_dash,
                (
                    barra_x,
                    105,
                    int(
                        200
                        * progreso_dash2
                    ),
                    8
                ),
                border_radius=4
            )

            progreso_360 = (
                player2.progreso_360()
            )

            color_360 = (
                (255, 120, 40)
                if player2.furia
                else (120, 230, 255)
            )

            screen.blit(
                font_habilidad.render(
                    "ENTER",
                    True,
                    (220, 220, 220)
                ),
                (
                    barra_x - 52,
                    118
                )
            )

            pygame.draw.rect(
                screen,
                (30, 30, 35),
                (
                    barra_x,
                    122,
                    200,
                    8
                ),
                border_radius=4
            )

            pygame.draw.rect(
                screen,
                color_360,
                (
                    barra_x,
                    122,
                    int(
                        200
                        * progreso_360
                    ),
                    8
                ),
                border_radius=4
            )

        # ===============================
        # COLISIONES
        # ===============================

        if not pausado:

            # powers Jorge
            if not player.caido:

                recogidos = pygame.sprite.spritecollide(
                    player,
                    powerups,
                    True
                )

                for powerup in recogidos:

                    sonido_powerup.play()

                    player.activar_powerup(
                        powerup.tipo
                    )

            # powers P2
            if (
                dos_jugadores
                and not player2.caido
            ):

                recogidos = pygame.sprite.spritecollide(
                    player2,
                    powerups,
                    True
                )

                for powerup in recogidos:

                    sonido_powerup.play()

                    player2.activar_powerup(
                        powerup.tipo
                    )

            # enemigo toca Jorge
            if not player.caido:

                tocando = pygame.sprite.spritecollide(
                    player,
                    enemies,
                    False
                )

                if tocando:

                    tocando[0].kill()

                    hacer_dano(
                        player,
                        sonido_damage
                    )

            # enemigo toca P2
            if (
                dos_jugadores
                and not player2.caido
            ):

                tocando = pygame.sprite.spritecollide(
                    player2,
                    enemies,
                    False
                )

                if tocando:

                    # aunque sea inmortal igual el enemigo muere
                    tocando[0].kill()

                    hacer_dano(
                        player2,
                        sonido_damage
                    )

            # revive
            if dos_jugadores:

                for jugador_caido, rescatista in [
                    (player, player2),
                    (player2, player)
                ]:

                    if (
                        jugador_caido.caido
                        and not rescatista.caido
                    ):

                        distancia = (
                            Vector2(
                                jugador_caido.rect.center
                            )
                            - Vector2(
                                rescatista.rect.center
                            )
                        ).length()

                        if distancia < 110:

                            jugador_caido.progreso_revivir += 1

                        else:

                            jugador_caido.progreso_revivir = 0

                        if (
                            jugador_caido.progreso_revivir
                            >= 300
                        ):

                            jugador_caido.revivir()
                            sonido_powerup.play()

            if dos_jugadores:
                todos_caidos = (
                    player.caido
                    and player2.caido
                )

            else:
                todos_caidos = player.caido

            if todos_caidos:

                pygame.mixer.music.stop()
                pygame.mouse.set_visible(True)

                return (
                    "dead", estadistica, recibio_dano, escudos_recogidos, uso_rapid_fire, balas_disparadas
                )

            estadistica += procesar_balas(
                player,
                enemies,
                sonido_hit
            )

            screen.blit(
                crosshair.image,
                crosshair.rect
            )

        # ===============================
        # MENU PAUSA
        # ===============================

        if pausado:

            overlay = pygame.Surface(
                (
                    screen.get_width(),
                    screen.get_height()
                ),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 180)
            )

            screen.blit(
                overlay,
                (0, 0)
            )

            titulo = font_pausa.render(
                "PAUSA",
                True,
                (255, 215, 80)
            )

            screen.blit(
                titulo,
                titulo.get_rect(
                    center=(
                        screen.get_width()
                        // 2,
                        230
                    )
                )
            )

            if pantalla_completa:
                texto_pantalla = "MODO VENTANA"

            else:
                texto_pantalla = "PANTALLA COMPLETA"

            mouse = pygame.mouse.get_pos()

            botones = [
                (
                    boton_reanudar,
                    "REANUDAR"
                ),
                (
                    boton_inicio,
                    "VOLVER AL INICIO"
                ),
                (
                    boton_pantalla,
                    texto_pantalla
                ),
                (
                    boton_salir,
                    "SALIR"
                )
            ]

            for boton, texto in botones:

                if boton.collidepoint(mouse):
                    color = (255, 205, 60)

                else:
                    color = (40, 45, 55)

                pygame.draw.rect(
                    screen,
                    color,
                    boton,
                    border_radius=10
                )

                pygame.draw.rect(
                    screen,
                    (255, 215, 80),
                    boton,
                    3,
                    border_radius=10
                )

                render = font_boton.render(
                    texto,
                    True,
                    (255, 255, 255)
                )

                screen.blit(
                    render,
                    render.get_rect(
                        center=boton.center
                    )
                )

        pygame.display.flip()

        clock.tick(60)