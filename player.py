import pygame
import os
import random
from os.path import join
from settings import *
from battery import Battery  # Importar la clase Battery

class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, collision_sprites, battery_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'down', 0
        current_dir = os.path.dirname(__file__)
        self.image = pygame.image.load(join(current_dir, 'Resources', 'img', 'player', 'down', '0.png')).convert_alpha()        
        self.rect = self.image.get_rect(center=position)
        self.hitbox_rect = self.rect.inflate(-60, -60)
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites
        self.battery_sprites = battery_sprites  # Grupo de sprites de baterías
        self.light_radius = 150
        self.max_light_radius = 150
        self.light_duration = 30
        self.light_timer = self.light_duration
    
    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.frames.keys():
            current_dir = os.path.dirname(__file__)
            for folder_path, sub_folders, file_names in walk(os.path.join(current_dir, 'Resources', 'img', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda x: int(x.split('.')[0])):                   
                        full_path = os.path.join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()      
                        self.frames[state].append(surf)                                
    
    def input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
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
        self.frame_index += 5 * dt
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
    
    def update_light(self, dt):
        if self.light_timer > 0:
            self.light_timer -= dt
            base_radius = (self.light_timer / self.light_duration) * self.max_light_radius
            base_radius = max(50, base_radius)  # Mínimo funcional de 50 mientras light_timer > 0
            
            # Calcular porcentaje de carga basado directamente en light_timer
            self.light_charge = max(0, min(100, (self.light_timer / self.light_duration) * 100))
            
            # Añadir efecto de parpadeo si el radio base está por debajo de 90
            if base_radius <= 90:  # Parpadeo comienza a los 12 segundos y continúa hasta el final
                flicker = random.uniform(-0.1 * base_radius, 0.1 * base_radius)
                self.light_radius = base_radius + flicker
                self.light_radius = max(50, min(base_radius, self.light_radius))  # Mínimo de 50
            else:
                self.light_radius = base_radius
        else:
            self.light_radius = 0  # Apagar completamente cuando el tiempo se agote
            self.light_charge = 0
    
    def collect_battery(self):
        # Detectar colisión con baterías
        for battery in pygame.sprite.spritecollide(self, self.battery_sprites, True):
            self.light_timer = self.light_duration  # Recargar la linterna al máximo
    
    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.update_light(dt)
        self.collect_battery()  # Verificar y recolectar baterías
        
        # Ajustar velocidad según el estado de la linterna
        if self.light_radius == 0:
            self.speed = 250  # Reducir velocidad a la mitad cuando la linterna está apagada
        else:
            self.speed = 500  # Restaurar velocidad normal cuando la linterna está encendida