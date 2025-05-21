import pygame
from settings import *

class Menu:
    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(None, 36)
        self.options = ['Jugar', 'Puntajes', 'Ayuda', 'Salir']
        self.selected_option = 0
        self.show_scores = False

    def draw_menu(self):
        self.display_surface.fill('black')
        for i, option in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            text = self.font.render(option, True, color)
            self.display_surface.blit(text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 100 + i * 50))

    def draw_scores(self):
        self.display_surface.fill('black')
        title = self.font.render("Mejores Puntajes", True, (255, 255, 255))
        self.display_surface.blit(title, (WINDOW_WIDTH // 2 - 100, 50))
        for i, score in enumerate(self.game.high_scores):
            text = f"{score['name']}: {score['score']} ({score['date']})"
            score_text = self.font.render(text, True, (255, 255, 255))
            self.display_surface.blit(score_text, (WINDOW_WIDTH // 2 - 100, 100 + i * 50))
        back_text = self.font.render("Presiona ESC para volver", True, (255, 255, 255))
        self.display_surface.blit(back_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 100))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
                if event.type == pygame.KEYDOWN:
                    if self.show_scores:
                        if event.key == pygame.K_ESCAPE:
                            self.show_scores = False
                    else:
                        if event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) % len(self.options)
                        if event.key == pygame.K_DOWN:
                            self.selected_option = (self.selected_option + 1) % len(self.options)
                        if event.key == pygame.K_RETURN:
                            if self.options[self.selected_option] == 'Jugar':
                                return True  # Iniciar juego
                            elif self.options[self.selected_option] == 'Puntajes':
                                self.show_scores = True
                            elif self.options[self.selected_option] == 'Ayuda':
                                pass  # Implementar ayuda más adelante
                            elif self.options[self.selected_option] == 'Salir':
                                pygame.quit()
                                return False

            if self.show_scores:
                self.draw_scores()
            else:
                self.draw_menu()
            pygame.display.update()