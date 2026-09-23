import os


#---- FEATURE TIENDA - ASSETS DISPONIBLES ----
ASSETS = {
    "background": [
        "assets/background.png",
        "assets/background_2.png",
        "assets/background_3.png",
        "assets/background_4.png",
        "assets/background_5.png",
    ],

    "bug": [
        "assets/bug.png",
        "assets/bug_2.png",
        "assets/bug_3.png",
        "assets/bug_4.png",
        "assets/bug_5.png",
    ],

    "bullet": [
        "assets/bullet.png",
        "assets/bullet_2.png",
        "assets/bullet_3.png",
        "assets/bullet_4.png",
        "assets/bullet_5.png",
    ],
}

seleccion = {
    "background": 0,
    "bug": 0,
    "bullet": 0,
}
#----


#---- FEATURE TIENDA - OBTENER ASSET SELECCIONADO ----
def obtener_asset(categoria):
    return ASSETS[categoria][seleccion[categoria]]
#----


#---- FEATURE TIENDA - CAMBIAR ASSET ----
def cambiar_asset(categoria, direccion):

    opciones = ASSETS[categoria]
    posicion = seleccion[categoria]

    for i in range(len(opciones)):
        posicion = (posicion + direccion) % len(opciones)

        if os.path.exists(opciones[posicion]):
            seleccion[categoria] = posicion
            return
#----