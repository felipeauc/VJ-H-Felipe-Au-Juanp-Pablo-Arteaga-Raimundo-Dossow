jugador_actual = None
muertes_acumuladas = 0


def registrar_jugador(jugador):
    global jugador_actual, muertes_acumuladas

    jugador_actual = jugador
    muertes_acumuladas = 0


def registrar_muerte(cantidad=1):
    global muertes_acumuladas

    if cantidad <= 0:
        return 0

    muertes_acumuladas += cantidad

    if jugador_actual is None:
        return 0

    corazones_curados = 0

    while muertes_acumuladas >= 10 and not jugador_actual.caido and jugador_actual.vidas < jugador_actual.max_vidas:
        muertes_acumuladas -= 10
        jugador_actual.vidas += 1
        corazones_curados += 1

    return corazones_curados


def progreso():
    return muertes_acumuladas


def progreso_siguiente_corazon():
    return muertes_acumuladas % 10