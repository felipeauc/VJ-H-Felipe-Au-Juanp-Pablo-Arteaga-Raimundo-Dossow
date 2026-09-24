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
from .crosshair import Crosshair
from .enemy import Enemy

#---- FEATURE PROGRESION DE NIVELES - ENEMIGO NIVEL 2 ----
from .enemy_level2 import EnemyLevel2
#----

from .enemy_projectile import EnemyProjectile

from .player import Player

#---- FEATURE POWER UPS - IMPORTAR POWER UP ----
from .powerup import PowerUp
#----

#---- FEATURE COOPERATIVO - IMPORTAR JUGADOR 2 ----
from .player2 import Player2
#----

# ? Para agregar mas elementos, solo hay que importarlos y agregarlos a la lista __all__.
# ? from .nombre_del_archivo import NombreDeLaClase

#---- FEATURE POWER UPS - AGREGAR POWER UP A ELEMENTS ----
__all__ = ["Bullet", "Crosshair", "Enemy", "EnemyLevel2", "EnemyProjectile", "Player", "PowerUp", "Player2"]
#----