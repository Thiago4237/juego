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
        self.show_help = False
        self.input_name_active = False
        self.player_name = ""
        self.character_selection_active = False
        self.characters = ['veronica', 'santiago']  
        self.selected_character = 0  

        # Cargar la imagen de fondo para la selección de personajes
        self.char_selection_bg = pygame.image.load(join('Resources', 'img', 'Personaje.png')).convert_alpha()
        self.char_selection_bg = pygame.transform.scale(self.char_selection_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))

        # Definir las áreas de los personajes
        self.char_areas = [
            pygame.Rect(350, 600, 250, 450),  # veronica (left character)
            pygame.Rect(700, 600, 250, 450)   # Santiago (right character)
        ]

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

    def draw_help(self):
        self.display_surface.fill('black')
        help_texts = [
            "Objetivo del Juego:",
            "Sobrevive en un entorno oscuro lleno de enemigos.",
            "Recoge baterías para mantener tu linterna encendida.",
            "Destruye enemigos para ganar puntos y sobrevivir.",
            "",
            "Controles:",
            "WASD: Mover al explorador",
            "Click izquierdo: Disparar",
            "ESC: Pausar el juego",
            "",
            "Presiona ESC para volver"
        ]
        for i, text in enumerate(help_texts):
            text_surf = self.font.render(text, True, (255, 255, 255))
            self.display_surface.blit(text_surf, (WINDOW_WIDTH // 2 - 150, 50 + i * 40))

    def draw_name_input(self):
        self.display_surface.fill('black')
        prompt_text = self.font.render("Ingresa tu nombre:", True, (255, 255, 255))
        name_text = self.font.render(self.player_name + ('.' if pygame.time.get_ticks() % 1000 < 500 else ''), True, (255, 255, 255))
        self.display_surface.blit(prompt_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
        self.display_surface.blit(name_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2))
        instruction_text = self.font.render("Presiona ENTER para continuar", True, (255, 255, 255))
        self.display_surface.blit(instruction_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 50))

    def draw_character_selection(self):
        
        self.display_surface.blit(self.char_selection_bg, (0, 0))
        
        triangle_size = 20
        selected_rect = self.char_areas[self.selected_character]
        triangle_points = [
            (selected_rect.centerx - 10, selected_rect.top),
            (selected_rect.centerx + 10, selected_rect.top),
            (selected_rect.centerx, selected_rect.top - triangle_size)
        ]
        pygame.draw.polygon(self.display_surface, (255, 255, 0), triangle_points)

    def handle_input_name(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.player_name.strip():
                    self.game.player_name = self.player_name.strip()
                    self.input_name_active = False
                    self.character_selection_active = True
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    self.input_name_active = False
                    self.player_name = ""
                elif len(self.player_name) < 10 and event.unicode.isprintable():
                    self.player_name += event.unicode
        return None

    def handle_character_selection(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_character = (self.selected_character - 1) % len(self.characters)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_character = (self.selected_character + 1) % len(self.characters)
                elif event.key == pygame.K_RETURN:
                    self.game.selected_character = self.characters[self.selected_character]
                    self.character_selection_active = False
                    return True
                elif event.key == pygame.K_ESCAPE:
                    self.character_selection_active = False
                    self.player_name = ""
                    return None
        return None

    def run(self, start_with_main_menu=True):
        self.show_scores = False
        self.show_help = False
        self.input_name_active = False
        self.character_selection_active = False
        self.player_name = ""
        if not start_with_main_menu:
            self.input_name_active = True
        while True:
            if self.input_name_active:
                result = self.handle_input_name()
                if result is not None:
                    if result:
                        return True
                    else:
                        return False
                self.draw_name_input()
            elif self.character_selection_active:
                result = self.handle_character_selection()
                if result is not None:
                    if result:
                        return True
                    else:
                        continue
                self.draw_character_selection()
            elif self.show_scores:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.show_scores = False
                self.draw_scores()
            elif self.show_help:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.show_help = False
                self.draw_help()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            self.selected_option = (self.selected_option - 1) % len(self.options)
                        if event.key == pygame.K_DOWN:
                            self.selected_option = (self.selected_option + 1) % len(self.options)
                        if event.key == pygame.K_RETURN:
                            if self.options[self.selected_option] == 'Jugar':
                                self.input_name_active = True
                            elif self.options[self.selected_option] == 'Puntajes':
                                self.show_scores = True
                            elif self.options[self.selected_option] == 'Ayuda':
                                self.show_help = True
                            elif self.options[self.selected_option] == 'Salir':
                                pygame.quit()
                                return False
                self.draw_menu()
            pygame.display.update()