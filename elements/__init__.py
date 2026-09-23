"""Modulo que contiene todos los elementos del juego, como el jugador, los enemigos y las balas."""

"""
? Este archivo solo existe para que se pueda importar el modulo elements de manera más limpia.
? En lugar de tener que hacer
?
?     from elements.player import Player
?     from elements.enemy import Enemy
?     from elements.bullet import Bullet
?
? podemos hacer
?
?     from elements import Player, Enemy, Bullet
?
? lo cual es mucho mas limpio, en especial si tuvieramos muchos mas elementos (VJ-Honors?)
"""

from .bullet import Bullet
from .enemy import Enemy
from .player import Player

# ? Para agregar mas elementos, solo hay que importarlos y agregarlos a la lista __all__.
# ? from .nombre_del_archivo import NombreDeLaClase

__all__ = ["Bullet", "Enemy", "Player"]
