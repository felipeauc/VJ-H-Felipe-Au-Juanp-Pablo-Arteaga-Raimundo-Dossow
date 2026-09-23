if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.math import Vector2

# TODO (2.1): Cargar imagen de la bala

bulletPNG = pygame.image.load("assets/bullet.png")
bulletPNG_scaled = pygame.transform.scale(bulletPNG, (26,14))

class Bullet(pygame.sprite.Sprite):
    # TODO (2.2): Agregar parametros al constructor
    def __init__(self, start_pos, direction, screen_width, screen_height):
        # ? super().__init__() inicializa la clase padre (Sprite) 
        
        super().__init__()

        # TODO (2.1): Aspecto inicial de nuestra bala
        self.image = bulletPNG_scaled
        self.rect = self.image.get_rect()

        # TODO (2.2): Posicionar la bala en la posición inicial
        self.rect.center = start_pos 

        # TODO (2.2): Variables requeridas por nuestra bala
        self.speed = 20
        self. direction = direction
        self.screen_width = screen_width
        self.screen_height = screen_height

        # TODO (3.1): Rotar la bala para que apunte en la dirección correcta
        angle = self.direction.angle_to(Vector2(1, 0))
        self.image = pygame.transform.rotate(bulletPNG_scaled, angle)
        self.rect = self.image.get_rect(center=start_pos)
        
    def update(self):
        # TODO (2.3): Mover la bala
        self.rect.move_ip(
            self.direction.x * self.speed, 
            self.direction.y * self.speed,
        )
        

        # TODO (2.3): Eliminar la bala si sale de la pantalla
        if (
            self.rect.right < 0 
            or self.rect.left > self.screen_width
            or self.rect.bottom < 0
            or self.rect.top > self.screen_height
        ):
            self.kill()
        pass
