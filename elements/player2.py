if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_DOWN, K_LEFT, K_RIGHT, K_UP
from pygame.math import Vector2

#---- FEATURE COOPERATIVO - SPRITE DEL JUGADOR 2 ----
Jugador2PNG = pygame.image.load("assets/jugador2.png")
Jugador2PNG_scaled = pygame.transform.scale(Jugador2PNG, (80, 80))
#----

class Player2(pygame.sprite.Sprite):
    def __init__(self, screen):

        # ? super().__init__() inicializa la clase padre (Sprite)
        super().__init__()

        self.image = Jugador2PNG_scaled
        self.rect = self.image.get_rect(center=(100, screen.get_height() // 2))

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.velocidad = 4

        #---- FEATURE COOPERATIVO - VIDAS JUGADOR 2 ----
        self.vidas = 5
        self.max_vidas = 5
        #----

        #---- FEATURE VIDAS DEL JUGADOR - EMBESTIR ----
        self.distancia_embestida = 220
        self.cooldown_embestida = 2500
        self.ultima_embestida = -self.cooldown_embestida

        self.sonido_embestida = pygame.mixer.Sound("assets/dash.wav")
        self.sonido_embestida.set_volume(0.70)
        #----   

    def update(self, pressed_keys):

        # ? Mover al Jugador 2
        if pressed_keys[K_UP]:
            self.rect.move_ip(0, -self.velocidad)

        if pressed_keys[K_DOWN]:
            self.rect.move_ip(0, self.velocidad)

        if pressed_keys[K_LEFT]:
            self.rect.move_ip(-self.velocidad, 0)

        if pressed_keys[K_RIGHT]:
            self.rect.move_ip(self.velocidad, 0)

        # ? Mantener al Jugador 2 en Pantalla
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

    #---- FEATURE COOPERATIVO - RECIBIR DAÑO JUGADOR 2 ----
    def recibir_dano(self):

        self.vidas -= 1

        if self.vidas <= 0:
            return True

        return False

    #---- FEATURE COOPERATIVO - EMBESTIR ----
    def embestida(self, pressed_keys):

        ahora = pygame.time.get_ticks()
        if ahora - self.ultima_embestida < self.cooldown_embestida:
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

        if direccion_x == 0 and direccion_y == 0:
            return None 

        direccion = Vector2(direccion_x, direccion_y).normalize()
        posicion_inicial = self.rect.center

        self.rect.x += int(direccion.x * self.distancia_embestida)
        self.rect.y += int(direccion.y * self.distancia_embestida) 

        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, self.screen_width)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, self.screen_height)

        posicion_final = self.rect.center
        self.ultima_embestida = ahora

        self.sonido_embestida.play()

        return posicion_inicial, posicion_final
    #----    

