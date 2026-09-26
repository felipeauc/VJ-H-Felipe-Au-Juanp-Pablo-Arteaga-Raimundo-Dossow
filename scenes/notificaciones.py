import pygame
import logros


cola = []

TIEMPO_VISIBLE = 4000

ANCHO_CAJA = 320
ALTO_CAJA = 76

sonido_logro = None

flip_original = None


nombres_logros = [
    "Primeros Pasos",
    "Piloto Veterano",
    "Leyenda Galáctica",
    "Primera Paga",
    "Tanque Espacial",
    "Arsenal Infinito",
    "Intocable",
    "Fortaleza Espacial",
    "Sobrecarga",
    "¿Eres nuevo?",
    "Pacifista",
    "Cliente VIP",
]


def reproducir_sonido():

    global sonido_logro

    if sonido_logro is None:

        try:

            sonido_logro = pygame.mixer.Sound(
                "assets/notificacion_logro.wav"
            )

            sonido_logro.set_volume(0.7)

        except:
            sonido_logro = False

    if sonido_logro:
        sonido_logro.play()


def mostrar(id_logro):

    if id_logro < 0 or id_logro >= len(nombres_logros):
        return

    cola.append({
        "texto": nombres_logros[id_logro],
        "inicio": pygame.time.get_ticks(),
        "sonido_reproducido": False
    })


def absorber_logros_nuevos():

    nuevos = logros.consumir_notificaciones()

    for id_logro in nuevos:
        mostrar(id_logro)


def dibujar(screen):

    absorber_logros_nuevos()

    if not cola:
        return

    noti = cola[0]

    tiempo_actual = pygame.time.get_ticks()

    tiempo_pasado = (
        tiempo_actual
        - noti["inicio"]
    )

    if not noti["sonido_reproducido"]:

        reproducir_sonido()

        noti["sonido_reproducido"] = True

    if tiempo_pasado > TIEMPO_VISIBLE:

        cola.pop(0)

        if cola:
            cola[0]["inicio"] = pygame.time.get_ticks()

        return

    x_base = (
        screen.get_width()
        - ANCHO_CAJA
        - 20
    )

    y_base = 20

    # entrada
    if tiempo_pasado < 450:

        progreso = tiempo_pasado / 450

        y_actual = (
            y_base
            - ALTO_CAJA
            - 30
            + (
                ALTO_CAJA + 30
            ) * progreso
        )

    # salida
    elif tiempo_pasado > TIEMPO_VISIBLE - 450:

        restante = (
            TIEMPO_VISIBLE
            - tiempo_pasado
        )

        progreso = restante / 450

        y_actual = (
            y_base
            - ALTO_CAJA
            - 30
            + (
                ALTO_CAJA + 30
            ) * progreso
        )

    else:

        y_actual = y_base

    rect = pygame.Rect(
        x_base,
        int(y_actual),
        ANCHO_CAJA,
        ALTO_CAJA
    )

    sombra = pygame.Surface(
        (
            ANCHO_CAJA,
            ALTO_CAJA
        ),
        pygame.SRCALPHA
    )

    sombra.fill(
        (20, 20, 25, 235)
    )

    screen.blit(
        sombra,
        rect
    )

    pygame.draw.rect(
        screen,
        (255, 215, 80),
        rect,
        width=2,
        border_radius=8
    )

    font_titulo = pygame.font.Font(
        None,
        23
    )

    font_logro = pygame.font.Font(
        None,
        29
    )

    texto_titulo = font_titulo.render(
        "LOGRO DESBLOQUEADO",
        True,
        (210, 210, 210)
    )

    texto_nombre = font_logro.render(
        noti["texto"],
        True,
        (255, 215, 80)
    )

    screen.blit(
        texto_titulo,
        (
            x_base + 18,
            y_actual + 13
        )
    )

    screen.blit(
        texto_nombre,
        (
            x_base + 18,
            y_actual + 39
        )
    )


# hace que todas las escenas muestren notificaciones
# aunque no llamen dibujar() directamente
def instalar_overlay():

    global flip_original

    if flip_original is not None:
        return

    flip_original = pygame.display.flip

    def flip_con_logros():

        screen = pygame.display.get_surface()

        if screen is not None:
            dibujar(screen)

        flip_original()

    pygame.display.flip = flip_con_logros