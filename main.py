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
        Inicializa el juego, configurando la ventana, los temporizadores, el audio y los recursos básicos.
        """
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Y ahora que...")
        self.clock = pygame.time.Clock()
        self.running = True        
        self.game_over = False
        self.game_over_time = 0
        self.game_over_duration = 3000  # 3 segundos para mostrar puntaje final
        self.game_active = False
        self.paused = False  # Estado para la pausa
        self.pause_selected_option = 0
        self.pause_options = ['Continuar', 'Reiniciar', 'Menú Principal']
        
        # Selección de personaje
        self.selected_character = "veronica"
        
        # Grupos de sprites (se inicializan vacíos, se llenan en setup)
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
        self.music = pygame.mixer.Sound(join('audio', 'principal.mp3'))
        self.music.set_volume(1)
        self.music.play(loops=-1)
        
        # Sistema de puntaje
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.enemies_defeated = {'ghost': 0, 'bat': 0, 'skeleton': 0}
        self.score_file = join('Resources', 'scores.json')
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        self.high_scores = self.load_scores()
        self.player_name = ""  # Se establecerá desde el menú

        # Cargar imágenes (sin inicializar el escenario aún)
        self.load_images()
        
    def load_images(self):
        self.bullet_surface = pygame.image.load(join('Resources', 'img', 'gun', 'bullet.png')).convert_alpha()
        folders = ['ghost', 'bat', 'skeleton']
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('Resources', 'img', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda x: int(x.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)
    
    def load_scores(self):
        try:
            with open(self.score_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_scores(self):
        if self.player_name:  # Solo guardar si hay un nombre válido
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_score = {'name': self.player_name, 'score': int(self.score), 'date': date}
            self.high_scores.append(new_score)
            self.high_scores = sorted(self.high_scores, key=lambda x: x['score'], reverse=True)[:5]
            with open(self.score_file, 'w') as f:
                json.dump(self.high_scores, f, indent=4)

    def update_score(self, dt, enemy_type=None):
        self.score += 10 * dt
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
        score_text = self.font.render(f"Puntaje: {int(self.score)}", True, (255, 255, 255))
        self.display_surface.blit(score_text, (10, 70))

    def draw_game_over(self):
        self.display_surface.fill('black')
        score_text = self.game_over_font.render(f"Puntaje Final: {int(self.score)}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.display_surface.blit(score_text, score_rect)
        pygame.display.update()

    def draw_pause_menu(self):
        self.display_surface.fill('black')
        title_text = self.font.render("Pausa", True, (255, 255, 255))
        self.display_surface.blit(title_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 100))
        for i, option in enumerate(self.pause_options):
            color = (255, 255, 0) if i == self.pause_selected_option else (255, 255, 255)
            text = self.font.render(option, True, color)
            self.display_surface.blit(text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 50 + i * 50))

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            self.shoot_sound.play()
            position = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surface, position, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()
       
    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True
        
    def reset_game(self):
        """
        Reinicia los valores críticos del juego para una nueva partida.
        """
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.enemies_defeated = {'ghost': 0, 'bat': 0, 'skeleton': 0}
        self.game_over = False
        self.game_over_time = 0
        self.game_active = False
        self.paused = False
        self.pause_selected_option = 0
        
        # Vaciar grupos de sprites para evitar persistencia
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.battery_sprites.empty()
        self.enemy_group.empty()
        
        # Reconfigurar el escenario y el jugador
        self.setup()

    def setup(self):
        current_dir = os.path.dirname(__file__)
        map = load_pygame(join(current_dir, 'Resources', 'map', 'maps', 'world.tmx'))
        for x, y, image in map.get_layer_by_name('Ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)
        for obj in map.get_layer_by_name('Objects'):
            CollisionSprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites))
        for obj in map.get_layer_by_name('Collisions'):
            CollisionSprite((obj.x, obj.y), pygame.Surface((obj.width, obj.height)), self.collision_sprites)
        player_pos = None
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.battery_sprites, character=self.selected_character)
                self.gun = Gun(self.player, self.all_sprites)
                player_pos = (obj.x, obj.y)
            else:
                self.spawn_positions.append((obj.x, obj.y))
        if player_pos:
            self.spawn_positions = [
                pos for pos in self.spawn_positions
                if pygame.math.Vector2(pos).distance_to(pygame.math.Vector2(player_pos)) > 50
            ]
        num_batteries = 7
        for _ in range(num_batteries):
            x = random.randint(0, WINDOW_WIDTH - 20)
            y = random.randint(0, WINDOW_HEIGHT - 20)
            Battery((x, y), (self.all_sprites, self.battery_sprites))
    
    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()
                    for sprite in collision_sprites:
                        sprite.take_damage(10)
                    bullet.kill()

    def player_collision(self):
        collision_sprites = pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask)
        if collision_sprites:
            for sprite in collision_sprites:
                self.player.take_damage(sprite.damage)
                if self.player.health <= 0:
                    self.game_over = True
                    self.game_over_time = pygame.time.get_ticks()
                    self.save_scores()

    def run(self):
        self.reset_game()  # Reiniciar valores y configurar el escenario
        self.game_active = True  # Activar el juego después de ingresar el nombre
        while self.running:
            dt = self.clock.tick() / 1000
            
            if self.paused:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = False
                            self.game_active = True
                        elif event.key == pygame.K_UP:
                            self.pause_selected_option = (self.pause_selected_option - 1) % len(self.pause_options)
                        elif event.key == pygame.K_DOWN:
                            self.pause_selected_option = (self.pause_selected_option + 1) % len(self.pause_options)
                        elif event.key == pygame.K_RETURN:
                            if self.pause_options[self.pause_selected_option] == 'Continuar':
                                self.paused = False
                                self.game_active = True
                            elif self.pause_options[self.pause_selected_option] == 'Reiniciar':
                                self.reset_game()
                                self.game_active = True
                            elif self.pause_options[self.pause_selected_option] == 'Menú Principal':
                                return  # Volver al menú principal
                self.draw_pause_menu()
                pygame.display.update()
                continue

            if self.game_over:
                self.game_active = False
                self.draw_game_over()
                if pygame.time.get_ticks() - self.game_over_time >= self.game_over_duration:
                    return  # Volver al menú
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game_active:
                        self.paused = True
                        self.game_active = False
                if event.type == self.enemy_event and self.game_active:
                    enemy_type = choice(['ghost', 'bat', 'skeleton'])
                    Enemy(choice(self.spawn_positions), self.enemy_frames[enemy_type], 
                          (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, enemy_type, self)
                    
            if self.game_active:
                self.gun_timer()
                self.input()
                self.all_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()
                self.update_score(dt)
            
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            self.light_surface.fill((10, 10, 20))
            light_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.draw.circle(self.light_surface, (255, 255, 200), light_pos, self.player.light_radius)
            self.light_surface.set_colorkey((255, 255, 200))
            self.light_surface.set_alpha(230)
            self.display_surface.blit(self.light_surface, (0, 0))
            
            bar_width = 200
            bar_height = 20
            bar_x = 10
            bar_y = 40
            max_health = self.player.max_health
            current_health = self.player.health
            health_ratio = current_health / max_health
            pygame.draw.rect(self.display_surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            fill_color = (0, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
            fill_width = bar_width * health_ratio
            pygame.draw.rect(self.display_surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
            
            bar_y = 10
            max_charge = 100
            current_charge = self.player.light_charge
            pygame.draw.rect(self.display_surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            fill_color = (0, 255, 0) if current_charge > 20 else (255, 0, 0)
            fill_width = (current_charge / max_charge) * bar_width
            pygame.draw.rect(self.display_surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
            
            for sprite in self.enemy_sprites:
                if hasattr(sprite, 'draw_health_bar') and sprite.death_time == 0:
                    sprite.draw_health_bar(self.display_surface, self.all_sprites.offset)
            
            self.draw_score()
            pygame.display.update()
            
        pygame.quit()

if __name__ == "__main__":
    while True:
        game = Game()
        menu = Menu(game)
        if not menu.run(start_with_main_menu=True):
            break
        game.run()