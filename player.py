import pygame
import os
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, collision_sprites, drop_sprites, character="veronica"):
        super().__init__(groups)
        self.character = character
        self.load_images()
        self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(join('Resources', 'img', f'player{self.character.capitalize()}', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.hitbox_rect = self.rect.inflate(-60, -60)
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites
        self.drop_sprites = drop_sprites
        self.light_radius = 150
        self.max_light_radius = 150
        self.light_duration = 30
        self.light_timer = self.light_duration
        self.max_health = 200
        self.health = self.max_health
        self.invulnerability_timer = 0
        self.invulnerability_duration = 500
        self.countdown_active = False

    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('Resources', 'img', f'player{self.character.capitalize()}', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda x: int(x.split('.')[0])):
                        full_path = os.path.join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom

    def animate(self, dt):
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def reset_flashlight(self):
        self.light_timer = self.light_duration
        self.light_charge = 100
        self.light_radius = self.max_light_radius

    def update_light(self, dt):
        if self.countdown_active:
            self.light_charge = 100
            self.light_radius = self.max_light_radius
            return
        if self.light_timer > 0:
            self.light_timer -= dt
            base_radius = (self.light_timer / self.light_duration) * self.max_light_radius
            base_radius = max(50, base_radius)
            self.light_charge = max(0, min(100, (self.light_timer / self.light_duration) * 100))
            if base_radius <= 90:
                flicker = random.uniform(-0.1 * base_radius, 0.1 * base_radius)
                self.light_radius = base_radius + flicker
                self.light_radius = max(50, min(base_radius, self.light_radius))
            else:
                self.light_radius = base_radius
        else:
            self.light_radius = 0
            self.light_charge = 0

    def collect_drop(self):
        for drop in pygame.sprite.spritecollide(self, self.drop_sprites, True):
            if drop.drop_type == 'health':
                self.health = min(self.max_health, self.health + 0.2 * self.max_health)
            elif drop.drop_type == 'battery':
                self.light_timer = self.light_duration

    def take_damage(self, damage):
        if self.invulnerability_timer <= 0:
            self.health -= damage
            if self.health < 0:
                self.health = 0
            self.invulnerability_timer = self.invulnerability_duration

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.update_light(dt)
        self.collect_drop()
        if self.light_radius == 0:
            self.speed = 250
        else:
            self.speed = 500
        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= dt * 1000