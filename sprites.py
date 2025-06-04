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
        """
        Calcula la dirección del jugador hacia la posición del mouse.
        Utiliza las coordenadas actuales del mouse y la posición central del jugador
        en la ventana para determinar un vector de dirección. Si el vector tiene una
        longitud mayor a cero, se normaliza para obtener una dirección unitaria.
        Atributos modificados:
        - self.player_direction: Vector unitario que indica la dirección hacia el mouse.
        Requisitos:
        - La función asume que las constantes WINDOW_WIDTH y WINDOW_HEIGHT están definidas
          y representan las dimensiones de la ventana del juego.
        - pygame debe estar correctamente inicializado y el mouse debe estar activo.
        """
        
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        direction_vector = mouse_pos - player_pos
        if direction_vector.length() > 0:
            self.player_direction = direction_vector.normalize()
        
    def rotate_gun(self):
        """
        Rota el arma del jugador según la dirección en la que se mueve.
        Calcula el ángulo de rotación basado en la dirección del jugador 
        utilizando la función atan2 y lo ajusta con un desplazamiento de -90 grados 
        para alinear correctamente la imagen del arma. Si la dirección en el eje x 
        es positiva, rota la imagen normalmente. Si la dirección en el eje x es negativa, 
        rota la imagen con el valor absoluto del ángulo y luego invierte la imagen verticalmente.
        Modifica:
            self.image: Actualiza la imagen del arma con la rotación y/o inversión aplicadas.
        Dependencias:
            - pygame.transform.rotozoom: Para rotar y escalar la imagen.
            - pygame.transform.flip: Para invertir la imagen verticalmente.
            - math.degrees: Para convertir el ángulo de radianes a grados.
            - math.atan2: Para calcular el ángulo basado en las coordenadas x e y.
        Variables:
            - angle (float): Ángulo calculado para la rotación del arma.
        """
        
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
        """
        Inicializa una instancia de un enemigo en el juego.
        Args:
            position (tuple): Posición inicial del enemigo en el juego (x, y).
            frames (list): Lista de fotogramas para la animación del enemigo.
            groups (pygame.sprite.Group): Grupos de sprites a los que pertenece el enemigo.
            player (Player): Referencia al jugador para calcular daño y otras interacciones.
            collision_sprites (pygame.sprite.Group): Grupo de sprites con los que el enemigo puede colisionar.
            enemy_type (str): Tipo de enemigo ('ghost', 'bat', 'skeleton').
            game (Game): Referencia al objeto principal del juego para acceder a configuraciones como el nivel de dificultad.
            drop_sprites (pygame.sprite.Group): Grupo de sprites que representan objetos que el enemigo puede soltar al morir.
        Atributos:
            base_speed (int): Velocidad base del enemigo según su tipo.
            base_damage_percent (float): Porcentaje base de daño que el enemigo inflige al jugador.
            max_damage_percent (float): Porcentaje máximo de daño que el enemigo puede infligir.
            max_health (int): Salud máxima del enemigo según su tipo.
            speed (float): Velocidad ajustada según el nivel de dificultad del juego.
            damage (float): Daño ajustado según el nivel de dificultad del juego y limitado por el porcentaje máximo.
            health (int): Salud actual del enemigo.
            frames (list): Fotogramas de animación del enemigo.
            frame_index (int): Índice actual del fotograma en la animación.
            image (pygame.Surface): Imagen actual del enemigo.
            animate_speed (int): Velocidad de animación del enemigo.
            rect (pygame.Rect): Rectángulo que define la posición y tamaño del enemigo.
            hitbox_rect (pygame.Rect): Rectángulo de colisión del enemigo.
            collision_sprites (pygame.sprite.Group): Grupo de sprites con los que el enemigo puede colisionar.
            direction (pygame.Vector2): Dirección de movimiento del enemigo.
            death_time (int): Tiempo en milisegundos desde que el enemigo murió.
            death_duration (int): Duración en milisegundos de la animación de muerte del enemigo.
        """
        
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
        """
        Mueve al enemigo hacia el jugador basado en su posición actual y dirección calculada.
        Args:
            dt (float): Delta de tiempo utilizado para ajustar la velocidad del movimiento.
        Descripción:
        - Calcula un vector de dirección desde la posición del enemigo hacia la posición del jugador.
        - Normaliza el vector de dirección para obtener una dirección unitaria.
        - Actualiza la posición del rectángulo de colisión (hitbox_rect) en los ejes horizontal y vertical.
        - Verifica colisiones en ambos ejes mediante los métodos 'collision'.
        - Ajusta la posición del rectángulo principal (rect) para que coincida con el centro del rectángulo de colisión.
        """
        
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
        """
        Maneja la lógica de colisión para un objeto en movimiento.
        Este método verifica si el objeto actual colisiona con otros sprites en la dirección especificada 
        y ajusta la posición del objeto en consecuencia. Si el tipo de enemigo es 'ghost', no se realiza 
        ninguna verificación de colisión.
        Args:
            direction (str): Dirección del movimiento, puede ser 'horizontal' o 'vertical'.
        Comportamiento:
            - Si la dirección es 'horizontal', ajusta la posición del rectángulo de colisión en el eje X 
              dependiendo de si el objeto se mueve hacia la derecha o hacia la izquierda.
            - Si la dirección es 'vertical', ajusta la posición del rectángulo de colisión en el eje Y 
              dependiendo de si el objeto se mueve hacia arriba o hacia abajo.
        Nota:
            Este método asume que los sprites con los que se verifica la colisión tienen un atributo `rect` 
            que define su área de colisión.
        """
        
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
        """
        Destruye el objeto enemigo y realiza las siguientes acciones:
        - Actualiza la puntuación del juego según el tipo de enemigo.
        - Registra el tiempo de destrucción utilizando `pygame.time.get_ticks()`.
        - Genera una nueva superficie basada en la máscara del primer fotograma del enemigo y 
          establece el color negro como transparente.
        - Calcula la probabilidad de soltar un objeto (drop) y, si se cumple, crea un objeto 
          de tipo 'health' o 'battery' en la posición del enemigo destruido.
        Args:
            No recibe argumentos directamente, pero utiliza atributos del objeto como 
            `self.game`, `self.enemy_type`, `self.frames`, `self.rect.center`, y `self.drop_sprites`.
        Nota:
            Este método depende de las bibliotecas `pygame` y `random`, así como de la clase `Drop`.
        """
        
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
        """
        Dibuja una barra de salud sobre el sprite en la superficie proporcionada.
        Args:
            surface (pygame.Surface): La superficie donde se dibujará la barra de salud.
            offset (pygame.math.Vector2): Desplazamiento para ajustar la posición de la barra de salud.
        Notas:
            - La barra de salud se dibuja solo si el objeto tiene los atributos 'health' y 'max_health'.
            - La barra tiene un ancho fijo de 50 píxeles y una altura de 5 píxeles.
            - El color de la barra cambia según la proporción de salud:
              - Verde (0, 255, 0) si la proporción de salud es mayor a 0.3.
              - Rojo (255, 0, 0) si la proporción de salud es menor o igual a 0.3.
        """
        
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