if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_UP
from pygame.math import Vector2

import habilidades


# pajaro normal
Jugador2PNG = pygame.image.load("assets/jugador2.png")
Jugador2PNG_scaled = pygame.transform.scale(Jugador2PNG, (80, 80))

# pajaro con shield
Jugador2ShieldPNG = pygame.image.load("assets/jugador2_shield.png")
Jugador2ShieldPNG_scaled = pygame.transform.scale(Jugador2ShieldPNG, (80, 80))

# imagen para el ataque giratorio
Ataque360PNG = pygame.image.load("assets/360.png")
Ataque360PNG_scaled = pygame.transform.scale(Ataque360PNG, (180, 180))


class Player2(pygame.sprite.Sprite):

    def __init__(self, screen):

        super().__init__()

        self.image = Jugador2PNG_scaled
        self.rect = self.image.get_rect(midleft=(0, screen.get_height() // 2))

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # movimiento un poco mas controlable
        self.velocidad = 5

        # vidas
        self.max_vidas = habilidades.vida_maxima()
        self.vidas = self.max_vidas

        # coop
        self.caido = False
        self.progreso_revivir = 0

        # ==============================
        # DASH
        # ==============================

        self.distancia_embestida = 125

        self.dano_embestida = 2
        self.dano_embestida_boss = 3

        self.cooldown_embestida_normal = 1800
        self.cooldown_embestida_furia = 650

        self.cooldown_embestida = self.cooldown_embestida_normal
        self.ultima_embestida = -self.cooldown_embestida

        self.sonido_embestida = pygame.mixer.Sound("assets/dash.wav")
        self.sonido_embestida.set_volume(0.65)

        # ==============================
        # ATAQUE 360
        # ==============================

        self.radio_360 = 100

        self.dano_360 = 2
        self.dano_360_boss = 3

        self.cooldown_360_normal = 1500
        self.cooldown_360_furia = 750

        self.cooldown_360 = self.cooldown_360_normal
        self.ultimo_360 = -self.cooldown_360

        self.imagen_360 = Ataque360PNG_scaled

        self.mostrando_360 = False

        self.inicio_efecto_360 = 0
        self.fin_efecto_360 = 0

        self.duracion_efecto_360 = 360

        self.sonido_360 = pygame.mixer.Sound("assets/360.wav")
        self.sonido_360.set_volume(0.75)

        # ==============================
        # INMORTALIDAD CORTA
        # ==============================

        self.duracion_inmortalidad = 200
        self.inmortal_hasta = 0

        # ==============================
        # POWERUPS
        # ==============================

        self.escudo = False

        self.furia = False
        self.duracion_furia = 7000
        self.fin_furia = 0


    def update(self, pressed_keys):

        direccion = Vector2(0, 0)

        if pressed_keys[K_UP]:
            direccion.y -= 1

        if pressed_keys[K_DOWN]:
            direccion.y += 1

        if pressed_keys[K_LEFT]:
            direccion.x -= 1

        if pressed_keys[K_RIGHT]:
            direccion.x += 1

        # normalizar evita que diagonal sea mas rapida
        if direccion.length() > 0:

            direccion = direccion.normalize()

            self.rect.x += int(direccion.x * self.velocidad)
            self.rect.y += int(direccion.y * self.velocidad)

        # no salir de pantalla
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

        ahora = pygame.time.get_ticks()

        # terminar visual del ataque
        if self.mostrando_360 and ahora >= self.fin_efecto_360:
            self.mostrando_360 = False

        # terminar furia
        if self.furia and ahora >= self.fin_furia:

            self.furia = False

            self.cooldown_embestida = self.cooldown_embestida_normal
            self.cooldown_360 = self.cooldown_360_normal


    # ==============================
    # INMORTALIDAD
    # ==============================

    def activar_inmortalidad(self):

        ahora = pygame.time.get_ticks()

        self.inmortal_hasta = max(
            self.inmortal_hasta,
            ahora + self.duracion_inmortalidad
        )


    def es_inmortal(self):

        return pygame.time.get_ticks() < self.inmortal_hasta


    # ==============================
    # VIDA
    # ==============================

    def recibir_dano(self):

        # segunda seguridad por si otro codigo llama este metodo directo
        if self.es_inmortal():
            return False

        self.vidas -= 1

        if self.vidas <= 0:

            self.vidas = 0
            return True

        return False


    def caer(self):

        self.caido = True
        self.progreso_revivir = 0

        self.mostrando_360 = False

        self.image = Jugador2PNG_scaled.copy()
        self.image.set_alpha(150)


    def revivir(self):

        self.caido = False
        self.progreso_revivir = 0

        self.vidas = min(2, self.max_vidas)

        self.inmortal_hasta = 0

        self.actualizar_apariencia()


    # ==============================
    # POWERUPS
    # ==============================

    def activar_powerup(self, tipo):

        if tipo == "rapid_fire":

            # para el pajaro rapid fire se transforma en furia
            self.furia = True

            self.fin_furia = (
                pygame.time.get_ticks()
                + self.duracion_furia
            )

            self.cooldown_embestida = self.cooldown_embestida_furia
            self.cooldown_360 = self.cooldown_360_furia

        elif tipo == "shield":

            self.escudo = True

        self.actualizar_apariencia()


    def actualizar_apariencia(self):

        centro = self.rect.center

        if self.escudo:
            self.image = Jugador2ShieldPNG_scaled

        else:
            self.image = Jugador2PNG_scaled

        self.rect = self.image.get_rect(center=centro)


    # ==============================
    # DASH - RSHIFT
    # ==============================

    def embestida(self, pressed_keys):

        ahora = pygame.time.get_ticks()

        if ahora - self.ultima_embestida < self.cooldown_embestida:
            return None

        direccion = Vector2(0, 0)

        if pressed_keys[K_UP]:
            direccion.y -= 1

        if pressed_keys[K_DOWN]:
            direccion.y += 1

        if pressed_keys[K_LEFT]:
            direccion.x -= 1

        if pressed_keys[K_RIGHT]:
            direccion.x += 1

        if direccion.length() == 0:
            return None

        direccion = direccion.normalize()

        posicion_inicial = self.rect.center

        self.rect.x += int(
            direccion.x * self.distancia_embestida
        )

        self.rect.y += int(
            direccion.y * self.distancia_embestida
        )

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

        posicion_final = self.rect.center

        self.ultima_embestida = ahora

        # 0.2 segundos sin recibir daño
        self.activar_inmortalidad()

        self.sonido_embestida.play()

        return posicion_inicial, posicion_final


    # ==============================
    # 360 - ENTER
    # ==============================

    def usar_360(self):

        ahora = pygame.time.get_ticks()

        if ahora - self.ultimo_360 < self.cooldown_360:
            return None

        self.ultimo_360 = ahora

        # 0.2 segundos sin recibir daño
        self.activar_inmortalidad()

        self.mostrando_360 = True

        self.inicio_efecto_360 = ahora

        self.fin_efecto_360 = (
            ahora + self.duracion_efecto_360
        )

        self.sonido_360.play()

        return Vector2(self.rect.center), self.radio_360


    def dibujar_360(self, screen):

        if not self.mostrando_360:
            return

        ahora = pygame.time.get_ticks()

        pasado = ahora - self.inicio_efecto_360

        if pasado >= self.duracion_efecto_360:
            return

        progreso = pasado / self.duracion_efecto_360

        # gira una vuelta entera
        angulo = -360 * progreso

        imagen = pygame.transform.rotate(
            self.imagen_360,
            angulo
        )

        rect = imagen.get_rect(
            center=self.rect.center
        )

        screen.blit(imagen, rect)


    def progreso_360(self):

        progreso = (
            pygame.time.get_ticks()
            - self.ultimo_360
        ) / self.cooldown_360

        return max(
            0,
            min(1, progreso)
        )