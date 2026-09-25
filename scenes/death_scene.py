if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
import sys
from scenes import notificaciones

def gameloop(screen, estadistica):
    try:
        fondo = pygame.image.load("assets/END.jpg").convert()
    except:
        fondo = pygame.image.load("assets/END.png").convert()
        
    fondo = pygame.transform.scale(fondo, (screen.get_width(), screen.get_height()))

    font_numero = pygame.font.SysFont(None, 55)
    font_boton = pygame.font.SysFont(None, 50)
    
    texto_stat_num = font_numero.render(str(estadistica), True, (180, 180, 180))
    
    boton_retry = pygame.Rect(0, 0, 280, 65)
    boton_retry.center = (screen.get_width() // 2, screen.get_height() // 2 + 60)
    
    boton_quit = pygame.Rect(0, 0, 280, 65)
    boton_quit.center = (screen.get_width() // 2, screen.get_height() // 2 + 140)

    while True:
        screen.blit(fondo, (0, 0))
        
        screen.blit(texto_stat_num, (330, screen.get_height() - 85))
        
        mouse_pos = pygame.mouse.get_pos()
        
        if boton_retry.collidepoint(mouse_pos):
            color_retry = (255, 205, 60)
            texto_retry = font_boton.render("Volver a Jugar", True, (20, 20, 20))
        else:
            color_retry = (40, 45, 55)
            texto_retry = font_boton.render("Volver a Jugar", True, (255, 255, 255))
            
        if boton_quit.collidepoint(mouse_pos):
            color_quit = (255, 205, 60)
            texto_quit = font_boton.render("Salir", True, (20, 20, 20))
        else:
            color_quit = (40, 45, 55)
            texto_quit = font_boton.render("Salir", True, (255, 255, 255))
        
        pygame.draw.rect(screen, color_retry, boton_retry, border_radius=10)
        pygame.draw.rect(screen, (255, 215, 80), boton_retry, 3, border_radius=10)
        
        pygame.draw.rect(screen, color_quit, boton_quit, border_radius=10)
        pygame.draw.rect(screen, (255, 215, 80), boton_quit, 3, border_radius=10)
        
        screen.blit(texto_retry, texto_retry.get_rect(center=boton_retry.center))
        screen.blit(texto_quit, texto_quit.get_rect(center=boton_quit.center))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if boton_retry.collidepoint(mouse_pos):
                        return "retry"
                    
                    if boton_quit.collidepoint(mouse_pos):
                        return "quit"
        
        notificaciones.dibujar(screen)
        pygame.display.flip()