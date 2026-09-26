import pygame

cola = []
TIEMPO_VISIBLE = 4000  
ANCHO_CAJA = 300
ALTO_CAJA = 70
sonido_logro = None

nombres_logros = [
    "Primeros Pasos", "Piloto Veterano", "Leyenda Galáctica",
    "Primera Paga", "Tanque Espacial", "Arsenal Infinito",
    "Intocable", "Fortaleza Espacial", "Sobrecarga Láser",
    "Houston, hay un problema", "Pacifista", "Héroe del reino"
]

def reproducir_sonido():
    global sonido_logro

    if sonido_logro is None:
        try:
            sonido_logro = pygame.mixer.Sound("assets/notificacion_logro.wav")
            sonido_logro.set_volume(0.7)
        except:
            sonido_logro = "ERROR"

    if sonido_logro != "ERROR" and sonido_logro is not None:
        sonido_logro.play()

def mostrar(id_logro):

    cola.append({
        "texto": nombres_logros[id_logro],
        "inicio": pygame.time.get_ticks(),
        "sonido_reproducido": False
    })

def dibujar(screen):
    if not cola:
        return

    noti = cola[0]
    tiempo_actual = pygame.time.get_ticks()
    tiempo_pasado = tiempo_actual - noti["inicio"]

    if not noti["sonido_reproducido"]:
        reproducir_sonido()
        noti["sonido_reproducido"] = True

    if tiempo_pasado > TIEMPO_VISIBLE:
        cola.pop(0)
        if cola:
            cola[0]["inicio"] = pygame.time.get_ticks()
        return

    x_base = screen.get_width() - ANCHO_CAJA - 20
    y_base = 20

    if tiempo_pasado < 500:  
        y_actual = y_base - ALTO_CAJA - 20 + ((ALTO_CAJA + 20) * (tiempo_pasado / 500))
    elif tiempo_pasado > TIEMPO_VISIBLE - 500:  
        restante = TIEMPO_VISIBLE - tiempo_pasado
        y_actual = y_base - ALTO_CAJA - 20 + ((ALTO_CAJA + 20) * (restante / 500))
    else:  
        y_actual = y_base

    rect = pygame.Rect(x_base, y_actual, ANCHO_CAJA, ALTO_CAJA)
    pygame.draw.rect(screen, (33, 33, 33), rect, border_radius=8)
    pygame.draw.rect(screen, (255, 215, 80), rect, width=2, border_radius=8)

    font_titulo = pygame.font.Font(None, 24)
    font_logro = pygame.font.Font(None, 30)

    texto_titulo = font_titulo.render("Logro Desbloqueado", True, (200, 200, 200))
    texto_nombre = font_logro.render(noti["texto"], True, (255, 215, 80))

    screen.blit(texto_titulo, (x_base + 20, y_actual + 15))
    screen.blit(texto_nombre, (x_base + 20, y_actual + 35))