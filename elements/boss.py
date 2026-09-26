if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import random
import pygame
from pygame.math import Vector2

import robo_vida


_cache_originales = {}
_cache_escaladas = {}


def imagen_original(archivo):
    if archivo not in _cache_originales:
        _cache_originales[archivo] = pygame.image.load(archivo).convert_alpha()

    return _cache_originales[archivo]


def imagen_escalada(archivo, tamano):
    clave = (archivo, tamano)

    if clave not in _cache_escaladas:
        _cache_escaladas[clave] = pygame.transform.scale(imagen_original(archivo), (tamano, tamano))

    return _cache_escaladas[clave]


class BossProjectile(pygame.sprite.Sprite):
    def __init__(self, posicion, direccion, screen, velocidad=8, tamano=32):
        super().__init__()

        self.image = imagen_escalada("assets/proyectil_B.png", tamano)
        self.rect = self.image.get_rect(center=posicion)

        direccion = Vector2(direccion)

        if direccion.length() == 0:
            direccion = Vector2(1, 0)

        self.direccion = direccion.normalize()
        self.velocidad = velocidad
        self.posicion = Vector2(posicion)

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        self.vidas = 1


    def update(self):
        self.posicion += self.direccion * self.velocidad
        self.rect.center = (round(self.posicion.x), round(self.posicion.y))

        margen = 70

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

        tamano = random.choice([56, 68, 80])

        self.image = imagen_escalada("assets/meteorito.png", tamano)

        if x is None:
            x = random.randint(20, screen.get_width() - 20)

        self.rect = self.image.get_rect(center=(x, -tamano))
        self.posicion = Vector2(self.rect.center)

        self.velocidad_y = velocidad
        self.velocidad_x = random.uniform(-1.0, 1.0)

        self.screen_height = screen.get_height()

        self.vidas = 2


    def update(self):
        self.posicion.x += self.velocidad_x
        self.posicion.y += self.velocidad_y

        self.rect.center = (round(self.posicion.x), round(self.posicion.y))

        if self.rect.top > self.screen_height + 60:
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
            self.vidas = 5

        self.image = imagen_escalada(archivo, tamano)

        self.velocidad = 3.0 + fase * 0.35

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
            self.posicion += direccion.normalize() * self.velocidad
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    def recibir_dano(self, cantidad=1):
        self.vidas -= cantidad

        if self.vidas <= 0:
            self.vidas = 0

            robo_vida.registrar_muerte()

            self.kill()

            return True

        return False


class Boss(pygame.sprite.Sprite):
    def __init__(self, screen):
        super().__init__()

        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # calentamos cache al inicio del boss y no durante fase 3
        for tamano in [24, 28, 32]:
            imagen_escalada("assets/proyectil_B.png", tamano)

        for tamano in [56, 68, 80]:
            imagen_escalada("assets/meteorito.png", tamano)

        imagen_escalada("assets/bug_S.png", 58)
        imagen_escalada("assets/bug_D.png", 65)
        imagen_escalada("assets/bug_G.png", 78)

        self.imagen_original = imagen_original("assets/boss.png")

        self.tamano_actual = 240
        self.image = pygame.transform.scale(self.imagen_original, (240, 240))
        self.rect = self.image.get_rect(center=(self.screen_width // 2, 150))
        self.posicion = Vector2(self.rect.center)

        self.max_vidas = 650
        self.vidas = self.max_vidas

        self.fase_actual = 1

        self.velocidad_movimiento = 2.5
        self.objetivo_movimiento = Vector2(self.rect.center)
        self.proximo_cambio_movimiento = 0

        self.ultimo_ataque = pygame.time.get_ticks()
        self.cooldown_ataque = 1350

        # dash
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
        self.golpeados_embestida = set()

        # meteoritos especiales
        self.fase_meteoritos = False
        self.inicio_fase_meteoritos = 0
        self.duracion_fase_meteoritos = 3200

        self.ultimo_meteorito = 0
        self.ultimo_spawn_fase = 0

        self.umbrales_meteoritos = [0.75, 0.45, 0.20]
        self.meteoritos_usados = set()

        # rafagas
        self.rafagas_pendientes = 0
        self.proxima_rafaga = 0
        self.tipo_rafaga = "radial"

        self.limite_proyectiles = {1: 40, 2: 55, 3: 70, 4: 90, 5: 110}
        self.limite_meteoritos = {1: 6, 2: 8, 3: 10, 4: 12, 5: 14}
        self.limite_subdragones = {1: 2, 2: 3, 3: 4, 4: 6, 5: 8}


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

        cooldowns = {1: 1350, 2: 1150, 3: 1000, 4: 800, 5: 650}

        self.cooldown_ataque = cooldowns[self.fase_actual]
        self.velocidad_movimiento = 2.0 + self.fase_actual * 0.65
        self.velocidad_ir_esquina = 7 + self.fase_actual


    def _actualizar_tamano(self):
        tamanos = {1: 240, 2: 220, 3: 175, 4: 140, 5: 110}

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


    def _elegir_nuevo_punto(self):
        margen = max(70, self.rect.width // 2)

        self.objetivo_movimiento = Vector2(random.randint(margen, self.screen_width - margen), random.randint(margen, min(self.screen_height - margen, 430)))
        self.proximo_cambio_movimiento = pygame.time.get_ticks() + random.randint(800, 1500)


    def _mover_normal(self):
        ahora = pygame.time.get_ticks()

        if ahora < self.quieto_hasta:
            return

        distancia = self.objetivo_movimiento - self.posicion

        if distancia.length() < 20 or ahora >= self.proximo_cambio_movimiento:
            self._elegir_nuevo_punto()
            distancia = self.objetivo_movimiento - self.posicion

        if distancia.length() > 0:
            self.posicion += distancia.normalize() * self.velocidad_movimiento
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    # primero viaja fisicamente a una esquina
    def iniciar_embestida(self):
        if self.yendo_esquina_dash or self.preparando_embestida or self.en_embestida:
            return

        margen_x = self.rect.width // 2 + 15
        margen_y = self.rect.height // 2 + 15

        esquinas = [
            Vector2(margen_x, margen_y),
            Vector2(self.screen_width - margen_x, margen_y),
            Vector2(margen_x, self.screen_height - margen_y),
            Vector2(self.screen_width - margen_x, self.screen_height - margen_y),
        ]

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

        self.posicion += distancia.normalize() * self.velocidad_ir_esquina
        self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    def _actualizar_preparacion_embestida(self, objetivos):
        if pygame.time.get_ticks() - self.inicio_preparacion_embestida >= self.tiempo_preparacion_embestida:
            self._empezar_embestida_real(objetivos)


    def _empezar_embestida_real(self, objetivos):
        if objetivos and random.random() < 0.80:
            objetivo = Vector2(random.choice(objetivos))
        else:
            objetivo = Vector2(random.randint(100, self.screen_width - 100), random.randint(100, self.screen_height - 100))

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

        self.posicion += distancia.normalize() * self.velocidad_embestida
        self.rect.center = (round(self.posicion.x), round(self.posicion.y))


    def terminar_embestida(self):
        self.en_embestida = False
        self.preparando_embestida = False
        self.yendo_esquina_dash = False

        self.objetivo_movimiento = self.posicion.copy()
        self.quieto_hasta = pygame.time.get_ticks() + 500
        self.ultimo_ataque = pygame.time.get_ticks()


    def _crear_disparo(self, direccion, proyectiles, velocidad=None, tamano=32):
        if len(proyectiles) >= self.limite_proyectiles[self.fase_actual]:
            return False

        if velocidad is None:
            velocidad = 7 + self.fase_actual

        proyectiles.add(BossProjectile(self.rect.center, direccion, self.screen, velocidad, tamano))

        return True


    def disparo_apuntado(self, objetivos, proyectiles):
        if not objetivos:
            return

        objetivo = random.choice(objetivos)
        direccion_base = Vector2(objetivo) - Vector2(self.rect.center)

        if direccion_base.length() == 0:
            return

        direccion_base = direccion_base.normalize()

        # fase 3 antes tiraba demasiados
        cantidades = {1: 3, 2: 4, 3: 5, 4: 7, 5: 9}

        cantidad = cantidades[self.fase_actual]
        separacion = 10

        centro = (cantidad - 1) / 2

        for i in range(cantidad):
            direccion = direccion_base.rotate((i - centro) * separacion)

            if not self._crear_disparo(direccion, proyectiles, 7 + self.fase_actual):
                break


    def disparo_radial(self, proyectiles):
        cantidades = {1: 10, 2: 12, 3: 14, 4: 18, 5: 22}

        cantidad = cantidades[self.fase_actual]
        offset = random.uniform(0, 360 / cantidad)

        for i in range(cantidad):
            direccion = Vector2(1, 0).rotate(offset + 360 * i / cantidad)

            if not self._crear_disparo(direccion, proyectiles, 6 + self.fase_actual, 28):
                break

        # segundo anillo solamente en fase 5
        if self.fase_actual == 5:
            for i in range(cantidad):
                direccion = Vector2(1, 0).rotate(offset + 360 * i / cantidad + 360 / cantidad / 2)

                if not self._crear_disparo(direccion, proyectiles, 9 + self.fase_actual, 24):
                    break


    def ataque_cruzado(self, objetivos, proyectiles):
        for angulo in range(0, 360, 45):
            if not self._crear_disparo(Vector2(1, 0).rotate(angulo), proyectiles, 10):
                break

        self.disparo_apuntado(objetivos, proyectiles)


    def lluvia_corta(self, objetivos, meteoritos):
        cantidades = {1: 3, 2: 4, 3: 5, 4: 6, 5: 7}

        for _ in range(cantidades[self.fase_actual]):
            if len(meteoritos) >= self.limite_meteoritos[self.fase_actual]:
                break

            if objetivos and random.random() < 0.60:
                objetivo = random.choice(objetivos)
                x = int(objetivo[0] + random.randint(-140, 140))
                x = max(20, min(self.screen_width - 20, x))

            else:
                x = random.randint(20, self.screen_width - 20)

            meteoritos.add(Meteorito(self.screen, x, 7 + self.fase_actual))


    def invocar_dragones(self, subdragones):
        limite = self.limite_subdragones[self.fase_actual]

        if len(subdragones) >= limite:
            return

        cantidades = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3}

        for _ in range(cantidades[self.fase_actual]):
            if len(subdragones) >= limite:
                break

            subdragones.add(MiniDragon(self.screen, self.fase_actual))


    def iniciar_rafaga(self, tipo):
        if self.rafagas_pendientes > 0:
            return

        cantidades = {1: 2, 2: 2, 3: 3, 4: 3, 5: 4}

        self.tipo_rafaga = tipo
        self.rafagas_pendientes = cantidades[self.fase_actual]
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

        intervalos = {1: 350, 2: 330, 3: 300, 4: 260, 5: 220}

        self.proxima_rafaga = ahora + intervalos[self.fase_actual]


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

        self.rafagas_pendientes = 0

        self.image.set_alpha(0)


    def actualizar_fase_meteoritos(self, objetivos, meteoritos, subdragones):
        ahora = pygame.time.get_ticks()

        if ahora - self.inicio_fase_meteoritos >= self.duracion_fase_meteoritos:
            self.fase_meteoritos = False
            self.image.set_alpha(255)

            # vuelve exactamente donde estaba
            self.rect.center = (round(self.posicion.x), round(self.posicion.y))

            self.quieto_hasta = ahora + 500
            self.ultimo_ataque = ahora

            return

        self.image.set_alpha(0)

        intervalos = {1: 420, 2: 380, 3: 350, 4: 310, 5: 280}
        intervalo_meteorito = intervalos[self.fase_actual]

        if ahora - self.ultimo_meteorito >= intervalo_meteorito and len(meteoritos) < self.limite_meteoritos[self.fase_actual]:
            self.ultimo_meteorito = ahora

            if objetivos and random.random() < 0.70:
                objetivo = random.choice(objetivos)
                x = int(objetivo[0] + random.randint(-160, 160))
                x = max(20, min(self.screen_width - 20, x))

            else:
                x = random.randint(20, self.screen_width - 20)

            meteoritos.add(Meteorito(self.screen, x, 8 + self.fase_actual))

        # en fase 3 no genera manadas cada segundo
        intervalo_dragones = {1: 1800, 2: 1700, 3: 1600, 4: 1450, 5: 1300}[self.fase_actual]

        if ahora - self.ultimo_spawn_fase >= intervalo_dragones:
            self.ultimo_spawn_fase = ahora
            self.invocar_dragones(subdragones)


    def elegir_ataque(self, objetivos, proyectiles, meteoritos, subdragones):
        if not objetivos:
            return

        if self.fase_actual == 1:
            ataques = ["apuntado", "radial", "dash"]
            pesos = [45, 30, 25]

        elif self.fase_actual == 2:
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones"]
            pesos = [30, 25, 20, 15, 10]

        elif self.fase_actual == 3:
            # fase 3 sigue dificil pero ya no se superponen 800 cosas
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones", "rafaga"]
            pesos = [24, 20, 18, 13, 10, 15]

        elif self.fase_actual == 4:
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones", "rafaga", "cruzado"]
            pesos = [17, 18, 15, 12, 10, 16, 12]

        else:
            ataques = ["apuntado", "radial", "dash", "meteoritos", "dragones", "rafaga", "cruzado", "caos"]
            pesos = [13, 15, 13, 11, 10, 16, 10, 12]

        ataque = random.choices(ataques, weights=pesos, k=1)[0]

        if ataque == "apuntado":
            self.disparo_apuntado(objetivos, proyectiles)

        elif ataque == "radial":
            self.disparo_radial(proyectiles)

        elif ataque == "dash":
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
            # antes lanzaba casi todo junto
            # ahora hace radial + UNA cosa extra
            self.disparo_radial(proyectiles)

            if random.random() < 0.5:
                self.lluvia_corta(objetivos, meteoritos)
            else:
                self.invocar_dragones(subdragones)


    def update(self, objetivos, proyectiles, meteoritos, subdragones):
        self.actualizar_fase()
        self.revisar_fase_meteoritos()

        if self.fase_meteoritos:
            self.actualizar_fase_meteoritos(objetivos, meteoritos, subdragones)
            return

        if self.yendo_esquina_dash:
            self._actualizar_ir_esquina()
            return

        if self.preparando_embestida:
            self._actualizar_preparacion_embestida(objetivos)
            return

        if self.en_embestida:
            self._actualizar_embestida()
            return

        # MUY IMPORTANTE:
        # una rafaga reemplaza los ataques normales hasta terminar
        if self.rafagas_pendientes > 0:
            self.actualizar_rafagas(objetivos, proyectiles)
            self._mover_normal()
            return

        self._mover_normal()

        ahora = pygame.time.get_ticks()

        if ahora - self.ultimo_ataque >= self.cooldown_ataque:
            self.ultimo_ataque = ahora
            self.elegir_ataque(objetivos, proyectiles, meteoritos, subdragones)


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