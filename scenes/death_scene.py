if __name__ == "__main__":
    raise RuntimeError("\033c❌ ESTE ARCHIVO NO DEBE EJECUTARSE. EJECUTA main.py")

import pygame
import sys

def gameloop(screen, estadistica=0):
    try:
        fondo = pygame.image.load("assets/END.jpg").convert()
    except:
        fondo = pygame.image.load("assets/END.png").convert()
        
    fondo = pygame.transform.scale(fondo, (screen.get_width(), screen.get_height()))

    font_numero = pygame.font.SysFont(None, 45)
    font_boton = pygame.font.SysFont(None, 50)
    
    texto_stat_num = font_numero.render(str(estadistica), True, (255, 200, 50))
    texto_retry = font_boton.render("Volver a Jugar", True, (0, 0, 0))
    texto_quit = font_boton.render("Salir", True, (0, 0, 0))
    
    centro_x = screen.get_width() // 2
    
    boton_retry = pygame.Rect(0, 0, 280, 65)
    boton_retry.center = (centro_x, screen.get_height() // 2 + 50)
    
    boton_quit = pygame.Rect(0, 0, 280, 65)
    boton_quit.center = (centro_x, screen.get_height() // 2 + 130)

    while True:
        screen.blit(fondo, (0, 0))
        
        pos_y_stat = screen.get_height() - 65
        screen.blit(texto_stat_num, (370, pos_y_stat))
        
        mouse_pos = pygame.mouse.get_pos()
        
        if boton_retry.collidepoint(mouse_pos):
            color_retry = (255, 205, 60)
        else:
            color_retry = (40, 45, 55)
            
        if boton_quit.collidepoint(mouse_pos):
            color_quit = (255, 205, 60)
        else:
            color_quit = (40, 45, 55)
        
        pygame.draw.rect(screen, color_retry, boton_retry, border_radius=15)
        pygame.draw.rect(screen, color_quit, boton_quit, border_radius=15)
        
        screen.blit(texto_retry, texto_retry.get_rect(center=boton_retry.center))
        screen.blit(texto_quit, texto_quit.get_rect(center=boton_quit.center))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if boton_retry.collidepoint(mouse_pos):
                    return "retry"
                
                if boton_quit.collidepoint(mouse_pos):
                    return "quit"
        
        pygame.display.flip()