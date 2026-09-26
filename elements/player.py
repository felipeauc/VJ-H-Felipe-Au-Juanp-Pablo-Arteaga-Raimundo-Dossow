if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_a, K_d, K_s, K_w, K_LSHIFT
from pygame.math import Vector2

import habilidades
import robo_vida

from .bullet import Bullet


JorgePNG = pygame.image.load("assets/jorge.png")
JorgeShieldPNG = pygame.image.load("assets/jorge_shield.png")
JorgeRapidPNG = pygame.image.load("assets/jorge_rapid.png")
JorgeShieldRapidPNG = pygame.image.load("assets/jorge_shield_rapid.png")

JorgeReloadPNG = pygame.image.load("assets/jorge_reload.png")
JorgeReloadShieldPNG = pygame.image.load("assets/jorge_reload_shield.png")
JorgeReloadRapidPNG = pygame.image.load("assets/jorge_reload_rapid.png")
JorgeReloadShieldRapidPNG = pygame.image.load("assets/jorge_reload_shield_rapid.png")

JorgeSprintPNG = pygame.image.load("assets/jorge_sprint.png")
JorgeShieldSprintPNG = pygame.image.load("assets/jorge_shield_sprint.png")
JorgeRapidSprintPNG = pygame.image.load("assets/jorge_rapid_sprint.png")
JorgeShieldRapidSprintPNG = pygame.image.load("assets/jorge_shield_rapid_sprint.png")


class Player(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # mejora de tamaño
        self.escala = habilidades.escala_jugador()
        self.tamano = max(40, round(80 * self.escala))

        # escalamos UNA sola vez al crear jugador
        self.sprites = {
            "normal": pygame.transform.scale(JorgePNG, (self.tamano, self.tamano)),
            "shield": pygame.transform.scale(JorgeShieldPNG, (self.tamano, self.tamano)),
            "rapid": pygame.transform.scale(JorgeRapidPNG, (self.tamano, self.tamano)),
            "shield_rapid": pygame.transform.scale(JorgeShieldRapidPNG, (self.tamano, self.tamano)),
            "reload": pygame.transform.scale(JorgeReloadPNG, (self.tamano, self.tamano)),
            "reload_shield": pygame.transform.scale(JorgeReloadShieldPNG, (self.tamano, self.tamano)),
            "reload_rapid": pygame.transform.scale(JorgeReloadRapidPNG, (self.tamano, self.tamano)),
            "reload_shield_rapid": pygame.transform.scale(JorgeReloadShieldRapidPNG, (self.tamano, self.tamano)),
            "sprint": pygame.transform.scale(JorgeSprintPNG, (self.tamano, self.tamano)),
            "shield_sprint": pygame.transform.scale(JorgeShieldSprintPNG, (self.tamano, self.tamano)),
            "rapid_sprint": pygame.transform.scale(JorgeRapidSprintPNG, (self.tamano, self.tamano)),
            "shield_rapid_sprint": pygame.transform.scale(JorgeShieldRapidSprintPNG, (self.tamano, self.tamano)),
        }

        self.image = self.sprites["normal"]
        self.rect = self.image.get_rect()

        self.bullets = pygame.sprite.Group()

        # mejoras
        self.disparos = 0
        self.max_disparos = habilidades.municion_maxima()

        self.sobrecalentado = False
        self.inicio_sobrecalentamiento = 0
        self.tiempo_sobrecalentamiento = habilidades.tiempo_recarga()

        self.max_vidas = habilidades.vida_maxima()
        self.vidas = self.max_vidas

        # robo de vida
        robo_vida.registrar_jugador(self)

        # coop
        self.caido = False
        self.progreso_revivir = 0

        # rapid fire
        self.rapid_fire = False
        self.duracion_rapid_fire = 7000
        self.fin_rapid_fire = 0
        self.ultimo_disparo_rapid_fire = 0
        self.cooldown_rapid_fire = 100

        self.escudo = False

        # movimiento
        self.velocidad_normal = 4
        self.velocidad_rapida = 6
        self.sprint = False

        # slow
        self.fin_slow = 0
        self.factor_slow = 0.5

        # dash
        self.distancia_dash = 140
        self.cooldown_dash = 1500
        self.ultimo_dash = -self.cooldown_dash

        # sonidos
        self.sonido_disparo = pygame.mixer.Sound("assets/arrow.wav")
        self.sonido_dash = pygame.mixer.Sound("assets/dash.wav")

        self.sonido_disparo.set_volume(0.55)
        self.sonido_dash.set_volume(0.70)


    def update(self, pressed_keys):
        moviendose = pressed_keys[K_w] or pressed_keys[K_s] or pressed_keys[K_a] or pressed_keys[K_d]
        self.sprint = pressed_keys[K_LSHIFT] and moviendose and not self.sobrecalentado

        velocidad = self.velocidad_rapida if self.sprint else self.velocidad_normal

        if pygame.time.get_ticks() < self.fin_slow:
            velocidad = max(1, int(velocidad * self.factor_slow))

        if pressed_keys[K_w]:
            self.rect.move_ip(0, -velocidad)

        if pressed_keys[K_s]:
            self.rect.move_ip(0, velocidad)

        if pressed_keys[K_a]:
            self.rect.move_ip(-velocidad, 0)

        if pressed_keys[K_d]:
            self.rect.move_ip(velocidad, 0)

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

        self.bullets.update()

        ahora = pygame.time.get_ticks()

        if self.sobrecalentado and ahora - self.inicio_sobrecalentamiento >= self.tiempo_sobrecalentamiento:
            self.sobrecalentado = False
            self.disparos = 0

        if self.rapid_fire and ahora >= self.fin_rapid_fire:
            self.rapid_fire = False
            self.disparos = 0
            self.sobrecalentado = False

        self.actualizar_apariencia()


    def shoot(self, mouse_pos):
        if self.rapid_fire:
            ahora = pygame.time.get_ticks()

            if ahora - self.ultimo_disparo_rapid_fire < self.cooldown_rapid_fire:
                return

            self.ultimo_disparo_rapid_fire = ahora

        elif self.sobrecalentado:
            return

        distance = Vector2(mouse_pos) - Vector2(self.rect.center)

        if distance.length() == 0:
            return

        direction = distance.normalize()

        bullet = Bullet(self.rect.center, direction, self.screen_width, self.screen_height, self.rapid_fire)
        self.bullets.add(bullet)

        self.sonido_disparo.play()

        if not self.rapid_fire:
            self.disparos += 1

            if self.disparos >= self.max_disparos:
                self.sobrecalentado = True
                self.inicio_sobrecalentamiento = pygame.time.get_ticks()


    def recibir_dano(self):
        self.vidas -= 1

        if self.vidas <= 0:
            self.vidas = 0
            return True

        return False


    def caer(self):
        self.caido = True
        self.progreso_revivir = 0

        self.image = self.image.copy()
        self.image.set_alpha(150)


    def revivir(self):
        self.caido = False
        self.progreso_revivir = 0
        self.vidas = min(2, self.max_vidas)

        self.actualizar_apariencia()


    def activar_powerup(self, tipo):
        if tipo == "rapid_fire":
            self.rapid_fire = True
            self.fin_rapid_fire = pygame.time.get_ticks() + self.duracion_rapid_fire
            self.sobrecalentado = False
            self.disparos = 0

        elif tipo == "shield":
            self.escudo = True

        self.actualizar_apariencia()


    def actualizar_apariencia(self):
        centro = self.rect.center

        if self.sobrecalentado and self.escudo and self.rapid_fire:
            self.image = self.sprites["reload_shield_rapid"]

        elif self.sobrecalentado and self.escudo:
            self.image = self.sprites["reload_shield"]

        elif self.sobrecalentado and self.rapid_fire:
            self.image = self.sprites["reload_rapid"]

        elif self.sobrecalentado:
            self.image = self.sprites["reload"]

        elif self.escudo and self.rapid_fire and self.sprint:
            self.image = self.sprites["shield_rapid_sprint"]

        elif self.escudo and self.rapid_fire:
            self.image = self.sprites["shield_rapid"]

        elif self.rapid_fire and self.sprint:
            self.image = self.sprites["rapid_sprint"]

        elif self.rapid_fire:
            self.image = self.sprites["rapid"]

        elif self.escudo and self.sprint:
            self.image = self.sprites["shield_sprint"]

        elif self.escudo:
            self.image = self.sprites["shield"]

        elif self.sprint:
            self.image = self.sprites["sprint"]

        else:
            self.image = self.sprites["normal"]

        self.rect = self.image.get_rect(center=centro)


    def dash(self, pressed_keys):
        ahora = pygame.time.get_ticks()

        if ahora - self.ultimo_dash < self.cooldown_dash:
            return None

        direccion_x = 0
        direccion_y = 0

        if pressed_keys[K_w]:
            direccion_y -= 1

        if pressed_keys[K_s]:
            direccion_y += 1

        if pressed_keys[K_a]:
            direccion_x -= 1

        if pressed_keys[K_d]:
            direccion_x += 1

        if direccion_x == 0 and direccion_y == 0:
            return None

        direccion = Vector2(direccion_x, direccion_y).normalize()
        posicion_inicial = self.rect.center

        self.rect.x += int(direccion.x * self.distancia_dash)
        self.rect.y += int(direccion.y * self.distancia_dash)

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

        posicion_final = self.rect.center

        self.ultimo_dash = ahora
        self.sonido_dash.play()

        return posicion_inicial, posicion_final


    def aplicar_slow(self):
        self.fin_slow = pygame.time.get_ticks() + 2500