if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random
import pygame
from pygame.math import Vector2


class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, posicion, direccion, screen, velocidad=8, tamano=32):
        super().__init__()

        imagen = pygame.image.load("assets/proyectil_B.png").convert_alpha()
        self.image = pygame.transform.scale(imagen, (tamano, tamano))
        self.rect = self.image.get_rect(center=posicion)

        direccion = Vector2(direccion)

        if direccion.length() == 0:
            direccion = Vector2(1, 0)

        self.direccion = direccion.normalize()
        self.velocidad = velocidad
        self.posicion = Vector2(posicion)

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # una flecha normal lo destruye
        self.vidas = 1


    def update(self):
        self.posicion += self.direccion * self.velocidad
        self.rect.center = (round(self.posicion.x), round(self.posicion.y))

        margen = 100

        if self.rect.right < -margen or self.rect.left > self.screen_width + margen or self.rect.bottom < -margen or self.rect.top > self.screen_height + margen:
            self.kill()


    def recibir_dano(self, cantidad=1):
        self.vidas -= cantidad

        if self.vidas <= 0:
            self.kill()
            return True

        return False


class Meteorito(pygame.sprite.Sprite):
    def __init__(self, screen, x=None, velocidad=9):
        super().__init__()

        imagen = pygame.image.load("assets/meteorito.png").convert_alpha()

        tamano = random.randint(55, 85)
        self.image = pygame.transform.scale(imagen, (tamano, tamano))

        if x is None:
            x = random.randint(20, screen.get_width() - 20)

        self.rect = self.image.get_rect(center=(x, -tamano))
        self.posicion = Vector2(self.rect.center)

        self.velocidad_y = velocidad
        self.velocidad_x = random.uniform(-1.3, 1.3)

        self.screen_height = screen.get_height()

        # necesita dos de daño
        self.vidas = 2


    def update(self):
        self.posicion.x += self.velocidad_x
        self.posicion.y += self.velocidad_y

        self.rect.center = (round(self.posicion.x), round(self.posicion.y))

        if self.rect.top > self.screen_height + 80:
            self.kill()


    def recibir_dano(self, cantidad=1):
        self.vidas -= cantidad

        if self.vidas <= 0:
            self.kill()
            return True

        return False


class MiniDragon(pygame.sprite.Sprite):
    def __init__(self, screen, fase):
        super().__init__()

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        tipo = random.choices(["S", "D", "G"], weights=[55, 30, 15], k=1)[0]

        if tipo == "S":
            archivo = "assets/bug_S.png"
            tamano = 58
            self.vidas = 1

        elif tipo == "D":
            archivo = "assets/bug_D.png"
            tamano = 65
            self.vidas = 2

        else:
            archivo = "assets/bug_G.png"
            tamano = 78
            self.vidas = 4

        imagen = pygame.image.load(archivo).convert_alpha()
        self.image = pygame.transform.scale(imagen, (tamano, tamano))

        self.velocidad = 3.2 + fase * 0.5

        lado = random.choice(["arriba", "abajo", "izquierda", "derecha"])

        if lado == "arriba":
            posicion = (random.randint(0, self.screen_width), -tamano)

        elif lado == "abajo":
            posicion = (random.randint(0, self.screen_width), self.screen_height + tamano)

        elif lado == "izquierda":
            posicion = (-tamano, random.randint(0, self.screen_height))

        else:
            posicion = (self.screen_width + tamano, random.randint(0, self.screen_height))

        self.rect = self.image.get_rect(center=posicion)
        self.posicion = Vector2(posicion)


    def update(self, objetivos):
        if not objetivos:
            return

        objetivo = min(objetivos, key=lambda p: (Vector2(p) - self.posicion).length_squared())
        direccion = Vector2(objetivo) - self.posicion

        if direccion.length() > 0:
            direccion = direccion.normalize()
            self.posicion += direccion * self.velocidad
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    def recibir_dano(self, cantidad=1):
        self.vidas -= cantidad

        if self.vidas <= 0:
            self.kill()
            return True

        return False


class Boss(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()

        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.imagen_original = pygame.image.load("assets/boss.png").convert_alpha()

        self.tamano_actual = 240
        self.image = pygame.transform.scale(self.imagen_original, (240, 240))
        self.rect = self.image.get_rect(center=(self.screen_width // 2, 150))
        self.posicion = Vector2(self.rect.center)

        # VIDA
        self.max_vidas = 650
        self.vidas = self.max_vidas

        self.fase_actual = 1

        # MOVIMIENTO NORMAL
        self.velocidad_movimiento = 2.5
        self.objetivo_movimiento = Vector2(self.rect.center)
        self.proximo_cambio_movimiento = 0

        # ATAQUES
        self.ultimo_ataque = pygame.time.get_ticks()
        self.cooldown_ataque = 1250

        # ======================================
        # DASH
        # siempre va a una esquina PRIMERO
        # ======================================

        self.yendo_esquina_dash = False
        self.preparando_embestida = False
        self.en_embestida = False

        self.esquina_dash = Vector2(self.rect.center)

        self.inicio_preparacion_embestida = 0
        self.tiempo_preparacion_embestida = 350

        self.direccion_embestida = Vector2(0, 0)
        self.destino_embestida = Vector2(self.rect.center)

        self.velocidad_ir_esquina = 8
        self.velocidad_embestida = 20

        self.quieto_hasta = 0

        # evita que un dash quite 5 vidas al mismo jugador
        self.golpeados_embestida = set()

        # METEORITOS ESPECIALES
        self.fase_meteoritos = False
        self.inicio_fase_meteoritos = 0
        self.duracion_fase_meteoritos = 4000

        self.ultimo_meteorito = 0
        self.ultimo_spawn_fase = 0

        self.umbrales_meteoritos = [0.78, 0.48, 0.22]
        self.meteoritos_usados = set()

        # RAFAGAS
        self.rafagas_pendientes = 0
        self.proxima_rafaga = 0
        self.tipo_rafaga = "radial"

        # para que no sea directamente imposible
        self.max_subdragones = 10


    # ==================================================
    # FASES
    # ==================================================

    def actualizar_fase(self):
        porcentaje = self.vidas / self.max_vidas

        if porcentaje > 0.80:
            nueva_fase = 1
        elif porcentaje > 0.60:
            nueva_fase = 2
        elif porcentaje > 0.40:
            nueva_fase = 3
        elif porcentaje > 0.20:
            nueva_fase = 4
        else:
            nueva_fase = 5

        if nueva_fase != self.fase_actual:
            self.fase_actual = nueva_fase
            self._actualizar_tamano()

        cooldowns = {1: 1250, 2: 1000, 3: 800, 4: 650, 5: 500}

        self.cooldown_ataque = cooldowns[self.fase_actual]
        self.velocidad_movimiento = 2.2 + self.fase_actual * 0.8
        self.velocidad_ir_esquina = 7 + self.fase_actual


    def _actualizar_tamano(self):
        tamanos = {1: 240, 2: 225, 3: 170, 4: 135, 5: 105}

        nuevo_tamano = tamanos[self.fase_actual]

        if nuevo_tamano == self.tamano_actual:
            return

        centro = self.rect.center

        self.tamano_actual = nuevo_tamano
        self.image = pygame.transform.scale(self.imagen_original, (nuevo_tamano, nuevo_tamano))
        self.rect = self.image.get_rect(center=centro)
        self.posicion = Vector2(self.rect.center)

        if self.fase_meteoritos:
            self.image.set_alpha(0)


    # ==================================================
    # MOVIMIENTO NORMAL
    # ==================================================

    def _elegir_nuevo_punto(self):
        margen = max(70, self.rect.width // 2)

        self.objetivo_movimiento = Vector2(
            random.randint(margen, self.screen_width - margen),
            random.randint(margen, min(self.screen_height - margen, 430))
        )

        self.proximo_cambio_movimiento = pygame.time.get_ticks() + random.randint(700, 1500)


    def _mover_normal(self):
        ahora = pygame.time.get_ticks()

        if ahora < self.quieto_hasta:
            return

        distancia = self.objetivo_movimiento - self.posicion

        if distancia.length() < 20 or ahora >= self.proximo_cambio_movimiento:
            self._elegir_nuevo_punto()
            distancia = self.objetivo_movimiento - self.posicion

        if distancia.length() > 0:
            direccion = distancia.normalize()
            self.posicion += direccion * self.velocidad_movimiento
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    # ==================================================
    # DASH
    # 1) VA A UNA ESQUINA
    # 2) AVISA
    # 3) DASHEA
    # ==================================================

    def iniciar_embestida(self):
        if self.yendo_esquina_dash or self.preparando_embestida or self.en_embestida:
            return

        margen_x = self.rect.width // 2 + 15
        margen_y = self.rect.height // 2 + 15

        esquinas = [
            Vector2(margen_x, margen_y),
            Vector2(self.screen_width - margen_x, margen_y),
            Vector2(margen_x, self.screen_height - margen_y),
            Vector2(self.screen_width - margen_x, self.screen_height - margen_y)
        ]

        # no siempre elige la esquina mas cercana
        self.esquina_dash = random.choice(esquinas)
        self.yendo_esquina_dash = True

        self.golpeados_embestida.clear()


    def _actualizar_ir_esquina(self):
        distancia = self.esquina_dash - self.posicion

        if distancia.length() <= self.velocidad_ir_esquina:
            self.posicion = self.esquina_dash.copy()
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))

            self.yendo_esquina_dash = False
            self.preparando_embestida = True
            self.inicio_preparacion_embestida = pygame.time.get_ticks()

            return

        direccion = distancia.normalize()
        self.posicion += direccion * self.velocidad_ir_esquina
        self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    def _actualizar_preparacion_embestida(self, objetivos):
        ahora = pygame.time.get_ticks()

        if ahora - self.inicio_preparacion_embestida < self.tiempo_preparacion_embestida:
            return

        self._empezar_embestida_real(objetivos)


    def _empezar_embestida_real(self, objetivos):
        # normalmente apunta a un jugador, pero a veces elige otro punto
        if objetivos and random.random() < 0.78:
            objetivo = Vector2(random.choice(objetivos))

        else:
            objetivo = Vector2(
                random.randint(100, self.screen_width - 100),
                random.randint(100, self.screen_height - 100)
            )

        direccion = objetivo - self.posicion

        if direccion.length() == 0:
            direccion = Vector2(self.screen_width // 2, self.screen_height // 2) - self.posicion

        if direccion.length() == 0:
            direccion = Vector2(1, 0)

        self.direccion_embestida = direccion.normalize()

        margen_x = self.rect.width // 2
        margen_y = self.rect.height // 2

        tiempos = []

        if self.direccion_embestida.x > 0:
            t = (self.screen_width - margen_x - self.posicion.x) / self.direccion_embestida.x
            if t > 5:
                tiempos.append(t)

        elif self.direccion_embestida.x < 0:
            t = (margen_x - self.posicion.x) / self.direccion_embestida.x
            if t > 5:
                tiempos.append(t)

        if self.direccion_embestida.y > 0:
            t = (self.screen_height - margen_y - self.posicion.y) / self.direccion_embestida.y
            if t > 5:
                tiempos.append(t)

        elif self.direccion_embestida.y < 0:
            t = (margen_y - self.posicion.y) / self.direccion_embestida.y
            if t > 5:
                tiempos.append(t)

        if not tiempos:
            self.preparando_embestida = False
            return

        distancia = min(tiempos)

        self.destino_embestida = self.posicion + self.direccion_embestida * distancia
        self.velocidad_embestida = 16 + self.fase_actual * 2

        self.golpeados_embestida.clear()

        self.preparando_embestida = False
        self.en_embestida = True


    def _actualizar_embestida(self):
        distancia = self.destino_embestida - self.posicion

        if distancia.length() <= self.velocidad_embestida:
            self.posicion = self.destino_embestida.copy()
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))
            self.terminar_embestida()
            return

        direccion = distancia.normalize()
        self.posicion += direccion * self.velocidad_embestida
        self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    def terminar_embestida(self):
        self.en_embestida = False
        self.preparando_embestida = False
        self.yendo_esquina_dash = False

        # se queda EXACTAMENTE donde termino
        self.objetivo_movimiento = self.posicion.copy()
        self.quieto_hasta = pygame.time.get_ticks() + 500
        self.ultimo_ataque = pygame.time.get_ticks()


    # ==================================================
    # PROYECTILES
    # ==================================================

    def _crear_disparo(self, direccion, proyectiles, velocidad=None, tamano=32):
        if velocidad is None:
            velocidad = 7 + self.fase_actual

        proyectiles.add(BossProjectile(self.rect.center, direccion, self.screen, velocidad, tamano))


    def disparo_apuntado(self, objetivos, proyectiles):
        if not objetivos:
            return

        objetivo = random.choice(objetivos)
        direccion_base = Vector2(objetivo) - Vector2(self.rect.center)

        if direccion_base.length() == 0:
            return

        direccion_base = direccion_base.normalize()

        cantidades = {1: 3, 2: 5, 3: 7, 4: 9, 5: 11}
        cantidad = cantidades[self.fase_actual]

        separacion = 9
        centro = (cantidad - 1) / 2

        for i in range(cantidad):
            angulo = (i - centro) * separacion
            direccion = direccion_base.rotate(angulo)
            self._crear_disparo(direccion, proyectiles, 7.5 + self.fase_actual)


    def disparo_radial(self, proyectiles):
        cantidades = {1: 12, 2: 16, 3: 20, 4: 26, 5: 32}
        cantidad = cantidades[self.fase_actual]

        offset = random.uniform(0, 360 / cantidad)

        for i in range(cantidad):
            angulo = offset + 360 * i / cantidad
            direccion = Vector2(1, 0).rotate(angulo)
            self._crear_disparo(direccion, proyectiles, 6 + self.fase_actual, 28)

        if self.fase_actual >= 4:
            for i in range(cantidad):
                angulo = offset + 360 * i / cantidad + 360 / cantidad / 2
                direccion = Vector2(1, 0).rotate(angulo)
                self._crear_disparo(direccion, proyectiles, 9 + self.fase_actual, 24)


    def ataque_cruzado(self, objetivos, proyectiles):
        for angulo in range(0, 360, 45):
            direccion = Vector2(1, 0).rotate(angulo)
            self._crear_disparo(direccion, proyectiles, 11)

        self.disparo_apuntado(objetivos, proyectiles)


    # ==================================================
    # METEORITOS
    # ==================================================

    def lluvia_corta(self, objetivos, meteoritos):
        cantidad = 4 + self.fase_actual * 2

        for _ in range(cantidad):
            if objetivos and random.random() < 0.65:
                objetivo = random.choice(objetivos)
                x = int(objetivo[0] + random.randint(-130, 130))
                x = max(20, min(self.screen_width - 20, x))

            else:
                x = random.randint(20, self.screen_width - 20)

            meteoritos.add(Meteorito(self.screen, x, 7 + self.fase_actual))


    # ==================================================
    # SUBDRAGONES
    # ==================================================

    def invocar_dragones(self, subdragones):
        if len(subdragones) >= self.max_subdragones:
            return

        cantidades = {1: 1, 2: 2, 3: 3, 4: 4, 5: 6}
        cantidad = cantidades[self.fase_actual]

        for _ in range(cantidad):
            if len(subdragones) >= self.max_subdragones:
                break

            subdragones.add(MiniDragon(self.screen, self.fase_actual))


    # ==================================================
    # RAFAGAS
    # ==================================================

    def iniciar_rafaga(self, tipo):
        self.tipo_rafaga = tipo
        self.rafagas_pendientes = 3 + self.fase_actual
        self.proxima_rafaga = pygame.time.get_ticks()


    def actualizar_rafagas(self, objetivos, proyectiles):
        if self.rafagas_pendientes <= 0:
            return

        ahora = pygame.time.get_ticks()

        if ahora < self.proxima_rafaga:
            return

        if self.tipo_rafaga == "radial":
            self.disparo_radial(proyectiles)

        else:
            self.disparo_apuntado(objetivos, proyectiles)

        self.rafagas_pendientes -= 1

        intervalos = {1: 300, 2: 260, 3: 220, 4: 180, 5: 140}
        self.proxima_rafaga = ahora + intervalos[self.fase_actual]


    # ==================================================
    # FASE ESPECIAL METEORITOS
    # ==================================================

    def revisar_fase_meteoritos(self):
        if self.fase_meteoritos:
            return

        porcentaje = self.vidas / self.max_vidas

        for i, umbral in enumerate(self.umbrales_meteoritos):
            if porcentaje <= umbral and i not in self.meteoritos_usados:
                self.meteoritos_usados.add(i)
                self.iniciar_fase_meteoritos()
                return


    def iniciar_fase_meteoritos(self):
        ahora = pygame.time.get_ticks()

        self.fase_meteoritos = True
        self.inicio_fase_meteoritos = ahora

        self.ultimo_meteorito = 0
        self.ultimo_spawn_fase = 0

        self.en_embestida = False
        self.preparando_embestida = False
        self.yendo_esquina_dash = False

        self.image.set_alpha(0)


    def actualizar_fase_meteoritos(self, objetivos, meteoritos, subdragones):
        ahora = pygame.time.get_ticks()

        if ahora - self.inicio_fase_meteoritos >= self.duracion_fase_meteoritos:
            self.fase_meteoritos = False
            self.image.set_alpha(255)

            # NO TELEPORT
            # vuelve a aparecer exactamente donde estaba
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))

            self.quieto_hasta = ahora + 500
            self.ultimo_ataque = ahora

            return

        # asegurarse de que siga invisible aunque cambie de tamaño
        self.image.set_alpha(0)

        intervalo_meteorito = max(130, 270 - self.fase_actual * 25)

        if ahora - self.ultimo_meteorito >= intervalo_meteorito:
            self.ultimo_meteorito = ahora

            if objetivos and random.random() < 0.75:
                objetivo = random.choice(objetivos)
                x = int(objetivo[0] + random.randint(-150, 150))
                x = max(20, min(self.screen_width - 20, x))

            else:
                x = random.randint(20, self.screen_width - 20)

            meteoritos.add(Meteorito(self.screen, x, 8 + self.fase_actual))

        if ahora - self.ultimo_spawn_fase >= 1000:
            self.ultimo_spawn_fase = ahora
            self.invocar_dragones(subdragones)


    # ==================================================
    # ELECCION ALEATORIA DE ATAQUES
    # ==================================================

    def elegir_ataque(self, objetivos, proyectiles, meteoritos, subdragones):
        if not objetivos:
            return

        if self.fase_actual == 1:
            ataques = ["apuntado", "radial", "dash"]
            pesos = [45, 30, 25]

        elif self.fase_actual == 2:
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones"]
            pesos = [25, 20, 20, 20, 15]

        elif self.fase_actual == 3:
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones", "rafaga"]
            pesos = [18, 18, 16, 16, 14, 18]

        elif self.fase_actual == 4:
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones", "rafaga", "cruzado"]
            pesos = [12, 17, 13, 14, 14, 18, 12]

        else:
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones", "rafaga", "cruzado", "caos"]
            pesos = [10, 13, 10, 12, 13, 17, 10, 15]

        ataque = random.choices(ataques, weights=pesos, k=1)[0]

        if ataque == "apuntado":
            self.disparo_apuntado(objetivos, proyectiles)

        elif ataque == "radial":
            self.disparo_radial(proyectiles)

        elif ataque == "dash":
            # NO DASHEA TODAVIA
            # primero empieza a viajar hacia una esquina
            self.iniciar_embestida()

        elif ataque == "meteoritos":
            self.lluvia_corta(objetivos, meteoritos)

        elif ataque == "dragones":
            self.invocar_dragones(subdragones)

        elif ataque == "rafaga":
            self.iniciar_rafaga(random.choice(["radial", "apuntado"]))

        elif ataque == "cruzado":
            self.ataque_cruzado(objetivos, proyectiles)

        elif ataque == "caos":
            self.disparo_radial(proyectiles)
            self.disparo_apuntado(objetivos, proyectiles)
            self.lluvia_corta(objetivos, meteoritos)
            self.invocar_dragones(subdragones)
            self.iniciar_rafaga(random.choice(["radial", "apuntado"]))


    # ==================================================
    # UPDATE
    # ==================================================

    def update(self, objetivos, proyectiles, meteoritos, subdragones):
        self.actualizar_fase()
        self.revisar_fase_meteoritos()

        if self.fase_meteoritos:
            self.actualizar_fase_meteoritos(objetivos, meteoritos, subdragones)
            return

        # si eligio dash, PRIMERO se mueve hasta la esquina
        if self.yendo_esquina_dash:
            self._actualizar_ir_esquina()
            return

        # cuando llega a la esquina se queda avisando 0.35 s
        if self.preparando_embestida:
            self._actualizar_preparacion_embestida(objetivos)
            return

        # recien despues sale disparado
        if self.en_embestida:
            self._actualizar_embestida()
            return

        self.actualizar_rafagas(objetivos, proyectiles)
        self._mover_normal()

        ahora = pygame.time.get_ticks()

        if ahora - self.ultimo_ataque >= self.cooldown_ataque:
            self.ultimo_ataque = ahora
            self.elegir_ataque(objetivos, proyectiles, meteoritos, subdragones)


    # ==================================================
    # DAÑO
    # ==================================================

    def recibir_dano(self, cantidad=1):
        if self.fase_meteoritos:
            return False

        self.vidas -= cantidad

        if self.vidas <= 0:
            self.vidas = 0
            self.kill()
            return True

        return False


    def ajustar_pausa(self, tiempo):
        self.ultimo_ataque += tiempo
        self.proximo_cambio_movimiento += tiempo
        self.quieto_hasta += tiempo

        if self.preparando_embestida:
            self.inicio_preparacion_embestida += tiempo

        if self.rafagas_pendientes > 0:
            self.proxima_rafaga += tiempo

        if self.fase_meteoritos:
            self.inicio_fase_meteoritos += tiempo
            self.ultimo_meteorito += tiempo
            self.ultimo_spawn_fase += tiempo