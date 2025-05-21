from settings import *
from player import *
from sprites import *
from pytmx.util_pygame import load_pygame 
from groups import AllSprites
from random import randint, choice
from battery import Battery
from menu import Menu
import json
from datetime import datetime

class Game:
    def __init__(self):
        """
        Inicializa el juego, configurando la ventana, los grupos de sprites, los temporizadores, el audio y cargando los recursos necesarios.
        """
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Y ahora que...")
        self.clock = pygame.time.Clock()
        self.running = True        
        
        # Grupos de sprites para organización y colisiones
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.battery_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        
        # Superficie para simular la oscuridad y la linterna
        self.light_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.light_surface.fill((10, 10, 20))
        self.light_surface.set_alpha(230)                
        
        # Variables para controlar el disparo del arma
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100
        
        # Temporizador para aparición de enemigos
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 300)
        self.spawn_positions = []
        
        # Cargar sonidos y música
        self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
        self.shoot_sound.set_volume(0.4)
        self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
        self.music = pygame.mixer.Sound(join('audio', 'music.wav'))
        self.music.set_volume(0.3)
        self.music.play(loops=-1)
        
        # Sistema de puntaje
        self.score = 0  # Puntaje inicial
        self.start_time = pygame.time.get_ticks()  # Tiempo de inicio
        self.enemies_defeated = {'ghost': 0, 'bat': 0, 'skeleton': 0}  # Contador de enemigos
        self.score_file = join('Resources', 'scores.json')  # Archivo para guardar puntajes
        self.font = pygame.font.Font(None, 36)  # Fuente para mostrar puntaje
        self.high_scores = self.load_scores()  # Cargar puntajes previos
        self.player_name = ""  # Nombre del jugador (se pedirá al final)
        self.name_input_active = False  # Estado para entrada de nombre
        
        # Cargar imágenes y preparar el escenario
        self.load_images()
        self.setup()
        
    def load_images(self):
        """
        Carga las imágenes necesarias para las balas y los enemigos, organizando los frames de animación por tipo de enemigo.
        """
        self.bullet_surface = pygame.image.load(join('Resources', 'img', 'gun', 'bullet.png')).convert_alpha()
        
        # Cargar los frames de animación de cada tipo de enemigo
        folders = ['ghost', 'bat', 'skeleton']  # Tipos de enemigos
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('Resources', 'img', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda x: int(x.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)
    
    def load_scores(self):
        """Carga los 5 mejores puntajes desde un archivo JSON."""
        try:
            with open(self.score_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def save_scores(self, player_name, score):
        """Guarda el puntaje actual en los 5 mejores puntajes en un archivo JSON."""
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_score = {'name': player_name, 'score': int(score), 'date': date}
        self.high_scores.append(new_score)
        # Ordenar por puntaje (descendente) y mantener solo los 5 mejores
        self.high_scores = sorted(self.high_scores, key=lambda x: x['score'], reverse=True)[:5]
        with open(self.score_file, 'w') as f:
            json.dump(self.high_scores, f, indent=4)

    def update_score(self, dt, enemy_type=None):
        """Actualiza el puntaje según el tiempo sobrevivido y enemigos derrotados."""
        # Sumar 10 puntos por segundo sobrevivido
        self.score += 10 * dt
        # Sumar puntos por enemigos derrotados
        if enemy_type:
            if enemy_type == 'ghost':
                self.score += 50
                self.enemies_defeated['ghost'] += 1
            elif enemy_type == 'bat':
                self.score += 20
                self.enemies_defeated['bat'] += 1
            elif enemy_type == 'skeleton':
                self.score += 100
                self.enemies_defeated['skeleton'] += 1
    
    def draw_score(self):
        """Muestra el puntaje actual en la pantalla de juego."""
        score_text = self.font.render(f"Puntaje: {int(self.score)}", True, (255, 255, 255))
        self.display_surface.blit(score_text, (10, 70))  # Debajo de las barras de vida y linterna

    def input_name(self):
        """Maneja la entrada del nombre del jugador al final de la partida."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self.player_name:
                    self.save_scores(self.player_name, self.score)
                    self.name_input_active = False
                    self.running = False  # Terminar después de guardar
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif len(self.player_name) < 10:  # Límite de 10 caracteres
                    self.player_name += event.unicode

    def draw_name_input(self):
        """Muestra la pantalla para ingresar el nombre."""
        self.display_surface.fill('black')
        prompt_text = self.font.render("Ingresa tu nombre:", True, (255, 255, 255))
        name_text = self.font.render(self.player_name, True, (255, 255, 255))
        self.display_surface.blit(prompt_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50))
        self.display_surface.blit(name_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2))
        pygame.display.update()
    
    def input(self):
        """
        Gestiona la entrada del jugador para disparar el arma cuando se presiona el botón izquierdo del mouse y el arma está lista.
        """
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()  # Reproducir sonido de disparo
            position = self.gun.rect.center + self.gun.player_direction * 50  # Posición inicial de la bala
            Bullet(self.bullet_surface, position, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False  # Bloquear disparo hasta que pase el cooldown
            self.shoot_time = pygame.time.get_ticks()
       
    def gun_timer(self):
        """
        Controla el tiempo de recarga del arma para permitir el siguiente disparo después de un enfriamiento.
        """
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True  # Permitir disparar de nuevo
        
    def setup(self):
        """
        Configura el mapa, los sprites del entorno, el jugador, el arma, las posiciones de aparición de enemigos y las baterías.
        """
        current_dir = os.path.dirname(__file__)
        map = load_pygame(join(current_dir, 'Resources', 'map', 'maps', 'world.tmx'))
        
        # Crear el suelo a partir de la capa 'Ground' del mapa
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        
        # Crear objetos sólidos a partir de la capa 'Objects'
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        
        # Crear colisiones invisibles a partir de la capa 'Collisions'
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        
        player_pos = None
        
        # Crear jugador y guardar posiciones de spawn de enemigos
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.battery_sprites)
                self.gun = Gun(self.player, self.all_sprites)
                player_pos = (obj.x, obj.y)
            else:
                self.spawn_positions.append((obj.x, obj.y))
                
        if player_pos:
            self.spawn_positions = [
                pos for pos in self.spawn_positions
                if pygame.math.Vector2(pos).distance_to(pygame.math.Vector2(player_pos)) > 50
            ]
        # Colocar baterías en posiciones aleatorias
        num_batteries = 7
        for _ in range(num_batteries):
            x = random.randint(0, WINDOW_WIDTH - 20)
            y = random.randint(0, WINDOW_HEIGHT - 20)
            Battery((x, y), (self.all_sprites, self.battery_sprites))
    
    def bullet_collision(self):
        """
        Detecta colisiones entre balas y enemigos. Aplica daño al enemigo y elimina la bala.
        """
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.take_damage(10)  # Cada bala hace 10 de daño
                    bullet.kill()

    def player_collision(self):
        """
        Detecta colisiones entre el jugador y los enemigos. Aplica daño al jugador según el tipo de enemigo.
        """
        collision_sprites = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if collision_sprites:
            for sprite in collision_sprites:
                self.player.take_damage(sprite.damage)  # Aplicar daño según el tipo de enemigo
                if self.player.health <= 0:
                    self.running = False  # Fin del juego si la salud llega a 0
    
    def run(self):
        """
        Bucle principal del juego. Gestiona eventos, actualizaciones de sprites, colisiones, renderizado y HUD.
        """
        while self.running:
            
            dt = self.clock.tick() / 1000
            
            if self.name_input_active:
                self.input_name()
                self.draw_name_input()
                continue
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == self.enemy_event:
                    # Crear un nuevo enemigo con un tipo específico
                    enemy_type = choice(['ghost', 'bat', 'skeleton'])
                    Enemy(choice(self.spawn_positions), self.enemy_frames[enemy_type], (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, enemy_type, self)
                    
            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()
            self.update_score(dt)
            
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)

            # Dibujar la linterna y la oscuridad
            self.light_surface.fill((10, 10, 20))
            light_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.draw.circle(self.light_surface, (255, 255, 255), light_pos, self.player.light_radius)
            self.light_surface.set_colorkey((255, 255, 255))
            self.light_surface.set_alpha(230)
            self.display_surface.blit(self.light_surface, (0, 0))
            
            # Dibujar barra de salud del jugador
            bar_width = 200
            bar_height = 20
            bar_x = 10
            bar_y = 40  # Debajo de la barra de la linterna
            max_health = self.player.max_health
            current_health = self.player.health
            health_ratio = current_health / max_health
            pygame.draw.rect(self.display_surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            fill_color = (0, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
            fill_width = bar_width * health_ratio
            pygame.draw.rect(self.display_surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
            
            # Dibujar barra de carga de la linterna
            bar_y = 10
            max_charge = 100
            current_charge = self.player.light_charge
            pygame.draw.rect(self.display_surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            fill_color = (0, 255, 0) if current_charge > 20 else (255, 0, 0)
            fill_width = (current_charge / max_charge) * bar_width
            pygame.draw.rect(self.display_surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
            
            # Dibujar barras de salud de los enemigos
            for sprite in self.enemy_sprites:
                if hasattr(sprite, 'draw_health_bar') and sprite.death_time == 0:
                    sprite.draw_health_bar(self.display_surface, self.all_sprites.offset)
            
            # Dibujar puntaje
            self.draw_score()
            
            # Verificar si el juego terminó
            if self.player.health <= 0:
                # Verificar si el puntaje califica para los 5 mejores
                if not self.high_scores or len(self.high_scores) < 5 or self.score > min(self.high_scores, key=lambda x: x['score'])['score']:
                    self.name_input_active = True
                else:
                    self.running = False
            
            pygame.display.update()
            
        pygame.quit()

# if __name__ == "__main__":
#     game = Game()
#     game.run()

if __name__ == "__main__":
    game = Game()
    menu = Menu(game)
    if menu.run():
        game.run()