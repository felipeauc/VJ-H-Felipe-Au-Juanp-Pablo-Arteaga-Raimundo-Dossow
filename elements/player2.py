if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_UP
from pygame.math import Vector2

import habilidades


# jugador 2
Jugador2PNG = pygame.image.load("assets/jugador2.png")
Jugador2PNG_scaled = pygame.transform.scale(Jugador2PNG, (80, 80))


# player2 con shield
Jugador2ShieldPNG = pygame.image.load("assets/jugador2_shield.png")
Jugador2ShieldPNG_scaled = pygame.transform.scale(Jugador2ShieldPNG, (80, 80))


class Player2(pygame.sprite.Sprite):
    def __init__(self, screen):

        super().__init__()

        self.image = Jugador2PNG_scaled
        self.rect = self.image.get_rect(
            midleft=(0, screen.get_height() // 2)
        )

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.velocidad = 7


        # vidas, usa la mejora comprada en tienda
        self.max_vidas = habilidades.vida_maxima()
        self.vidas = self.max_vidas


        # estado caido coop
        self.caido = False
        self.progreso_revivir = 0


        # embestida
        self.distancia_embestida = 220

        self.cooldown_embestida = 2000
        self.ultima_embestida = -self.cooldown_embestida


        self.sonido_embestida = pygame.mixer.Sound(
            "assets/dash.wav"
        )

        self.sonido_embestida.set_volume(0.70)


        # power ups
        self.escudo = False

        self.furia = False

        self.duracion_furia = 7000
        self.fin_furia = 0

        self.cooldown_normal = self.cooldown_embestida
        self.cooldown_furia = 400


    def update(self, pressed_keys):

        # mover player 2
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.velocidad)

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.velocidad)

        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.velocidad, 0)

        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.velocidad, 0)


        # no salir de pantalla
        self.rect.left = max(
            self.rect.left,
            0
        )

        self.rect.right = min(
            self.rect.right,
            self.screen_width
        )

        self.rect.top = max(
            self.rect.top,
            0
        )

        self.rect.bottom = min(
            self.rect.bottom,
            self.screen_height
        )


        # termina furia
        if self.furia:

            if pygame.time.get_ticks() >= self.fin_furia:

                self.furia = False

                self.cooldown_embestida = self.cooldown_normal


    # daño
    def recibir_dano(self):

        self.vidas -= 1


        if self.vidas <= 0:

            self.vidas = 0

            return True


        return False


    # cae en coop
    def caer(self):

        self.caido = True

        self.progreso_revivir = 0


        self.image = Jugador2PNG_scaled.copy()

        self.image.set_alpha(
            150
        )


    # revivirlo
    def revivir(self):

        self.caido = False

        self.progreso_revivir = 0


        self.vidas = min(
            2,
            self.max_vidas
        )


        self.actualizar_apariencia()


    # power up del pato
    def activar_powerup(self, tipo):

        if tipo == "rapid_fire":

            # como no dispara, rapid se convierte en furia de embestida
            self.furia = True

            self.fin_furia = (
                pygame.time.get_ticks()
                + self.duracion_furia
            )

            self.cooldown_embestida = self.cooldown_furia


        elif tipo == "shield":

            self.escudo = True


        self.actualizar_apariencia()


    # imagen shield / normal
    def actualizar_apariencia(self):

        centro = self.rect.center


        if self.escudo:

            self.image = Jugador2ShieldPNG_scaled


        else:

            self.image = Jugador2PNG_scaled


        self.rect = self.image.get_rect(
            center=centro
        )


    # habilidad player 2
    def embestida(self, pressed_keys):

        ahora = pygame.time.get_ticks()


        if (
            ahora - self.ultima_embestida
            < self.cooldown_embestida
        ):

            return None


        direccion_x = 0
        direccion_y = 0


        if pressed_keys[K_UP]:
            direccion_y -= 1

        if pressed_keys[K_DOWN]:
            direccion_y += 1

        if pressed_keys[K_LEFT]:
            direccion_x -= 1

        if pressed_keys[K_RIGHT]:
            direccion_x += 1


        if (
            direccion_x == 0
            and direccion_y == 0
        ):

            return None


        direccion = Vector2(
            direccion_x,
            direccion_y
        ).normalize()


        posicion_inicial = self.rect.center


        self.rect.x += int(
            direccion.x
            * self.distancia_embestida
        )

        self.rect.y += int(
            direccion.y
            * self.distancia_embestida
        )


        self.rect.left = max(
            self.rect.left,
            0
        )

        self.rect.right = min(
            self.rect.right,
            self.screen_width
        )

        self.rect.top = max(
            self.rect.top,
            0
        )

        self.rect.bottom = min(
            self.rect.bottom,
            self.screen_height
        )


        posicion_final = self.rect.center


        self.ultima_embestida = ahora


        self.sonido_embestida.play()


        return (
            posicion_inicial,
            posicion_final
        )