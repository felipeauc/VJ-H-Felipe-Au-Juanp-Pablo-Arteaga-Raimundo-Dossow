ARCHIVO_HABILIDADES = "habilidades.txt"

orden = ["vida", "municion", "recarga", "penetracion", "dano", "tamano"]

niveles = {
    "vida": 0,
    "municion": 0,
    "recarga": 0,
    "penetracion": 0,
    "dano": 0,
    "tamano": 0,
}

maximos = {
    "vida": 5,
    "municion": 5,
    "recarga": 5,
    "penetracion": 3,
    "dano": 4,
    "tamano": 5,
}

costos_base = {
    "vida": 600,
    "municion": 400,
    "recarga": 500,
    "penetracion": 750,
    "dano": 900,
    "tamano": 900,
}

multiplicadores = {
    "vida": 1.70,
    "municion": 1.60,
    "recarga": 1.65,
    "penetracion": 1.80,
    "dano": 1.85,
    "tamano": 1.75,
}


def cargar():
    try:
        with open(ARCHIVO_HABILIDADES, "r") as archivo:
            lineas = archivo.readlines()

        for i, nombre in enumerate(orden):
            if i < len(lineas):
                try:
                    valor = int(lineas[i].strip())
                    niveles[nombre] = max(0, min(valor, maximos[nombre]))
                except ValueError:
                    niveles[nombre] = 0

    except FileNotFoundError:
        pass


def guardar():
    with open(ARCHIVO_HABILIDADES, "w") as archivo:
        for nombre in orden:
            archivo.write(f"{niveles[nombre]}\n")


def costo(nombre):
    nivel = niveles[nombre]

    if nivel >= maximos[nombre]:
        return 0

    return round(costos_base[nombre] * (multiplicadores[nombre] ** nivel))


def comprar(nombre, coins):
    if nombre not in niveles:
        return coins, False

    if niveles[nombre] >= maximos[nombre]:
        return coins, False

    precio = costo(nombre)

    if coins < precio:
        return coins, False

    coins -= precio
    niveles[nombre] += 1

    guardar()

    return coins, True


def vida_maxima(nivel=None):
    if nivel is None:
        nivel = niveles["vida"]

    return 5 + nivel


def municion_maxima(nivel=None):
    if nivel is None:
        nivel = niveles["municion"]

    return 5 + nivel


def tiempo_recarga(nivel=None):
    if nivel is None:
        nivel = niveles["recarga"]

    return max(1500, 3000 - nivel * 300)


def penetracion(nivel=None):
    if nivel is None:
        nivel = niveles["penetracion"]

    return 1 + nivel


def dano(nivel=None):
    if nivel is None:
        nivel = niveles["dano"]

    # NIVEL 0 = 1 daño
    # NIVEL 4 = 5 daño
    return 1 + nivel


def escala_jugador(nivel=None):
    if nivel is None:
        nivel = niveles["tamano"]

    # 100%, 90%, 80%, 70%, 60%, 50%
    return max(0.50, 1.0 - nivel * 0.10)


def texto_valor(nombre, nivel=None):
    if nivel is None:
        nivel = niveles[nombre]

    if nombre == "vida":
        return f"{vida_maxima(nivel)} corazones"

    if nombre == "municion":
        return f"{municion_maxima(nivel)} flechas"

    if nombre == "recarga":
        return f"{tiempo_recarga(nivel) / 1000:.1f} s"

    if nombre == "penetracion":
        return f"{penetracion(nivel)} enemigos"

    if nombre == "dano":
        return f"{dano(nivel)} daño"

    if nombre == "tamano":
        return f"{round(escala_jugador(nivel) * 100)}%"

    return "-"


cargar()