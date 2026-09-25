if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
from pygame.locals import K_ESCAPE, KEYDOWN, QUIT
import customization

def gameloop(screen, logros_desbloqueados):
    clock = pygame.time.Clock()
    
    font_titulo = pygame.font.Font(None, 72)
    font_nombre = pygame.font.Font(None, 36)
    font_desc = pygame.font.Font(None, 24)
    font_chica = pygame.font.Font(None, 27)

    nombres = [
        "Primeros Pasos", "Piloto Veterano", "Leyenda Galáctica",
        "Primera Paga", "Tanque Espacial", "Arsenal Infinito",
        "Intocable", "Fortaleza Espacial", "Sobrecarga",
        "¿Eres nuevo?", "Pacifista", "Cliente VIP"
    ]
    
    descripciones = [
        "Juega tu primera partida.", "Supera los 500 puntos.", "Alcanza los 1000 puntos.",
        "Acumula 100 coins totales.", "Alcanza el nivel 10 de Vida.", "Alcanza el nivel 10 de Munición.",
        "Gana 250 pts sin recibir daño.", "Recoge 3 escudos en una partida.", "Usa la ametralladora (Rapid Fire).",
        "Muere con menos de 10 puntos.", "Llega a 100 pts sin disparar.", "Gasta 500 coins en una visita."
    ]

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit"
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "back"

        # Dibujar el fondo
        background = pygame.image.load(customization.obtener_asset("background")).convert()
        background = pygame.transform.scale(background, (screen.get_width(), screen.get_height()))
        screen.blit(background, (0, 0))

        sombra = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        sombra.fill((0, 0, 0, 200)) # Sombra un poco más oscura para leer mejor
        screen.blit(sombra, (0, 0))

        titulo = font_titulo.render("LOGROS Y TROFEOS", True, (255, 215, 80))
        screen.blit(titulo, titulo.get_rect(center=(screen.get_width() // 2, 60)))

        for i in range(12):
            x = 80 if i < 6 else 540
            y = 150 + (i % 6) * 90

            desbloqueado = logros_desbloqueados[i]

            if desbloqueado:
                color_titulo = (255, 215, 80)  
                color_desc = (200, 200, 200)   
                texto_nombre = nombres[i]
                texto_desc = descripciones[i]
            else:
                color_titulo = (100, 100, 100) 
                color_desc = (80, 80, 80)
                
                if i >= 9:
                    texto_nombre = "??? (Logro Oculto)"
                    texto_desc = "Sigue jugando para descubrirlo."
                else:
                    texto_nombre = nombres[i] + " (Bloqueado)"
                    texto_desc = descripciones[i]

            sup_nombre = font_nombre.render(texto_nombre, True, color_titulo)
            sup_desc = font_desc.render(texto_desc, True, color_desc)
            
            screen.blit(sup_nombre, (x, y))
            screen.blit(sup_desc, (x, y + 30))

        controles = font_chica.render("ESC: Volver al menú", True, (220, 220, 220))
        screen.blit(controles, controles.get_rect(center=(screen.get_width() // 2, 720)))

        pygame.display.flip()
        clock.tick(60)