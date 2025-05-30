import pygame
from settings import *

class Menu:
    def __init__(self, game):
        self.game = game
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(join('Resources', 'fonts', 'CrimsonText-Regular.ttf'), 36)  
        self.name_font = pygame.font.Font(join('Resources', 'fonts', 'CrimsonText-Regular.ttf'), 48)  
        self.options = ['Jugar', 'Puntajes', 'Ayuda', 'Salir']
        self.selected_option = 0
        self.show_scores = False
        self.show_help = False
        self.input_name_active = False
        self.player_name = ""
        self.character_selection_active = False
        self.characters = ['veronica', 'santiago']
        self.selected_character = 0
        
        self.show_splash = True
        self.splash_timer = 0
        self.splash_duration = 2000
        self.fading_out = False
        self.fade_timer = 0
        self.fade_duration = 1000
        self.splash_alpha = 255
        
        # Cargar música de fondo usando pygame.mixer.music
        try:
            pygame.mixer.music.load(join('audio', 'principal.mp3'))
            pygame.mixer.music.set_volume(1)
        except pygame.error as e:
            print(f"Error al cargar música: {e}")
        
        self.char_selection_bg = pygame.image.load(join('Resources', 'img', 'Personaje.png')).convert_alpha()
        self.char_selection_bg = pygame.transform.scale(self.char_selection_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.menu_bg = pygame.image.load(join('Resources', 'img', 'Menu.png')).convert_alpha()
        self.menu_bg = pygame.transform.scale(self.menu_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.splash_bg = pygame.image.load(join('Resources', 'img', 'PreMenu.png')).convert_alpha()
        self.splash_bg = pygame.transform.scale(self.splash_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.splash_surface = self.splash_bg.copy()
        
        self.help_bg = pygame.image.load(join('Resources', 'img', 'Ayuda.png')).convert_alpha()
        self.help_bg = pygame.transform.scale(self.help_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.scores_bg = pygame.image.load(join('Resources', 'img', 'Scores.png')).convert_alpha()
        self.scores_bg = pygame.transform.scale(self.scores_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        self.name_input_bg = pygame.image.load(join('Resources', 'img', 'NameInput.png')).convert_alpha()
        self.name_input_bg = pygame.transform.scale(self.name_input_bg, (WINDOW_WIDTH, WINDOW_HEIGHT))        
                
        self.option_areas = [
            pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 170 - 25, 200, 40),  # Jugar
            pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 55 - 25, 200, 40),   # Puntajes
            pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 37, 200, 40),        # Ayuda
            pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 178 - 25, 200, 40)   # Salir
        ]
        self.char_areas = [
            pygame.Rect(350, 150, 250, 450),  # Personaje Veronica
            pygame.Rect(700, 150, 250, 450)   # Personaje Santiago
        ]

    def play_music(self):
        """Inicia o reinicia la música del menú."""
        try:
            pygame.mixer.music.play(loops=-1)
        except pygame.error as e:
            print(f"Error al reproducir música: {e}")

    def stop_music(self):
        """Detiene la música del menú."""
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"Error al detener música: {e}")

    def draw_menu(self):
        self.display_surface.blit(self.menu_bg, (0, 0))
        selected_rect = self.option_areas[self.selected_option]
        triangle_size = 15
        triangle_points = [
            (selected_rect.left - 30, selected_rect.centery),
            (selected_rect.left - 45, selected_rect.centery - triangle_size),
            (selected_rect.left - 45, selected_rect.centery + triangle_size)
        ]
        pygame.draw.polygon(self.display_surface, (255, 255, 0), triangle_points)

    def draw_splash(self):
        self.display_surface.blit(self.menu_bg, (0, 0))
        self.splash_surface.set_alpha(int(self.splash_alpha))
        self.display_surface.blit(self.splash_surface, (0, 0))

    def draw_scores(self):        
        self.display_surface.blit(self.scores_bg, (0, 0))                

        for i, score in enumerate(self.game.high_scores):
            text = f"{score['name']}: {score['score']} ({score['date']})"
            score_text = self.font.render(text, True, (255, 255, 255))
            self.display_surface.blit(score_text, (WINDOW_WIDTH // 2 - 210, 180 + i * 75))

    def draw_help(self):
        self.display_surface.blit(self.help_bg, (0, 0))

    def draw_name_input(self):
        self.display_surface.blit(self.name_input_bg, (0, 0))        
        name_text = self.name_font.render(self.player_name + ('.' if pygame.time.get_ticks() % 1000 < 500 else ''), True, (255, 255, 255))
        self.display_surface.blit(name_text, (WINDOW_WIDTH // 2 + 75, WINDOW_HEIGHT // 2 - 32))

    def draw_character_selection(self):
        self.display_surface.blit(self.char_selection_bg, (0, 0))
        triangle_size = 20
        selected_rect = self.char_areas[self.selected_character]
        triangle_points = [
            (selected_rect.centerx, selected_rect.bottom - triangle_size),
            (selected_rect.centerx - 10, selected_rect.bottom),
            (selected_rect.centerx + 10, selected_rect.bottom)
        ]
        pygame.draw.polygon(self.display_surface, (255, 255, 0), triangle_points)

    def handle_input_name(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_music()
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
                self.stop_music()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_character = (self.selected_character - 1) % len(self.characters)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_character = (self.selected_character + 1) % len(self.characters)
                elif event.key == pygame.K_RETURN:
                    self.game.selected_character = self.characters[self.selected_character]
                    self.character_selection_active = False
                    # self.stop_music()  # Detener música antes de iniciar el juego
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
        if start_with_main_menu:
            self.show_splash = True
            self.splash_timer = pygame.time.get_ticks()
            self.splash_alpha = 255
            self.play_music()  # Iniciar música al mostrar el menú
        else:
            self.show_splash = False
            self.fading_out = False
            self.input_name_active = True
            self.play_music()  # Iniciar música al mostrar el menú

        while True:
            if self.show_splash:
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.splash_timer

                if not self.fading_out:
                    if elapsed_time >= self.splash_duration:
                        self.fading_out = True
                        self.fade_timer = pygame.time.get_ticks()
                    self.draw_splash()
                else:
                    fade_elapsed = current_time - self.fade_timer
                    if fade_elapsed < self.fade_duration:
                        self.splash_alpha = 255 * (1 - fade_elapsed / self.fade_duration)
                        self.draw_splash()
                    else:
                        self.show_splash = False
                        self.fading_out = False
                        self.splash_alpha = 255

                pygame.display.update()
                continue

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
                        self.stop_music()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.show_scores = False
                self.draw_scores()
            elif self.show_help:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop_music()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.show_help = False
                self.draw_help()
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop_music()
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.selected_option = (self.selected_option - 1) % len(self.options)
                        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.selected_option = (self.selected_option + 1) % len(self.options)
                        if event.key == pygame.K_RETURN:
                            if self.options[self.selected_option] == 'Jugar':
                                self.input_name_active = True
                            elif self.options[self.selected_option] == 'Puntajes':
                                self.show_scores = True
                            elif self.options[self.selected_option] == 'Ayuda':
                                self.show_help = True
                            elif self.options[self.selected_option] == 'Salir':
                                self.stop_music()
                                return False
                self.draw_menu()
            pygame.display.update()