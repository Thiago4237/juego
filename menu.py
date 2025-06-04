import pygame
from settings import *

class Menu:
    def __init__(self, game):
        # incializa la configuracion a usar en el aplicativo 
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
        """
        Dibuja el menú en la superficie de visualización principal.
        Esta función coloca la imagen de fondo del menú y dibuja un triángulo amarillo
        al lado de la opción actualmente seleccionada para indicar la selección del usuario.
        El triángulo se posiciona a la izquierda de la opción seleccionada, utilizando
        las coordenadas del rectángulo correspondiente en `self.option_areas`.
        No recibe parámetros adicionales y no retorna ningún valor.
        """
        
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
        """
        Dibuja la pantalla de presentación (splash) sobre la superficie principal de la ventana.
        Este método primero dibuja el fondo del menú y luego superpone la imagen de splash
        con un nivel de transparencia determinado por `self.splash_alpha`.
        Uso típico:
            - Mostrar una pantalla de bienvenida o transición antes de mostrar el menú principal.
        Variables utilizadas:
            self.display_surface: Superficie principal donde se dibujan los elementos.
            self.menu_bg: Imagen de fondo del menú.
            self.splash_surface: Imagen de la pantalla de presentación.
            self.splash_alpha: Valor de transparencia para la imagen de splash (0-255).
        """
        
        self.display_surface.blit(self.menu_bg, (0, 0))
        self.splash_surface.set_alpha(int(self.splash_alpha))
        self.display_surface.blit(self.splash_surface, (0, 0))

    def draw_scores(self): 
        """
        Dibuja en pantalla la lista de puntuaciones más altas.
        Esta función muestra un fondo específico para las puntuaciones y luego recorre la lista de puntuaciones altas del juego,
        mostrando el nombre del jugador, la puntuación y la fecha en la superficie de visualización.
        Parámetros:
            No recibe parámetros directos, pero utiliza los atributos:
                - self.display_surface: Superficie donde se dibuja.
                - self.scores_bg: Imagen de fondo para la sección de puntuaciones.
                - self.game.high_scores: Lista de diccionarios con las puntuaciones más altas.
                - self.font: Fuente utilizada para renderizar el texto.
        Retorno:
            None
        """
               
        self.display_surface.blit(self.scores_bg, (0, 0))                

        for i, score in enumerate(self.game.high_scores):
            text = f"{score['name']}: {score['score']} ({score['date']})"
            score_text = self.font.render(text, True, (255, 255, 255))
            self.display_surface.blit(score_text, (WINDOW_WIDTH // 2 - 210, 180 + i * 75))

    def draw_help(self):
        self.display_surface.blit(self.help_bg, (0, 0))

    def draw_name_input(self):
        """
        Dibuja la pantalla de entrada de nombre del jugador.
        Este método renderiza un fondo específico para la entrada de nombre y 
        muestra el nombre del jugador en la pantalla. Si el tiempo actual en 
        milisegundos es divisible por 1000 y menor que 500, se agrega un punto 
        parpadeante al final del nombre del jugador.
        La posición del texto se calcula en base al ancho y alto de la ventana 
        (WINDOW_WIDTH y WINDOW_HEIGHT).
        Parámetros:
        - No recibe parámetros.
        Retorno:
        - No retorna ningún valor.
        """
        
        self.display_surface.blit(self.name_input_bg, (0, 0))        
        name_text = self.name_font.render(self.player_name + ('.' if pygame.time.get_ticks() % 1000 < 500 else ''), True, (255, 255, 255))
        self.display_surface.blit(name_text, (WINDOW_WIDTH // 2 + 75, WINDOW_HEIGHT // 2 - 32))

    def draw_character_selection(self):
        """
        Dibuja la pantalla de selección de personajes en la superficie de visualización.
        Este método renderiza el fondo de selección de personajes y un triángulo amarillo
        que indica el personaje actualmente seleccionado. El triángulo se posiciona en la
        parte inferior del área del personaje seleccionado.
        Atributos:
            self.display_surface: Superficie de visualización donde se renderiza la selección.
            self.char_selection_bg: Imagen de fondo para la selección de personajes.
            self.char_areas: Lista de rectángulos que representan las áreas de los personajes.
            self.selected_character: Índice del personaje actualmente seleccionado.
        Detalles:
            - El triángulo amarillo tiene un tamaño de 20 píxeles.
            - Se calcula la posición del triángulo basado en el rectángulo del personaje seleccionado.
            - El triángulo se dibuja utilizando `pygame.draw.polygon`.
        """
        
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
        """
        Maneja la entrada del nombre del jugador mediante eventos de Pygame.
        Este método procesa los eventos generados por Pygame para permitir al jugador
        ingresar su nombre. Realiza las siguientes acciones según el tipo de evento:
        - Si se detecta un evento de salida (pygame.QUIT), detiene la música y finaliza el bucle.
        - Si se presiona la tecla Enter (pygame.K_RETURN) y el nombre del jugador no está vacío,
          guarda el nombre del jugador, desactiva la entrada de nombre y activa la selección de personaje.
        - Si se presiona la tecla Backspace (pygame.K_BACKSPACE), elimina el último carácter del nombre.
        - Si se presiona la tecla Escape (pygame.K_ESCAPE), desactiva la entrada de nombre y limpia el nombre.
        - Si el nombre tiene menos de 10 caracteres y el carácter ingresado es imprimible,
          agrega el carácter al nombre del jugador.
        Retorno:
            - False: Si se detecta un evento de salida (pygame.QUIT).
            - None: En cualquier otro caso.
        Atributos modificados:
            - self.player_name: Actualiza el nombre del jugador según la entrada.
            - self.input_name_active: Cambia el estado de la entrada de nombre.
            - self.character_selection_active: Activa la selección de personaje.
        Restricciones:
            - El nombre del jugador no puede exceder los 10 caracteres.
            - Solo se aceptan caracteres imprimibles.
        """
        
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
        """
        Maneja la lógica de selección de personaje en el menú del juego.
        Este método procesa los eventos de entrada del usuario para permitir la selección
        de un personaje, la confirmación de la selección, o la salida del menú de selección.
        Eventos manejados:
        - pygame.QUIT: Detiene la música y sale del menú de selección.
        - pygame.KEYDOWN:
            - Flecha izquierda (K_LEFT) o tecla 'A': Cambia al personaje anterior en la lista.
            - Flecha derecha (K_RIGHT) o tecla 'D': Cambia al siguiente personaje en la lista.
            - Enter (K_RETURN): Confirma la selección del personaje y desactiva el menú de selección.
            - Escape (K_ESCAPE): Cancela la selección y limpia el nombre del jugador.
        Retorno:
        - False: Si se detecta un evento de salida (pygame.QUIT).
        - True: Si se confirma la selección del personaje (K_RETURN).
        - None: Si no se realiza ninguna acción relevante o se cancela la selección (K_ESCAPE).
        """
        
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
        """
        Ejecuta el ciclo principal del menú del juego.
        Este método controla la lógica y la visualización del menú, incluyendo la pantalla de inicio,
        la entrada del nombre del jugador, la selección de personaje, la visualización de puntajes y ayuda,
        así como la navegación por las opciones del menú principal.
        Args:
            start_with_main_menu (bool): Indica si se debe iniciar con el menú principal o directamente con la entrada de nombre.
                                         Por defecto es True.
        Returns:
            bool: Devuelve True si el jugador decide iniciar el juego, o False si el jugador decide salir.
        """
        
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