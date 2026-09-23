if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random

import pygame

import customization


class Enemy(pygame.sprite.Sprite):
    def __init__(self, screen):

        # ? super().__init__() inicializa la clase padre (Sprite)
        super().__init__()

        #---- FEATURE TIENDA - SPRITE DEL ENEMIGO ----
        BUGpng = pygame.image.load(customization.obtener_asset("bug")).convert_alpha()
        BUGpng_scaled = pygame.transform.scale(BUGpng, (64, 64))
        self.image = BUGpng_scaled
        #----

        self.rect = self.image.get_rect(
            center=(
                screen.get_width() + 100,
                random.randint(self.image.get_height() // 2, screen.get_height() - self.image.get_height() // 2),
            )
        )

        self.speed = random.randint(3, 5)

    def update(self):
        # ? Mover a los enemigos
        self.rect.move_ip(-self.speed, 0)

        # ? Destruir a los enemigos
        if self.rect.right < 0:
            self.kill()