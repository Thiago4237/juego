from settings import *
from player import *
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from random import randint, choice
from drop import Drop
from menu import Menu
import json
from datetime import datetime
import pygame
import math

class Game:
    def __init__(self):
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Y ahora que...")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.game_over_time = 0
        self.game_over_duration = 3000
        self.game_active = False
        self.paused = False
        self.pause_selected_option = 0
        self.pause_options = ['Continuar', 'Reiniciar', 'Menú Principal']
        
        self.selected_character = "veronica"
        
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.drop_sprites = pygame.sprite.Group()
        
        self.light_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.light_surface.fill((10, 10, 20))
        self.light_surface.set_alpha(230)
        
        self.fog_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.fog_surface.fill((200, 200, 200))
        self.fog_base_alpha = 75
        self.fog_alpha_variation = 25
        self.fog_alpha_speed = 1.0
        self.fog_offset = pygame.Vector2(0, 0)
        self.fog_scroll_speed = pygame.Vector2(20, -10)
        self.fog_active = True
        self.fog_active_duration = 5.0
        self.fog_inactive_duration = 3.0
        self.fog_timer = 0.0
        
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 100
        
        self.enemy_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_event, 500)
        self.spawn_positions = []
        
        try:
            self.shoot_sound = pygame.mixer.Sound(join('audio', 'shoot.wav'))
            self.shoot_sound.set_volume(0.2)
            self.impact_sound = pygame.mixer.Sound(join('audio', 'impact.ogg'))
            pygame.mixer.music.load(join('audio', 'principal.mp3'))
            pygame.mixer.music.set_volume(1)
        except pygame.error as e:
            print(f"Error al cargar sonidos o música: {e}")
            self.shoot_sound = None
            self.impact_sound = None
        
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.difficulty_timer = 0
        self.difficulty_interval = 180
        self.difficulty_level = 0
        self.enemies_defeated = {'ghost': 0, 'bat': 0, 'skeleton': 0}
        self.enemies_active = {'ghost': 0, 'bat': 0, 'skeleton': 0}
        self.max_enemies_per_type = 5
        self.score_file = join('Resources', 'scores.json')
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        self.high_scores = self.load_scores()
        self.player_name = ""
        
        self.load_images()
        
    def play_music(self):
        """Inicia o reinicia la música del juego."""
        try:
            pygame.mixer.music.play(loops=-1)
        except pygame.error as e:
            print(f"Error al reproducir música: {e}")

    def stop_music(self):
        """Detiene la música del juego."""
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print(f"Error al detener música: {e}")

    def pause_music(self):
        """Pausa la música del juego."""
        try:
            pygame.mixer.music.pause()
        except pygame.error as e:
            print(f"Error al pausar música: {e}")

    def unpause_music(self):
        """Reanuda la música del juego desde donde se pausó."""
        try:
            pygame.mixer.music.unpause()
        except pygame.error as e:
            print(f"Error al reanudar música: {e}")

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
        if self.player_name:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_score = {'name': self.player_name, 'score': int(self.score), 'date': date}
            self.high_scores.append(new_score)
            self.high_scores = sorted(self.high_scores, key=lambda x: x['score'], reverse=True)[:5]
            with open(self.score_file, 'w') as f:
                json.dump(self.high_scores, f, indent=4)

    def update_score(self, dt, enemy_type=None):
        self.score += 10 * dt
        if enemy_type:
            if enemy_type == 'ghost' and self.enemies_active['ghost'] > 0:
                self.score += 50
                self.enemies_defeated['ghost'] += 1
                self.enemies_active['ghost'] -= 1
            elif enemy_type == 'bat' and self.enemies_active['bat'] > 0:
                self.score += 20
                self.enemies_defeated['bat'] += 1
                self.enemies_active['bat'] -= 1
            elif enemy_type == 'skeleton' and self.enemies_active['skeleton'] > 0:
                self.score += 100
                self.enemies_defeated['skeleton'] += 1
                self.enemies_active['skeleton'] -= 1

    def draw_score(self):
        score_text = self.font.render(f"Puntaje: {int(self.score)}", True, (255, 255, 255))
        self.display_surface.blit(score_text, (10, 70))
        total_enemies = sum(self.enemies_active.values())
        debug_text = self.font.render(
            f"Enemigos activos: G={self.enemies_active['ghost']} "
            f"B={self.enemies_active['bat']} S={self.enemies_active['skeleton']} "
            f"Total={total_enemies}",
            True, (255, 255, 255)
        )
        self.display_surface.blit(debug_text, (10, 100))

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
            if self.shoot_sound:
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

    def update_difficulty(self, dt):
        self.difficulty_timer += dt
        if self.difficulty_timer >= self.difficulty_interval:
            self.difficulty_level += 1
            self.difficulty_timer = 0

    def get_drop_probability(self):
        base_probability = 0.7  # 70% inicial
        reduction = 0.05 * self.difficulty_level  # Reducir 5% por nivel
        return max(0.1, base_probability - reduction)  # Mínimo 10%

    def reset_game(self):
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.difficulty_timer = 0
        self.difficulty_level = 0
        self.enemies_defeated = {'ghost': 0, 'bat': 0, 'skeleton': 0}
        self.enemies_active = {'ghost': 0, 'bat': 0, 'skeleton': 0}
        self.game_over = False
        self.game_over_time = 0
        self.game_active = False
        self.paused = False
        self.pause_selected_option = 0
        self.fog_offset = pygame.Vector2(0, 0)
        self.fog_active = True
        self.fog_timer = 0.0
        
        self.all_sprites.empty()
        self.collision_sprites.empty()
        self.bullet_sprites.empty()
        self.enemy_sprites.empty()
        self.drop_sprites.empty()
        
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
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.drop_sprites, character=self.selected_character)
                self.gun = Gun(self.player, self.all_sprites)
                player_pos = (obj.x, obj.y)
            else:
                self.spawn_positions.append((obj.x, obj.y))
        if player_pos:
            self.spawn_positions = [
                pos for pos in self.spawn_positions
                if pygame.math.Vector2(pos).distance_to(pygame.math.Vector2(player_pos)) > 50
            ]

    def bullet_collision(self):
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    if self.impact_sound:
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

    def spawn_enemies(self, enemy_type, base_pos):
        if enemy_type == 'bat':
            num_bats = randint(2, 4)
            bats_to_spawn = min(num_bats, self.max_enemies_per_type - self.enemies_active['bat'])
            for _ in range(bats_to_spawn):
                offset_x = randint(-50, 50)
                offset_y = randint(-50, 50)
                spawn_pos = (base_pos[0] + offset_x, base_pos[1] + offset_y)
                spawn_pos = (
                    max(0, min(spawn_pos[0], WINDOW_WIDTH)),
                    max(0, min(spawn_pos[1], WINDOW_HEIGHT))
                )
                Enemy(spawn_pos, self.enemy_frames[enemy_type], 
                      (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, 
                      enemy_type, self, self.drop_sprites)
                self.enemies_active['bat'] += 1
        else:
            if self.enemies_active[enemy_type] < self.max_enemies_per_type:
                Enemy(base_pos, self.enemy_frames[enemy_type], 
                      (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites, 
                      enemy_type, self, self.drop_sprites)
                self.enemies_active[enemy_type] += 1

    def update_fog(self, dt):
        self.fog_timer += dt
        if self.fog_active:
            if self.fog_timer >= self.fog_active_duration:
                self.fog_active = False
                self.fog_timer = 0.0
        else:
            if self.fog_timer >= self.fog_inactive_duration:
                self.fog_active = True
                self.fog_timer = 0.0
        self.fog_offset += self.fog_scroll_speed * dt
        self.fog_offset.x %= WINDOW_WIDTH
        self.fog_offset.y %= WINDOW_HEIGHT
        if self.fog_active:
            fog_alpha = self.fog_base_alpha + self.fog_alpha_variation * math.sin(
                pygame.time.get_ticks() / 1000.0 * self.fog_alpha_speed
            )
            self.fog_surface.set_alpha(int(fog_alpha))
        else:
            self.fog_surface.set_alpha(0)

    def draw_fog(self):
        self.display_surface.blit(self.fog_surface, (self.fog_offset.x, self.fog_offset.y))
        self.display_surface.blit(self.fog_surface, (self.fog_offset.x - WINDOW_WIDTH, self.fog_offset.y))
        self.display_surface.blit(self.fog_surface, (self.fog_offset.x, self.fog_offset.y - WINDOW_HEIGHT))
        self.display_surface.blit(self.fog_surface, (self.fog_offset.x - WINDOW_WIDTH, self.fog_offset.y - WINDOW_HEIGHT))

    def run(self):
        self.reset_game()
        self.game_active = True
        # Iniciar la música si no está reproduciéndose
        if not pygame.mixer.music.get_busy():
            self.play_music()
        while self.running:
            dt = self.clock.tick() / 1000
            
            if self.paused:
                self.pause_music()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        self.stop_music()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.paused = False
                            self.game_active = True
                            self.unpause_music()
                        elif event.key == pygame.K_UP:
                            self.pause_selected_option = (self.pause_selected_option - 1) % len(self.pause_options)
                        elif event.key == pygame.K_DOWN:
                            self.pause_selected_option = (self.pause_selected_option + 1) % len(self.pause_options)
                        elif event.key == pygame.K_RETURN:
                            if self.pause_options[self.pause_selected_option] == 'Continuar':
                                self.paused = False
                                self.game_active = True
                                self.unpause_music()
                            elif self.pause_options[self.pause_selected_option] == 'Reiniciar':
                                self.reset_game()
                                self.game_active = True
                                # Reanudar la música si estaba pausada
                                self.unpause_music()
                            elif self.pause_options[self.pause_selected_option] == 'Menú Principal':
                                self.save_scores()
                                self.stop_music()
                                self.running = False
                                return
                self.draw_pause_menu()
                pygame.display.update()
                continue

            if self.game_over:
                self.stop_music()
                self.game_active = False
                self.draw_game_over()
                if pygame.time.get_ticks() - self.game_over_time >= self.game_over_duration:
                    self.stop_music()
                    return
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    self.stop_music()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game_active:
                        self.paused = True
                        self.game_active = False
                if event.type == self.enemy_event and self.game_active:
                    enemy_type = choice(['ghost', 'bat', 'skeleton'])
                    self.spawn_enemies(enemy_type, choice(self.spawn_positions))
                    
            if self.game_active:
                self.gun_timer()
                self.input()
                self.update_difficulty(dt)
                self.update_fog(dt)
                self.all_sprites.update(dt)
                self.drop_sprites.update(dt)
                self.bullet_collision()
                self.player_collision()
                self.update_score(dt)
            
            self.display_surface.fill('black')
            self.all_sprites.draw(self.player.rect.center)
            self.draw_fog()
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
                if hasattr(sprite, 'draw_health_bar') and sprite.death_time == 0 and hasattr(sprite, 'health'):
                    sprite.draw_health_bar(self.display_surface, self.all_sprites.offset)
            
            self.draw_score()
            pygame.display.update()
            
        self.stop_music()

if __name__ == "__main__":
    pygame.init()
    while True:
        try:
            pygame.mixer.music.stop()
        except pygame.error:
            pass
        game = Game()
        menu = Menu(game)
        if not menu.run(start_with_main_menu=True):
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass
            pygame.quit()
            break
        game.run()