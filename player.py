import pygame
import os
import random
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, position, groups, collision_sprites, drop_sprites, character="veronica"):
        """
        Inicializa una instancia de la clase Player.
        Args:
            position (tuple): Coordenadas iniciales (x, y) del jugador.
            groups (iterable): Grupos de sprites a los que pertenece el jugador.
            collision_sprites (iterable): Sprites con los que el jugador puede colisionar.
            drop_sprites (iterable): Sprites que el jugador puede soltar o interactuar.
            character (str, opcional): Nombre del personaje que se utilizará. Por defecto es "veronica".
        Atributos:
            character (str): Nombre del personaje.
            state (str): Estado inicial del jugador, por defecto 'down'.
            frame_index (int): Índice del fotograma inicial, por defecto 0.
            image (Surface): Imagen inicial del jugador.
            rect (Rect): Rectángulo que define la posición del jugador.
            hitbox_rect (Rect): Rectángulo de colisión ajustado para el jugador.
            direction (Vector2): Dirección del movimiento del jugador.
            speed (int): Velocidad del jugador.
            collision_sprites (iterable): Sprites con los que el jugador puede colisionar.
            drop_sprites (iterable): Sprites que el jugador puede soltar o interactuar.
            light_radius (int): Radio inicial de luz del jugador.
            max_light_radius (int): Radio máximo de luz del jugador.
            light_duration (int): Duración de la luz en fotogramas.
            light_timer (int): Temporizador de la luz.
            max_health (int): Salud máxima del jugador.
            health (int): Salud actual del jugador.
            invulnerability_timer (int): Temporizador de invulnerabilidad.
            invulnerability_duration (int): Duración de la invulnerabilidad en milisegundos.
            countdown_active (bool): Indica si el temporizador de cuenta regresiva está activo.
        """
        
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
        # carga las imagenes a utilizar segun la direccion del personaje
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
        # calcula el movimiento del personaje
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def collision(self, direction):
        """
        Detecta y maneja las colisiones entre el jugador y los sprites en la dirección especificada.
        Args:
            direction (str): Dirección del movimiento del jugador. Puede ser 'horizontal' o 'vertical'.
        Comportamiento:
            - Si la dirección es 'horizontal', ajusta la posición del rectángulo de colisión del jugador
              (hitbox_rect) para evitar superposiciones con los sprites en la dirección x.
            - Si la dirección es 'vertical', ajusta la posición del rectángulo de colisión del jugador
              (hitbox_rect) para evitar superposiciones con los sprites en la dirección y.
        Notas:
            - La detección de colisiones se realiza utilizando el método `colliderect` de los rectángulos.
            - La posición del rectángulo de colisión del jugador se ajusta dependiendo de la dirección
              del movimiento (positiva o negativa) en los ejes x o y.
        """
        
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
        """
        Actualiza el estado de la luz del jugador en función del tiempo y otros parámetros.
        Args:
            dt (float): Delta de tiempo transcurrido desde la última actualización.
        Comportamiento:
            - Si el temporizador de cuenta regresiva está activo (`countdown_active`), 
              la luz se establece con carga completa (`light_charge = 100`) y el radio máximo (`light_radius = max_light_radius`).
            - Si el temporizador de luz (`light_timer`) es mayor que 0:
                - Reduce el temporizador de luz en función del delta de tiempo.
                - Calcula el radio base de la luz proporcional al tiempo restante.
                - Ajusta la carga de la luz proporcional al tiempo restante.
                - Si el radio base es menor o igual a 90, aplica un efecto de parpadeo aleatorio.
                - Si el radio base es mayor que 90, utiliza el radio base directamente.
            - Si el temporizador de luz ha expirado (`light_timer <= 0`):
                - Establece el radio de la luz y la carga en 0.
        Notas:
            - El radio de la luz y la carga están limitados a valores mínimos y máximos para evitar valores fuera de rango.
            - El efecto de parpadeo se aplica solo cuando el radio base es menor o igual a 90.
        """
        
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
        """
        Maneja la recolección de objetos ("drops") por parte del jugador.
        Este método verifica las colisiones entre el jugador y los objetos 
        disponibles en el grupo `drop_sprites`. Si se detecta una colisión, 
        el objeto se elimina del grupo y se aplica su efecto correspondiente 
        al jugador según su tipo.
        Tipos de objetos y efectos:
        - 'health': Incrementa la salud del jugador hasta un máximo del 20% 
          de su salud máxima (`max_health`).
        - 'battery': Restaura el temporizador de luz del jugador al valor 
          máximo (`light_duration`).
        Returns:
            None
        """
        
        for drop in pygame.sprite.spritecollide(self, self.drop_sprites, True):
            if drop.drop_type == 'health':
                self.health = min(self.max_health, self.health + 0.2 * self.max_health)
            elif drop.drop_type == 'battery':
                self.light_timer = self.light_duration

    def take_damage(self, damage):
        """
        Aplica daño al jugador, reduciendo su salud si no está en estado de invulnerabilidad.
        Args:
            damage (int): La cantidad de daño que se aplicará al jugador.
        Notas:
            - Si el temporizador de invulnerabilidad (`invulnerability_timer`) es menor o igual a 0, 
              el daño se aplica directamente a la salud del jugador.
            - La salud del jugador no puede ser menor que 0.
            - Después de recibir daño, se reinicia el temporizador de invulnerabilidad 
              al valor de `invulnerability_duration`.
        """
        
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