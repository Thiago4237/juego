from settings import *
from math import atan2, degrees
import pygame
import random
from drop import Drop

class Sprite(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.ground = True

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)

class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(0, 1)
        super().__init__(groups)
        self.gun_surface = pygame.image.load(join('Resources', 'img', 'gun', 'gun.png')).convert_alpha()
        self.image = self.gun_surface
        self.rect = self.image.get_rect(center=self.player.rect.center + self.player_direction * self.distance)
        
    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        direction_vector = mouse_pos - player_pos
        if direction_vector.length() > 0:
            self.player_direction = direction_vector.normalize()
        
    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surface, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surface, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)
        
    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = self.player.rect.center + self.player_direction * self.distance

class Bullet(pygame.sprite.Sprite):
    def __init__(self, surface, position, direction, groups):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000
        self.direction = direction
        self.speed = 1200
        
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, frames, groups, player, collision_sprites, enemy_type, game, drop_sprites):
        super().__init__(groups)
        self.player = player
        self.enemy_type = enemy_type
        self.game = game
        self.drop_sprites = drop_sprites
        
        if enemy_type == 'ghost':
            self.base_speed = 200
            self.base_damage_percent = 0.05
            self.max_damage_percent = 0.20
            self.max_health = 50
        elif enemy_type == 'bat':
            self.base_speed = 300
            self.base_damage_percent = 0.03
            self.max_damage_percent = 0.15
            self.max_health = 20
        elif enemy_type == 'skeleton':
            self.base_speed = 160
            self.base_damage_percent = 0.1
            self.max_damage_percent = 0.25
            self.max_health = 100
        
        self.speed = self.base_speed * (1 + 0.1 * game.difficulty_level)
        damage_percent = self.base_damage_percent * (1 + 0.03 * game.difficulty_level)
        damage_percent = min(damage_percent, self.max_damage_percent)
        self.damage = damage_percent * player.max_health
        
        self.health = self.max_health
        
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animate_speed = 6
        self.rect = self.image.get_rect(center=position)
        self.hitbox_rect = self.rect.inflate(-20, -40)
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()
        self.death_time = 0
        self.death_duration = 200
        
    def animate(self, dt):
        self.frame_index += self.animate_speed * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        
    def move(self, dt):
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        direction_vector = player_pos - enemy_pos
        if direction_vector.length() > 0:
            self.direction = direction_vector.normalize()
        else:
            self.direction = pygame.Vector2(0, 0)
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center
        
    def collision(self, direction):
        if self.enemy_type != 'ghost':
            for sprite in self.collision_sprites:
                if sprite.rect.colliderect(self.hitbox_rect):
                    if direction == 'horizontal':
                        if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                        if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                    else:
                        if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                        if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom
    
    def take_damage(self, damage):
        if self.death_time == 0:
            self.health -= damage
            if self.health <= 0:
                self.destroy()
                
    def destroy(self):
        self.game.update_score(0, self.enemy_type)
        self.death_time = pygame.time.get_ticks()
        surface = pygame.mask.from_surface(self.frames[0]).to_surface()
        surface.set_colorkey('black')
        self.image = surface
        # print(f"{self.enemy_type.capitalize()} destruido, activos: {self.game.enemies_active[self.enemy_type]}")
        drop_probability = self.game.get_drop_probability()
        if random.random() < drop_probability:
            drop_type = random.choices(['health', 'battery'], weights=[0.5, 0.5])[0]
            Drop(self.rect.center, (self.game.all_sprites, self.drop_sprites), drop_type)
        
    def death_timer(self):
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()
    
    def draw_health_bar(self, surface, offset):
        if not hasattr(self, 'health') or not hasattr(self, 'max_health'):
            return
        bar_width = 50
        bar_height = 5
        bar_x = self.rect.centerx - bar_width // 2 + offset.x
        bar_y = self.rect.top - 10 + offset.y
        health_ratio = self.health / self.max_health
        fill_width = bar_width * health_ratio
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        fill_color = (0, 255, 0) if health_ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
    
    def update(self, dt):
        if self.death_time == 0:
            self.move(dt)
            self.animate(dt)
        else:
            self.death_timer()