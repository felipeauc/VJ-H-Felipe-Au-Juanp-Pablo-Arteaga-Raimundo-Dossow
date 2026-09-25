if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random

import pygame

from pygame.locals import (
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    MOUSEBUTTONDOWN,
    QUIT,
    K_RSHIFT,
)

from pygame.math import Vector2

import customization

from elements import (
    Crosshair,
    EnemyLevel2,
    Player,
    PowerUp,
    Player2,
    OndaExpansiva,
    Boss,
)


# para que una flecha no haga daño cada frame al mismo bicho
def colision_bala_enemigo(bala, enemigo):

    if enemigo in bala.enemigos_golpeados:
        return False


    if bala.rect.colliderect(enemigo.rect):

        bala.enemigos_golpeados.add(
            enemigo
        )

        return True


    return False


def cambiar_modo_pantalla(pantalla_completa):

    if pantalla_completa:

        screen = pygame.display.set_mode(
            (1024, 768),
            pygame.FULLSCREEN
        )

    else:

        screen = pygame.display.set_mode(
            (1024, 768)
        )


    return screen


# para no repetir shield/daño 40 veces
def hacer_dano(jugador, sonido_damage):

    if jugador.escudo:

        jugador.escudo = False

        jugador.actualizar_apariencia()


    else:

        sonido_damage.play()

        murio = jugador.recibir_dano()


        if murio:
            jugador.caer()


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


    # fondo castillo / boss
    background_image = pygame.image.load(
        "assets/background_n3.png"
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


    proyectiles_enemigos = pygame.sprite.Group()


    # cosas boss
    boss = None

    boss_group = pygame.sprite.Group()

    proyectiles_boss = pygame.sprite.Group()

    meteoritos = pygame.sprite.Group()


    boss_aparecio = False

    victoria = False

    inicio_victoria = 0


    powerups = pygame.sprite.Group()


    ADDENEMY = pygame.USEREVENT + 1

    pygame.time.set_timer(
        ADDENEMY,
        400
    )


    ADDPOWERUP = pygame.USEREVENT + 2

    pygame.time.set_timer(
        ADDPOWERUP,
        8000
    )


    # HUD municion
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


    # pausa
    pausado = False

    inicio_pausa = 0


    pantalla_completa = bool(
        pygame.display.get_surface().get_flags()
        & pygame.FULLSCREEN
    )


    boton_reanudar = pygame.Rect(
        0,
        0,
        320,
        60
    )

    boton_inicio = pygame.Rect(
        0,
        0,
        320,
        60
    )

    boton_pantalla = pygame.Rect(
        0,
        0,
        320,
        60
    )

    boton_salir = pygame.Rect(
        0,
        0,
        320,
        60
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


    estadistica = 0

    ultimo_segundo = pygame.time.get_ticks()


    font_puntos = pygame.font.Font(
        None,
        45
    )

    font_boss = pygame.font.Font(
        None,
        34
    )

    font_aviso = pygame.font.Font(
        None,
        50
    )

    font_victoria = pygame.font.Font(
        None,
        85
    )


    clock = pygame.time.Clock()

    running = True


    while running:

        screen.blit(
            background_image,
            (0, 0)
        )


        # ==================== EVENTOS ====================
        for event in pygame.event.get():

            if event.type == QUIT:

                pygame.mixer.music.stop()

                pygame.mouse.set_visible(True)

                return "quit"


            if pausado:

                if (
                    event.type == KEYDOWN
                    and event.key == K_ESCAPE
                ):

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


                    if player2.furia:
                        player2.fin_furia += tiempo_pausa


                    if boss is not None and boss.alive():

                        boss.ultimo_ataque += tiempo_pausa


                        if boss.fase_meteoritos:

                            boss.inicio_fase_meteoritos += tiempo_pausa

                            boss.ultimo_meteorito += tiempo_pausa


                    for i in range(len(estelas_dash)):

                        inicio, fin, tiempo_inicio = estelas_dash[i]

                        estelas_dash[i] = (
                            inicio,
                            fin,
                            tiempo_inicio + tiempo_pausa
                        )


                    pausado = False

                    pygame.mixer.music.unpause()

                    pygame.mouse.set_visible(False)


                if (
                    event.type == MOUSEBUTTONDOWN
                    and event.button == 1
                ):

                    if boton_reanudar.collidepoint(event.pos):

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


                        if player2.furia:
                            player2.fin_furia += tiempo_pausa


                        if boss is not None and boss.alive():

                            boss.ultimo_ataque += tiempo_pausa


                            if boss.fase_meteoritos:

                                boss.inicio_fase_meteoritos += tiempo_pausa

                                boss.ultimo_meteorito += tiempo_pausa


                        for i in range(len(estelas_dash)):

                            inicio, fin, tiempo_inicio = estelas_dash[i]

                            estelas_dash[i] = (
                                inicio,
                                fin,
                                tiempo_inicio + tiempo_pausa
                            )


                        pausado = False

                        pygame.mixer.music.unpause()

                        pygame.mouse.set_visible(False)


                    elif boton_inicio.collidepoint(event.pos):

                        pygame.mixer.music.stop()

                        pygame.mouse.set_visible(True)

                        return "menu"


                    elif boton_pantalla.collidepoint(event.pos):

                        pantalla_completa = not pantalla_completa

                        screen = cambiar_modo_pantalla(
                            pantalla_completa
                        )


                        background_image = pygame.image.load(
                            "assets/background_n3.png"
                        ).convert()


                        background_image = pygame.transform.scale(
                            background_image,
                            (
                                screen.get_width(),
                                screen.get_height()
                            )
                        )


                    elif boton_salir.collidepoint(event.pos):

                        pygame.mixer.music.stop()

                        pygame.mouse.set_visible(True)

                        return "quit"


                continue


            if event.type == KEYDOWN:

                if event.key == K_ESCAPE:

                    pausado = True

                    inicio_pausa = pygame.time.get_ticks()

                    pygame.mixer.music.pause()

                    pygame.mouse.set_visible(True)


                # dash jorge
                if (
                    event.key == K_SPACE
                    and not player.caido
                ):

                    resultado_dash = player.dash(
                        pygame.key.get_pressed()
                    )


                    if resultado_dash is not None:

                        inicio, fin = resultado_dash

                        estelas_dash.append(
                            (
                                inicio,
                                fin,
                                pygame.time.get_ticks()
                            )
                        )


                # RSHIFT pato
                if (
                    event.key == K_RSHIFT
                    and dos_jugadores
                    and not player2.caido
                ):

                    resultado_embestida = player2.embestida(
                        pygame.key.get_pressed()
                    )


                    if resultado_embestida is not None:

                        inicio, fin = resultado_embestida


                        estelas_dash.append(
                            (
                                inicio,
                                fin,
                                pygame.time.get_ticks()
                            )
                        )


                        golpeados = 0

                        golpeo_boss = False


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


                            if boss is not None and boss.alive():

                                if (
                                    not boss.fase_meteoritos
                                    and player2.rect.colliderect(boss.rect)
                                    and not golpeo_boss
                                ):

                                    boss.recibir_dano(3)

                                    golpeo_boss = True

                                    sonido_hit.play()


                            else:

                                enemigos_golpeados = pygame.sprite.spritecollide(
                                    player2,
                                    enemies,
                                    True
                                )


                                golpeados += len(
                                    enemigos_golpeados
                                )


                        player2.rect.center = fin


                        if golpeados > 0:

                            estadistica += golpeados * 5

                            sonido_hit.play()


            # spawns solo antes del BOSS
            elif event.type == ADDENEMY and not boss_aparecio:

                tipo = random.choices(
                    [
                        "normal",
                        "S",
                        "G",
                        "M",
                        "D",
                    ],
                    weights=[
                        45,
                        25,
                        14,
                        10,
                        6,
                    ],
                    k=1
                )[0]


                new_enemy = EnemyLevel2(
                    screen,
                    tipo
                )


                enemies.add(
                    new_enemy
                )

                all_sprites.add(
                    new_enemy
                )


            elif event.type == ADDPOWERUP:

                if len(powerups) == 0:

                    new_powerup = PowerUp(
                        screen
                    )

                    powerups.add(
                        new_powerup
                    )


            elif event.type == MOUSEBUTTONDOWN:

                if (
                    event.button == 1
                    and not player.caido
                ):

                    player.shoot(
                        pygame.mouse.get_pos()
                    )


        # ================= UPDATE =================
        if not pausado and not victoria:

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

                player.update(
                    pressed_keys
                )

            else:

                player.bullets.update()


            if dos_jugadores and not player2.caido:

                player2.update(
                    pressed_keys
                )


            if not boss_aparecio:

                enemies.update(
                    player.rect.center,
                    proyectiles_enemigos
                )


            proyectiles_enemigos.update()

            proyectiles_boss.update()

            meteoritos.update()


            # update jefe
            if (
                boss is not None
                and boss.alive()
            ):

                objetivos = []


                if not player.caido:

                    objetivos.append(
                        player.rect.center
                    )


                if (
                    dos_jugadores
                    and not player2.caido
                ):

                    objetivos.append(
                        player2.rect.center
                    )


                boss.update(
                    objetivos,
                    proyectiles_boss,
                    meteoritos
                )


            crosshair.update()

            powerups.update()


            # onda coop
            if (
                dos_jugadores
                and not player.caido
                and not player2.caido
            ):

                cargando = (
                    pressed_keys[K_SPACE]
                    and pressed_keys[K_RSHIFT]
                )

            else:

                cargando = False


            centro_x = (
                player.rect.centerx
                + player2.rect.centerx
            ) // 2

            centro_y = (
                player.rect.centery
                + player2.rect.centery
            ) // 2


            if onda.update(
                cargando,
                (
                    centro_x,
                    centro_y
                )
            ):

                if (
                    boss is not None
                    and boss.alive()
                ):

                    if not boss.fase_meteoritos:

                        boss.recibir_dano(5)

                        proyectiles_boss.empty()


                else:

                    estadistica += len(enemies) * 5


                    for enemigo in enemies.sprites():
                        enemigo.kill()


                    proyectiles_enemigos.empty()


            # puntos
            ahora_puntos = pygame.time.get_ticks()


            if (
                ahora_puntos
                - ultimo_segundo
                >= 1000
            ):

                estadistica += 1

                ultimo_segundo += 1000


            # BOSS a los 300
            if (
                estadistica >= 300
                and not boss_aparecio
            ):

                boss_aparecio = True


                pygame.time.set_timer(
                    ADDENEMY,
                    0
                )


                for enemigo in enemies.sprites():
                    enemigo.kill()


                proyectiles_enemigos.empty()


                boss = Boss(
                    screen
                )


                boss_group.add(
                    boss
                )


        if pausado:

            tiempo_visual = inicio_pausa

        else:

            tiempo_visual = pygame.time.get_ticks()


        # dash trail
        for estela in estelas_dash[:]:

            inicio, fin, tiempo_inicio = estela

            tiempo_pasado = (
                tiempo_visual
                - tiempo_inicio
            )


            if tiempo_pasado >= duracion_estela:

                if not pausado:
                    estelas_dash.remove(estela)

                continue


            transparencia = int(
                200
                * (
                    1
                    - tiempo_pasado / duracion_estela
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


        # ================= DIBUJO =================
        for entity in all_sprites:

            screen.blit(
                entity.image,
                entity.rect
            )


        for jefe in boss_group:

            screen.blit(
                jefe.image,
                jefe.rect
            )


        # barra de revivir
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
                        jugador.rect.centerx
                        - 40
                    )

                    barra_y = (
                        jugador.rect.top
                        - 14
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


        for bala in player.bullets:

            screen.blit(
                bala.image,
                bala.rect
            )


        for proyectil in proyectiles_enemigos:

            screen.blit(
                proyectil.image,
                proyectil.rect
            )


        for proyectil in proyectiles_boss:

            screen.blit(
                proyectil.image,
                proyectil.rect
            )


        for meteorito in meteoritos:

            screen.blit(
                meteorito.image,
                meteorito.rect
            )


        # vidas jorge
        for i in range(player.vidas):

            x = 20 + i * 40


            if player.escudo:

                screen.blit(
                    icono_corazon_shield,
                    (x, 20)
                )

            else:

                screen.blit(
                    icono_corazon,
                    (x, 20)
                )


        # score
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


        pos_x_puntos = (
            screen.get_width()
            - texto_puntos.get_width()
            - 20
        )


        screen.blit(
            sombra_puntos,
            (
                pos_x_puntos + 2,
                22
            )
        )

        screen.blit(
            texto_puntos,
            (
                pos_x_puntos,
                20
            )
        )


        # municion
        inicio_x = 20
        inicio_y = 62

        separacion = 8

        ancho_icono = icono_flecha.get_width()


        for i in range(player.max_disparos):

            x = (
                inicio_x
                + i
                * (
                    ancho_icono
                    + separacion
                )
            )


            posicion_icono = (
                x,
                inicio_y
            )


            if player.rapid_fire:

                screen.blit(
                    icono_flecha_rapid,
                    posicion_icono
                )


            elif i >= player.max_disparos - player.disparos:

                screen.blit(
                    icono_flecha_sombra,
                    posicion_icono
                )


            else:

                screen.blit(
                    icono_flecha,
                    posicion_icono
                )


        # dash mana
        mana_x = 20
        mana_y = 90

        mana_ancho = 200
        mana_alto = 9


        tiempo_dash = (
            tiempo_visual
            - player.ultimo_dash
        )


        mana_dash = min(
            1,
            tiempo_dash / player.cooldown_dash
        )


        pygame.draw.rect(
            screen,
            (30, 30, 35),
            (
                mana_x,
                mana_y,
                mana_ancho,
                mana_alto
            ),
            border_radius=4
        )


        pygame.draw.rect(
            screen,
            (255, 200, 40),
            (
                mana_x,
                mana_y,
                int(mana_ancho * mana_dash),
                mana_alto
            ),
            border_radius=4
        )


        # rapid fire
        if player.rapid_fire:

            barra_x = 20
            barra_y = 106

            barra_ancho = 200
            barra_alto = 5


            tiempo_restante = (
                player.fin_rapid_fire
                - tiempo_visual
            )


            progreso = (
                tiempo_restante
                / player.duracion_rapid_fire
            )


            progreso = max(
                0,
                min(1, progreso)
            )


            pygame.draw.rect(
                screen,
                (35, 35, 40),
                (
                    barra_x,
                    barra_y,
                    barra_ancho,
                    barra_alto
                ),
                border_radius=3
            )


            pygame.draw.rect(
                screen,
                (255, 205, 40),
                (
                    barra_x,
                    barra_y,
                    int(barra_ancho * progreso),
                    barra_alto
                ),
                border_radius=3
            )


        # player2 hud
        if dos_jugadores:

            for i in range(player2.vidas):

                x = (
                    screen.get_width()
                    - 54
                    - i * 40
                )


                if player2.escudo:

                    screen.blit(
                        icono_corazon_shield,
                        (x, 65)
                    )

                else:

                    screen.blit(
                        icono_corazon,
                        (x, 65)
                    )


            barra_x = (
                screen.get_width()
                - 220
            )


            tiempo_embestida = (
                tiempo_visual
                - player2.ultima_embestida
            )


            mana_embestida = min(
                1,
                tiempo_embestida
                / player2.cooldown_embestida
            )


            pygame.draw.rect(
                screen,
                (30, 30, 35),
                (
                    barra_x,
                    105,
                    200,
                    9
                ),
                border_radius=4
            )


            if player2.furia:

                color_barra = (255, 120, 40)

            else:

                color_barra = (80, 180, 255)


            pygame.draw.rect(
                screen,
                color_barra,
                (
                    barra_x,
                    105,
                    int(200 * mana_embestida),
                    9
                ),
                border_radius=4
            )


        # onda coop
        if dos_jugadores:

            onda_ancho = 240

            onda_x = (
                screen.get_width() // 2
                - onda_ancho // 2
            )

            onda_y = 24


            if onda.espera > 0:

                progreso_onda = (
                    1
                    - onda.espera / onda.cooldown
                )

                color_onda = (110, 110, 120)


            elif onda.carga > 0:

                progreso_onda = (
                    onda.carga / onda.tiempo_carga
                )

                color_onda = (255, 255, 255)


            else:

                progreso_onda = 1

                color_onda = (170, 90, 255)


            pygame.draw.rect(
                screen,
                (30, 30, 35),
                (
                    onda_x,
                    onda_y,
                    onda_ancho,
                    12
                ),
                border_radius=5
            )


            pygame.draw.rect(
                screen,
                color_onda,
                (
                    onda_x,
                    onda_y,
                    int(onda_ancho * progreso_onda),
                    12
                ),
                border_radius=5
            )


        # cuenta atras antes del jefe
        if not boss_aparecio:

            faltan = max(
                0,
                300 - estadistica
            )


            texto_boss = font_boss.render(
                f"BOSS EN {faltan} PTS",
                True,
                (255, 100, 100)
            )


            screen.blit(
                texto_boss,
                texto_boss.get_rect(
                    center=(
                        screen.get_width() // 2,
                        70
                    )
                )
            )


        # VIDA DEL BOSS
        if (
            boss is not None
            and boss.alive()
        ):

            barra_ancho = 500
            barra_alto = 22


            barra_x = (
                screen.get_width() // 2
                - barra_ancho // 2
            )

            barra_y = 55


            porcentaje = (
                boss.vidas
                / boss.max_vidas
            )


            pygame.draw.rect(
                screen,
                (30, 30, 35),
                (
                    barra_x,
                    barra_y,
                    barra_ancho,
                    barra_alto
                ),
                border_radius=6
            )


            pygame.draw.rect(
                screen,
                (210, 35, 35),
                (
                    barra_x,
                    barra_y,
                    int(barra_ancho * porcentaje),
                    barra_alto
                ),
                border_radius=6
            )


            pygame.draw.rect(
                screen,
                (255, 210, 90),
                (
                    barra_x,
                    barra_y,
                    barra_ancho,
                    barra_alto
                ),
                3,
                border_radius=6
            )


            texto_boss = font_boss.render(
                f"DRAGON KING   {boss.vidas:g}/{boss.max_vidas:g}",
                True,
                (255, 255, 255)
            )


            screen.blit(
                texto_boss,
                texto_boss.get_rect(
                    center=(
                        screen.get_width() // 2,
                        40
                    )
                )
            )


        if (
            boss is not None
            and boss.alive()
            and boss.fase_meteoritos
        ):

            texto_meteoritos = font_aviso.render(
                "LLUVIA DE METEORITOS",
                True,
                (255, 120, 40)
            )


            screen.blit(
                texto_meteoritos,
                texto_meteoritos.get_rect(
                    center=(
                        screen.get_width() // 2,
                        110
                    )
                )
            )


        # ================= COLISIONES =================
        if not pausado and not victoria:

            # tiros M/D contra Jorge
            if player.caido:

                impactos = []

            else:

                impactos = pygame.sprite.spritecollide(
                    player,
                    proyectiles_enemigos,
                    True
                )


            for proyectil in impactos:

                if proyectil.tipo == "M":

                    player.aplicar_slow()


                elif proyectil.tipo == "D":

                    hacer_dano(
                        player,
                        sonido_damage
                    )


            # proyectil boss con jorge
            if not player.caido:

                impactos_boss = pygame.sprite.spritecollide(
                    player,
                    proyectiles_boss,
                    True
                )


                if impactos_boss:

                    hacer_dano(
                        player,
                        sonido_damage
                    )


            # boss shots j2
            if (
                dos_jugadores
                and not player2.caido
            ):

                impactos_boss_2 = pygame.sprite.spritecollide(
                    player2,
                    proyectiles_boss,
                    True
                )


                if impactos_boss_2:

                    hacer_dano(
                        player2,
                        sonido_damage
                    )


            # meteoros jorge
            if not player.caido:

                meteoritos_j1 = pygame.sprite.spritecollide(
                    player,
                    meteoritos,
                    True
                )


                if meteoritos_j1:

                    hacer_dano(
                        player,
                        sonido_damage
                    )


            # meteoros j2
            if (
                dos_jugadores
                and not player2.caido
            ):

                meteoritos_j2 = pygame.sprite.spritecollide(
                    player2,
                    meteoritos,
                    True
                )


                if meteoritos_j2:

                    hacer_dano(
                        player2,
                        sonido_damage
                    )


            # powerup Jorge
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


            # powerup j2
            if (
                dos_jugadores
                and not player2.caido
            ):

                recogidos_2 = pygame.sprite.spritecollide(
                    player2,
                    powerups,
                    True
                )


                for powerup in recogidos_2:

                    sonido_powerup.play()

                    player2.activar_powerup(
                        powerup.tipo
                    )


            # dragones con jorge antes del boss
            if (
                not boss_aparecio
                and not player.caido
            ):

                enemigos_tocando = pygame.sprite.spritecollide(
                    player,
                    enemies,
                    False
                )


                if enemigos_tocando:

                    enemigos_tocando[0].kill()

                    hacer_dano(
                        player,
                        sonido_damage
                    )


            # dragones j2
            if (
                not boss_aparecio
                and dos_jugadores
                and not player2.caido
            ):

                enemigos_tocando_2 = pygame.sprite.spritecollide(
                    player2,
                    enemies,
                    False
                )


                if enemigos_tocando_2:

                    enemigos_tocando_2[0].kill()

                    hacer_dano(
                        player2,
                        sonido_damage
                    )


            # embestida del boss
            if (
                boss is not None
                and boss.alive()
                and boss.en_embestida
            ):

                if (
                    not player.caido
                    and player.rect.colliderect(boss.rect)
                ):

                    hacer_dano(
                        player,
                        sonido_damage
                    )

                    boss.terminar_embestida()


                elif (
                    dos_jugadores
                    and not player2.caido
                    and player2.rect.colliderect(boss.rect)
                ):

                    hacer_dano(
                        player2,
                        sonido_damage
                    )

                    boss.terminar_embestida()


            # revivir
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


            # muerto?
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
                    "dead",
                    estadistica
                )


            # ===========================================
            # BALAS CON DAÑO Y PENETRACION vs dragones
            # ===========================================
            if not boss_aparecio:

                colisiones_balas = pygame.sprite.groupcollide(
                    player.bullets,
                    enemies,
                    True,
                    False,
                    colision_bala_enemigo
                )


                if colisiones_balas:

                    sonido_hit.play()


                for bala, lista_enemigos in colisiones_balas.items():

                    for enemigo in lista_enemigos:

                        if enemigo.alive():

                            murio_enemigo = enemigo.recibir_dano(
                                bala.dano
                            )


                            if murio_enemigo:

                                estadistica += 5


            # ===========================================
            # BALA vs BOSS
            # ===========================================
            if (
                boss is not None
                and boss.alive()
                and not boss.fase_meteoritos
            ):

                for bala in player.bullets.sprites():

                    if (
                        boss not in bala.enemigos_golpeados
                        and bala.rect.colliderect(boss.rect)
                    ):

                        bala.enemigos_golpeados.add(
                            boss
                        )


                        boss.recibir_dano(
                            bala.dano
                        )


                        sonido_hit.play()


                        # usa 1 penetracion
                        bala.kill()


                        # el primer tiro que lo baja a 150 puede iniciar meteoros
                        if boss.fase_meteoritos:
                            break


            # victoria
            if (
                boss_aparecio
                and boss is not None
                and not boss.alive()
                and not victoria
            ):

                victoria = True

                inicio_victoria = pygame.time.get_ticks()


                proyectiles_boss.empty()

                proyectiles_enemigos.empty()

                meteoritos.empty()


                estadistica += 200


            screen.blit(
                crosshair.image,
                crosshair.rect
            )


        # victoria visual
        if victoria:

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


            texto_victoria = font_victoria.render(
                "BOSS DERROTADO",
                True,
                (255, 215, 80)
            )


            screen.blit(
                texto_victoria,
                texto_victoria.get_rect(
                    center=(
                        screen.get_width() // 2,
                        screen.get_height() // 2
                    )
                )
            )


            if (
                pygame.time.get_ticks()
                - inicio_victoria
                >= 2500
            ):

                pygame.mixer.music.stop()

                pygame.mouse.set_visible(True)

                return (
                    "victory",
                    estadistica
                )


        # PAUSA visual
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


            titulo_pausa = font_pausa.render(
                "PAUSA",
                True,
                (255, 215, 80)
            )


            screen.blit(
                titulo_pausa,
                titulo_pausa.get_rect(
                    center=(
                        screen.get_width() // 2,
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
                ),
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


                texto_render = font_boton.render(
                    texto,
                    True,
                    (255, 255, 255)
                )


                screen.blit(
                    texto_render,
                    texto_render.get_rect(
                        center=boton.center
                    )
                )


        pygame.display.flip()

        clock.tick(60)


    pygame.mixer.music.stop()

    pygame.mouse.set_visible(True)

    return "quit"