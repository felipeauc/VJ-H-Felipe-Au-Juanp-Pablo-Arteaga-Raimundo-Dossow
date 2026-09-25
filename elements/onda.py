if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame


#---- FEATURE COOPERATIVO - SPRITE ONDA EXPANSIVA ----
OndaPNG = pygame.image.load("assets/onda_expansiva.png")
#----


#---- FEATURE COOPERATIVO - ONDA EXPANSIVA ----
class OndaExpansiva(pygame.sprite.Sprite):
    def __init__(self):

        super().__init__()

        self.tiempo_carga = 240
        self.carga = 0

        self.cooldown = 900
        self.espera = 0

        self.duracion_animacion = 40
        self.animacion = 0
        self.tamano_maximo = 1400

        self.image = OndaPNG
        self.rect = self.image.get_rect()

        #---- FEATURE MUSICA Y SONIDO - SONIDO ONDA EXPANSIVA ----
        self.sonido_onda = pygame.mixer.Sound("assets/onda.wav")
        self.sonido_onda.set_volume(1.0)
        #----

    def update(self, cargando, centro):

        if self.animacion > 0:

            self.animacion -= 1

            avance = 1 - self.animacion / self.duracion_animacion
            tamano = int(self.tamano_maximo * avance) + 1

            self.image = pygame.transform.scale(OndaPNG, (tamano, tamano))
            self.image.set_alpha(int(255 * (1 - avance)))
            self.rect = self.image.get_rect(center=self.rect.center)

        if self.espera > 0:

            self.espera -= 1
            self.carga = 0

            return False

        if cargando:
            self.carga += 1

        else:
            self.carga = 0

        if self.carga >= self.tiempo_carga:

            self.carga = 0
            self.espera = self.cooldown
            self.animacion = self.duracion_animacion

            self.image = pygame.transform.scale(OndaPNG, (1, 1))
            self.rect = self.image.get_rect(center=centro)

            self.sonido_onda.play()

            return True

        return False
#----
