if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_a, K_d, K_s, K_w, K_LSHIFT, K_RSHIFT
from pygame.math import Vector2

from .bullet import Bullet


JorgePNG = pygame.image.load("assets/jorge.png")
JorgePNG_scaled = pygame.transform.scale(JorgePNG, (80, 80))

#---- FEATURE POWER UPS - CARGAR SPRITES DE ESTADO ----
JorgeShieldPNG = pygame.image.load("assets/jorge_shield.png")
JorgeShieldPNG_scaled = pygame.transform.scale(JorgeShieldPNG, (80, 80))

JorgeRapidPNG = pygame.image.load("assets/jorge_rapid.png")
JorgeRapidPNG_scaled = pygame.transform.scale(JorgeRapidPNG, (80, 80))

JorgeShieldRapidPNG = pygame.image.load("assets/jorge_shield_rapid.png")
JorgeShieldRapidPNG_scaled = pygame.transform.scale(JorgeShieldRapidPNG, (80, 80))

JorgeReloadPNG = pygame.image.load("assets/jorge_reload.png")
JorgeReloadPNG_scaled = pygame.transform.scale(JorgeReloadPNG, (80, 80))

JorgeReloadShieldPNG = pygame.image.load("assets/jorge_reload_shield.png")
JorgeReloadShieldPNG_scaled = pygame.transform.scale(JorgeReloadShieldPNG, (80, 80))

JorgeReloadRapidPNG = pygame.image.load("assets/jorge_reload_rapid.png")
JorgeReloadRapidPNG_scaled = pygame.transform.scale(JorgeReloadRapidPNG, (80, 80))

JorgeReloadShieldRapidPNG = pygame.image.load("assets/jorge_reload_shield_rapid.png")
JorgeReloadShieldRapidPNG_scaled = pygame.transform.scale(JorgeReloadShieldRapidPNG, (80, 80))
#----

#---- FEATURE HABILIDAD ESPECIAL - SPRITES DE SPRINT ----
JorgeSprintPNG = pygame.image.load("assets/jorge_sprint.png")
JorgeSprintPNG_scaled = pygame.transform.scale(JorgeSprintPNG, (80, 80))

JorgeShieldSprintPNG = pygame.image.load("assets/jorge_shield_sprint.png")
JorgeShieldSprintPNG_scaled = pygame.transform.scale(JorgeShieldSprintPNG, (80, 80))

JorgeRapidSprintPNG = pygame.image.load("assets/jorge_rapid_sprint.png")
JorgeRapidSprintPNG_scaled = pygame.transform.scale(JorgeRapidSprintPNG, (80, 80))

JorgeShieldRapidSprintPNG = pygame.image.load("assets/jorge_shield_rapid_sprint.png")
JorgeShieldRapidSprintPNG_scaled = pygame.transform.scale(JorgeShieldRapidSprintPNG, (80, 80))
#----


class Player(pygame.sprite.Sprite):
    def __init__(self, screen):

        # ? super().__init__() inicializa la clase padre (Sprite)
        super().__init__()

        self.image = JorgePNG_scaled
        self.rect = self.image.get_rect()

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # TODO (2.4): Crear grupo de balas
        self.bullets = pygame.sprite.Group()

        # Sobrecalentamiento del arma
        self.disparos = 0
        self.max_disparos = 5
        self.sobrecalentado = False
        self.inicio_sobrecalentamiento = 0
        self.tiempo_sobrecalentamiento = 3000

        #---- FEATURE VIDAS DEL JUGADOR - 5 CORAZONES ----
        self.vidas = 5
        self.max_vidas = 5
        #----

        #---- FEATURE POWER UPS - RAPID FIRE ----
        self.rapid_fire = False
        self.duracion_rapid_fire = 7000
        self.fin_rapid_fire = 0
        self.ultimo_disparo_rapid_fire = 0
        self.cooldown_rapid_fire = 100
        #----

        #---- FEATURE POWER UPS - ESCUDO ----
        self.escudo = False
        #----

        #---- FEATURE HABILIDAD ESPECIAL - VELOCIDAD CON SHIFT ----
        self.velocidad_normal = 4
        self.velocidad_rapida = 6
        self.sprint = False
        #----

        #---- FEATURE NUEVOS ENEMIGOS - SLOW BUG M ----
        self.fin_slow = 0
        self.factor_slow = 0.5
        #----

        #---- FEATURE HABILIDAD ESPECIAL - VARIABLES DASH ----
        self.distancia_dash = 140
        self.cooldown_dash = 1500
        self.ultimo_dash = -self.cooldown_dash
        #----

        #---- FEATURE MUSICA Y SONIDO - SONIDOS DEL JUGADOR ----
        self.sonido_disparo = pygame.mixer.Sound("assets/arrow.wav")
        self.sonido_dash = pygame.mixer.Sound("assets/dash.wav")

        self.sonido_disparo.set_volume(0.55)
        self.sonido_dash.set_volume(0.70)
        #----

    def update(self, pressed_keys):

        #---- FEATURE HABILIDAD ESPECIAL - VELOCIDAD CON SHIFT ----
        moviendose = pressed_keys[K_w] or pressed_keys[K_s] or pressed_keys[K_a] or pressed_keys[K_d]
        shift = pressed_keys[K_LSHIFT]

        self.sprint = shift and moviendose and not self.sobrecalentado

        if self.sprint:
            velocidad = self.velocidad_rapida

        else:
            velocidad = self.velocidad_normal
        #----

        #---- FEATURE NUEVOS ENEMIGOS - APLICAR SLOW ----
        if pygame.time.get_ticks() < self.fin_slow:
            velocidad = int(velocidad * self.factor_slow)
        #----

        # ? Mover a Jorge
        if pressed_keys[K_w]:
            self.rect.move_ip(0, -velocidad)

        if pressed_keys[K_s]:
            self.rect.move_ip(0, velocidad)

        if pressed_keys[K_a]:
            self.rect.move_ip(-velocidad, 0)

        if pressed_keys[K_d]:
            self.rect.move_ip(velocidad, 0)

        # ? Mantener a Jorge en Pantalla
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

        # TODO (2.4): Actualizar las balas
        self.bullets.update()

        ahora = pygame.time.get_ticks()

        if self.sobrecalentado:
            if ahora - self.inicio_sobrecalentamiento >= self.tiempo_sobrecalentamiento:
                self.sobrecalentado = False
                self.disparos = 0

        #---- FEATURE POWER UPS - TERMINAR RAPID FIRE ----
        if self.rapid_fire:
            if ahora >= self.fin_rapid_fire:
                self.rapid_fire = False
                self.disparos = 0
                self.sobrecalentado = False
        #----

        #---- FEATURE POWER UPS - ACTUALIZAR SPRITE DEL JUGADOR ----
        self.actualizar_apariencia()
        #----

    def shoot(self, mouse_pos):

        #---- FEATURE POWER UPS - RAPID FIRE ----
        if self.rapid_fire:

            ahora = pygame.time.get_ticks()

            if ahora - self.ultimo_disparo_rapid_fire < self.cooldown_rapid_fire:
                return

            self.ultimo_disparo_rapid_fire = ahora

        else:

            if self.sobrecalentado:
                return
        #----

        # TODO (2.4): Calcular direccion de la bala
        distance = Vector2(mouse_pos) - Vector2(self.rect.center)

        if distance.length() == 0:
            return

        direction = distance.normalize()

        # TODO (2.4): Crear bala y agregarla al grupo de balas
        bullet = Bullet(self.rect.center, direction, self.screen_width, self.screen_height, self.rapid_fire)
        self.bullets.add(bullet)

        #---- FEATURE MUSICA Y SONIDO - SONIDO DE DISPARO ----
        self.sonido_disparo.play()
        #----

        #---- FEATURE POWER UPS - RAPID FIRE SIN SOBRECALENTAMIENTO ----
        if not self.rapid_fire:

            self.disparos += 1

            if self.disparos >= self.max_disparos:
                self.sobrecalentado = True
                self.inicio_sobrecalentamiento = pygame.time.get_ticks()
        #----

        pass

    #---- FEATURE VIDAS DEL JUGADOR - RECIBIR DAÑO ----
    def recibir_dano(self):

        self.vidas -= 1

        if self.vidas <= 0:
            return True

        return False
    #----

    #---- FEATURE POWER UPS - ACTIVAR POWER UP ----
    def activar_powerup(self, tipo):

        if tipo == "rapid_fire":
            self.rapid_fire = True
            self.fin_rapid_fire = pygame.time.get_ticks() + self.duracion_rapid_fire
            self.sobrecalentado = False
            self.disparos = 0

        elif tipo == "shield":
            self.escudo = True

        self.actualizar_apariencia()
    #----

    #---- FEATURE POWER UPS - CAMBIAR APARIENCIA DEL JUGADOR ----
    def actualizar_apariencia(self):

        centro = self.rect.center

        if self.sobrecalentado and self.escudo and self.rapid_fire:
            self.image = JorgeReloadShieldRapidPNG_scaled

        elif self.sobrecalentado and self.escudo:
            self.image = JorgeReloadShieldPNG_scaled

        elif self.sobrecalentado and self.rapid_fire:
            self.image = JorgeReloadRapidPNG_scaled

        elif self.sobrecalentado:
            self.image = JorgeReloadPNG_scaled

        elif self.escudo and self.rapid_fire and self.sprint:
            self.image = JorgeShieldRapidSprintPNG_scaled

        elif self.escudo and self.rapid_fire:
            self.image = JorgeShieldRapidPNG_scaled

        elif self.rapid_fire and self.sprint:
            self.image = JorgeRapidSprintPNG_scaled

        elif self.rapid_fire:
            self.image = JorgeRapidPNG_scaled

        elif self.escudo and self.sprint:
            self.image = JorgeShieldSprintPNG_scaled

        elif self.escudo:
            self.image = JorgeShieldPNG_scaled

        elif self.sprint:
            self.image = JorgeSprintPNG_scaled

        else:
            self.image = JorgePNG_scaled

        self.rect = self.image.get_rect(center=centro)
    #----

    #---- FEATURE HABILIDAD ESPECIAL - DASH ----
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

        #---- FEATURE MUSICA Y SONIDO - SONIDO DASH ----
        self.sonido_dash.play()
        #----

        return posicion_inicial, posicion_final
    #----
    
    #---- FEATURE NUEVOS ENEMIGOS - RECIBIR SLOW ----      
    def aplicar_slow(self):

        self.fin_slow = pygame.time.get_ticks() + 2500
    #----