# sistema de mejoras permanentes, se guardan aparte pq si no se mezcla todo
# con progreso y despues es un cacho

ARCHIVO_HABILIDADES = "habilidades.txt"


niveles = {
    "vida": 0,
    "municion": 0,
    "recarga": 0,
    "penetracion": 0,
    "dano": 0,
}


# maximos de cada habildiad
maximos = {
    "vida": 5,
    "municion": 5,
    "recarga": 5,
    "penetracion": 3,
    "dano": 4,
}


# precios iniciales, la idea es que cueste farmearlos
costos_base = {
    "vida": 600,
    "municion": 400,
    "recarga": 500,
    "penetracion": 750,
    "dano": 900,
}


# cuanto se encarece cada compra
multiplicadores = {
    "vida": 1.70,
    "municion": 1.60,
    "recarga": 1.65,
    "penetracion": 1.80,
    "dano": 1.85,
}


def cargar():

    try:

        with open(ARCHIVO_HABILIDADES, "r") as archivo:
            lineas = archivo.readlines()

        claves = list(niveles.keys())

        for i in range(min(len(lineas), len(claves))):

            try:
                valor = int(lineas[i].strip())

            except ValueError:
                valor = 0

            nombre = claves[i]

            niveles[nombre] = max(
                0,
                min(valor, maximos[nombre])
            )

    except FileNotFoundError:
        pass


def guardar():

    with open(ARCHIVO_HABILIDADES, "w") as archivo:

        archivo.write(f"{niveles['vida']}\n")
        archivo.write(f"{niveles['municion']}\n")
        archivo.write(f"{niveles['recarga']}\n")
        archivo.write(f"{niveles['penetracion']}\n")
        archivo.write(f"{niveles['dano']}")


# calcula el precio DEL SIGUIENTE nivel
def costo(nombre):

    nivel = niveles[nombre]

    return round(
        costos_base[nombre]
        * multiplicadores[nombre] ** nivel
    )


# COMPRA, devuelve las coins nuevas y si compro o no
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


# valores reales usados por el player
def vida_maxima():
    return 5 + niveles["vida"]


def municion_maxima():
    return 5 + niveles["municion"]


def tiempo_recarga():
    return 3000 - niveles["recarga"] * 300


def penetracion():
    return 1 + niveles["penetracion"]


def dano():
    return 1 + niveles["dano"] * 0.5


# para que la tienda muestre algo entendible
def texto_valor(nombre, nivel=None):

    if nivel is None:
        nivel = niveles[nombre]

    if nombre == "vida":
        return f"{5 + nivel} corazones"

    if nombre == "municion":
        return f"{5 + nivel} flechas"

    if nombre == "recarga":
        tiempo = 3000 - nivel * 300
        return f"{tiempo / 1000:.1f} segundos"

    if nombre == "penetracion":
        return f"{1 + nivel} enemigos"

    if nombre == "dano":
        return f"{1 + nivel * 0.5:.1f} dano"


cargar()