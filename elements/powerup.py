if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random

import pygame


#---- FEATURE POWER UPS - CARGAR IMAGENES ----
RAPID_FIREpng = pygame.image.load("assets/powerup_rapid_fire.png")
RAPID_FIREpng_scaled = pygame.transform.scale(
    RAPID_FIREpng,
    (55, 55)
)

SHIELDpng = pygame.image.load("assets/powerup_shield.png")
SHIELDpng_scaled = pygame.transform.scale(
    SHIELDpng,
    (55, 55)
)
#----


#---- FEATURE POWER UPS - CREAR POWER UP ----
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, screen):

        super().__init__()

        self.tipo = random.choice([
            "rapid_fire",
            "shield",
        ])

        if self.tipo == "rapid_fire":
            self.image = RAPID_FIREpng_scaled

        elif self.tipo == "shield":
            self.image = SHIELDpng_scaled

        self.rect = self.image.get_rect(
            center=(
                random.randint(
                    80,
                    screen.get_width() - 80,
                ),
                random.randint(
                    80,
                    screen.get_height() - 80,
                ),
            )
        )
#----