ARCHIVO_LOGROS = "logros.txt"

CANTIDAD_LOGROS = 12


# estado de los logros
def cargar():

    try:

        with open(ARCHIVO_LOGROS, "r") as archivo:
            lineas = archivo.readlines()

        estado = []

        for linea in lineas[:CANTIDAD_LOGROS]:
            estado.append(linea.strip() == "True")

        while len(estado) < CANTIDAD_LOGROS:
            estado.append(False)

        return estado

    except (FileNotFoundError, ValueError):

        return [False] * CANTIDAD_LOGROS


logros = cargar()

# logros nuevos que todavia no se mostraron en pantalla
_notificaciones_pendientes = []


# estadisticas de la partida actual
partida_activa = False

disparos_partida = 0
danos_partida = 0
escudos_partida = 0
rapid_usado_partida = False

# gasto de una sola visita a tienda
gasto_visita_tienda = 0

_hooks_instalados = False


def guardar():

    with open(ARCHIVO_LOGROS, "w") as archivo:

        for desbloqueado in logros:
            archivo.write(f"{desbloqueado}\n")


def obtener_estado():

    return logros.copy()


def desbloquear(id_logro):

    if id_logro < 0 or id_logro >= CANTIDAD_LOGROS:
        return False

    if logros[id_logro]:
        return False

    logros[id_logro] = True

    guardar()

    _notificaciones_pendientes.append(id_logro)

    return True


def consumir_notificaciones():

    global _notificaciones_pendientes

    pendientes = _notificaciones_pendientes.copy()

    _notificaciones_pendientes = []

    return pendientes


# ==========================================
# PARTIDAS
# ==========================================

def iniciar_partida():

    global partida_activa
    global disparos_partida
    global danos_partida
    global escudos_partida
    global rapid_usado_partida

    partida_activa = True

    disparos_partida = 0
    danos_partida = 0
    escudos_partida = 0
    rapid_usado_partida = False


def registrar_disparo():

    global disparos_partida

    if partida_activa:
        disparos_partida += 1


def registrar_dano():

    global danos_partida

    if partida_activa:
        danos_partida += 1


def registrar_powerup(tipo):

    global escudos_partida
    global rapid_usado_partida

    if not partida_activa:
        return

    if tipo == "shield":

        escudos_partida += 1

        # Fortaleza Espacial
        if escudos_partida >= 3:
            desbloquear(7)

    elif tipo == "rapid_fire":

        rapid_usado_partida = True

        # Sobrecarga
        desbloquear(8)


def finalizar_partida(puntos, murio=False):

    global partida_activa

    # Primeros Pasos
    desbloquear(0)

    # Piloto Veterano
    if puntos >= 500:
        desbloquear(1)

    # Leyenda Galactica
    if puntos >= 1000:
        desbloquear(2)

    # Intocable
    if puntos >= 250 and danos_partida == 0:
        desbloquear(6)

    # por seguridad se vuelven a comprobar
    if escudos_partida >= 3:
        desbloquear(7)

    if rapid_usado_partida:
        desbloquear(8)

    # logro oculto: morir muy rapido
    if murio and puntos < 10:
        desbloquear(9)

    # Pacifista
    if puntos >= 100 and disparos_partida == 0:
        desbloquear(10)

    partida_activa = False


# ==========================================
# COINS
# ==========================================

def revisar_coins(coins):

    if coins >= 100:
        desbloquear(3)


# ==========================================
# HABILIDADES
# ==========================================

def revisar_habilidades():

    import habilidades

    if (
        habilidades.niveles["vida"]
        >= habilidades.maximos["vida"]
    ):
        desbloquear(4)

    if (
        habilidades.niveles["municion"]
        >= habilidades.maximos["municion"]
    ):
        desbloquear(5)


# ==========================================
# TIENDA
# ==========================================

def iniciar_visita_tienda():

    global gasto_visita_tienda

    gasto_visita_tienda = 0


def registrar_gasto(cantidad):

    global gasto_visita_tienda

    if cantidad <= 0:
        return

    gasto_visita_tienda += cantidad

    # Cliente VIP
    if gasto_visita_tienda >= 500:
        desbloquear(11)


# ==========================================
# PROGRESO VIEJO
# ==========================================

def revisar_historico(max_puntaje, coins):

    # sirve para no perder logros si ya habia progreso
    if max_puntaje > 0:
        desbloquear(0)

    if max_puntaje >= 500:
        desbloquear(1)

    if max_puntaje >= 1000:
        desbloquear(2)

    revisar_coins(coins)
    revisar_habilidades()


# ==========================================
# HOOKS
#
# Con esto no hay que ensuciar los 3 game_scene.
# Registramos disparos, daño y powerups directamente
# desde Player y Player2.
# ==========================================

def instalar_hooks():

    global _hooks_instalados

    if _hooks_instalados:
        return

    from elements import Player, Player2

    # --------------------------
    # PLAYER 1 - DISPARO
    # --------------------------

    disparo_original = Player.shoot

    def shoot_con_logro(self, *args, **kwargs):

        cantidad_antes = len(self.bullets)

        resultado = disparo_original(
            self,
            *args,
            **kwargs
        )

        cantidad_despues = len(self.bullets)

        # solo cuenta si realmente salio una bala
        if cantidad_despues > cantidad_antes:
            registrar_disparo()

        return resultado

    Player.shoot = shoot_con_logro


    # --------------------------
    # PLAYER 1 - DAÑO
    # --------------------------

    dano_original = Player.recibir_dano

    def dano_con_logro(self, *args, **kwargs):

        vidas_antes = self.vidas

        resultado = dano_original(
            self,
            *args,
            **kwargs
        )

        if self.vidas < vidas_antes:
            registrar_dano()

        return resultado

    Player.recibir_dano = dano_con_logro


    # --------------------------
    # PLAYER 1 - POWERUPS
    # --------------------------

    power_original = Player.activar_powerup

    def power_con_logro(self, tipo, *args, **kwargs):

        resultado = power_original(
            self,
            tipo,
            *args,
            **kwargs
        )

        registrar_powerup(tipo)

        return resultado

    Player.activar_powerup = power_con_logro


    # --------------------------
    # PLAYER 2 - DAÑO
    # --------------------------

    dano2_original = Player2.recibir_dano

    def dano2_con_logro(self, *args, **kwargs):

        vidas_antes = self.vidas

        resultado = dano2_original(
            self,
            *args,
            **kwargs
        )

        if self.vidas < vidas_antes:
            registrar_dano()

        return resultado

    Player2.recibir_dano = dano2_con_logro


    # --------------------------
    # PLAYER 2 - POWERUPS
    # --------------------------

    power2_original = Player2.activar_powerup

    def power2_con_logro(self, tipo, *args, **kwargs):

        resultado = power2_original(
            self,
            tipo,
            *args,
            **kwargs
        )

        registrar_powerup(tipo)

        return resultado

    Player2.activar_powerup = power2_con_logro

    _hooks_instalados = True