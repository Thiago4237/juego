import pygame
import os
import random
from settings import *
from battery import Battery  # Importar la clase Battery

class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, collision_sprites, battery_sprites):
        """
        Inicializa el jugador, carga imágenes, define atributos de movimiento, colisión y linterna.
        Args:
            position (tuple): Posición inicial del jugador.
            groups (iterable): Grupos de sprites a los que pertenece.
            collision_sprites (iterable): Sprites con los que puede colisionar.
            battery_sprites (iterable): Sprites de baterías que puede recolectar.
        """
        super().__init__(groups)
        self.load_images()  # Cargar animaciones
        self.state, self.frame_index = 'down', 0
        self.image = pygame.image.load(join('Resources', 'img', 'player', 'down', '0.png')).convert_alpha()        
        self.rect = self.image.get_rect(center=position)
        self.hitbox_rect = self.rect.inflate(-60, -60)  # Rectángulo reducido para colisiones
        self.direction = pygame.Vector2()  # Dirección de movimiento
        self.speed = 500  # Velocidad inicial
        self.collision_sprites = collision_sprites
        self.battery_sprites = battery_sprites  # Grupo de sprites de baterías
        self.light_radius = 150  # Radio inicial de la linterna
        self.max_light_radius = 150  # Radio máximo de la linterna
        self.light_duration = 30  # Duración máxima de la linterna (segundos)
        self.light_timer = self.light_duration  # Temporizador de la linterna
    
    def load_images(self):
        """
        Carga los frames de animación del jugador para cada dirección.
        """
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}
        for state in self.frames.keys():            
            for folder_path, sub_folders, file_names in walk(join('Resources', 'img', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda x: int(x.split('.')[0])):                   
                        full_path = os.path.join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()      
                        self.frames[state].append(surf)                                
    
    def input(self):
        """
        Lee la entrada del teclado y actualiza la dirección de movimiento del jugador.
        """
        keys = pygame.key.get_pressed()
        # Movimiento horizontal: derecha (D o flecha derecha) menos izquierda (A o flecha izquierda)
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        # Movimiento vertical: abajo (S o flecha abajo) menos arriba (W o flecha arriba)
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction 
        
    def move(self, dt):
        """
        Mueve al jugador según la dirección y gestiona colisiones.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        self.hitbox_rect.x += self.direction.x * self.speed * dt  # Mover en X
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt  # Mover en Y
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center  # Actualizar posición visual
   
    def collision(self, direction):
        """
        Gestiona la colisión del jugador con los sprites de colisión.
        Args:
            direction (str): 'horizontal' o 'vertical' para indicar el eje de colisión.
        """
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0: self.hitbox_rect.right = sprite.rect.left  # Colisión derecha
                    if self.direction.x < 0: self.hitbox_rect.left = sprite.rect.right  # Colisión izquierda
                else:
                    if self.direction.y > 0: self.hitbox_rect.bottom = sprite.rect.top  # Colisión abajo
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom  # Colisión arriba
    
    def animate(self, dt):
        """
        Actualiza el frame de animación del jugador según la dirección y el tiempo transcurrido.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'
            
        # Avanza el frame si se está moviendo, si no, se queda en el primer frame
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0 
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]
    
    def update_light(self, dt):
        """
        Actualiza el estado de la linterna: radio, carga y parpadeo según el tiempo restante.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        if self.light_timer > 0:
            self.light_timer -= dt  # Disminuir temporizador
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
        """
        Detecta colisión con baterías y recarga la linterna al máximo si recoge una.
        """
        # Detectar colisión con baterías
        for battery in pygame.sprite.spritecollide(self, self.battery_sprites, True):
            self.light_timer = self.light_duration  # Recargar la linterna al máximo
    
    def update(self, dt):
        """
        Actualiza el estado del jugador: entrada, movimiento, animación, linterna y recolección de baterías.
        Ajusta la velocidad según el estado de la linterna.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        self.input()  # Leer entrada del usuario
        self.move(dt)  # Mover y gestionar colisiones
        self.animate(dt)  # Animar sprite
        self.update_light(dt)  # Actualizar linterna
        self.collect_battery()  # Verificar y recolectar baterías
        
        # Ajustar velocidad según el estado de la linterna
        if self.light_radius == 0:
            self.speed = 250  # Reducir velocidad a la mitad cuando la linterna está apagada
        else:
            self.speed = 500  # Restaurar velocidad normal cuando la linterna está encendida