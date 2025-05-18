from settings import *
from math import atan2, degrees

class Sprite(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        """
        Inicializa un sprite básico con una imagen y posición.
        Args:
            position (tuple): Posición inicial del sprite.
            surface (pygame.Surface): Imagen del sprite.
            groups (iterable): Grupos de sprites a los que pertenece.
        """
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        self.ground = True  # Indica si el sprite está en el suelo

class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, position, surface, groups):
        """
        Inicializa un sprite de colisión con una imagen y posición.
        Args:
            position (tuple): Posición inicial del sprite.
            surface (pygame.Surface): Imagen del sprite.
            groups (iterable): Grupos de sprites a los que pertenece.
        """
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft=position)
        
class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        """
        Inicializa el arma del jugador.
        Args:
            player (pygame.sprite.Sprite): Referencia al jugador.
            groups (iterable): Grupos de sprites a los que pertenece.
        """
        # Conexión con el jugador
        self.player = player
        self.distance = 140  # Distancia del arma respecto al jugador
        self.player_direction = pygame.Vector2(0, 1)  # Dirección inicial
        
        # Configuración del sprite del arma
        super().__init__(groups)
        self.gun_surface = pygame.image.load(join('Resources', 'img', 'gun', 'gun.png')).convert_alpha()
        self.image = self.gun_surface
        self.rect = self.image.get_rect(center = self.player.rect.center + self.player_direction * self.distance)
        
    def get_direction(self):
        """
        Calcula la dirección del arma en función de la posición del mouse respecto al centro de la pantalla.
        """
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())  # Posición del mouse
        player_pos= pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)  # Centro de la pantalla
        self.player_direction = (mouse_pos - player_pos).normalize()  # Vector dirección
        
    def rotate_gun(self):
        """
        Rota la imagen del arma para que apunte hacia la dirección calculada.
        """
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90  # Ángulo de rotación
        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surface, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surface, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)  # Voltea el arma si apunta a la izquierda
        
    def update(self, _):
        """
        Actualiza la dirección, rotación y posición del arma en cada frame.
        """
        self.get_direction()  # Actualiza la dirección
        self.rotate_gun()    # Rota el sprite
        self.rect.center = self.player.rect.center + self.player_direction * self.distance  # Posiciona el arma
    
class Bullet(pygame.sprite.Sprite):
    def __init__(self, surface, position, direction, groups):
        """
        Inicializa una bala disparada por el arma.
        Args:
            surface (pygame.Surface): Imagen de la bala.
            position (tuple): Posición inicial de la bala.
            direction (pygame.Vector2): Dirección de movimiento.
            groups (iterable): Grupos de sprites a los que pertenece.
        """
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(center=position)
        self.spawn_time = pygame.time.get_ticks()  # Tiempo de creación
        self.lifetime = 1000  # Vida útil de la bala en milisegundos
        
        self.direction = direction  # Dirección de movimiento
        self.speed = 1200  # Velocidad de la bala
        
    def update(self, dt):
        """
        Actualiza la posición de la bala y la elimina si ha pasado su tiempo de vida.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        self.rect.center += self.direction * self.speed * dt  # Mueve la bala
        
        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()  # Elimina la bala si ha pasado su vida útil
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, frames, groups, player, collision_sprites):
        """
        Inicializa un enemigo que persigue al jugador y puede colisionar con obstáculos.
        Args:
            position (tuple): Posición inicial del enemigo.
            frames (list): Lista de imágenes para la animación.
            groups (iterable): Grupos de sprites a los que pertenece.
            player (pygame.sprite.Sprite): Referencia al jugador.
            collision_sprites (iterable): Sprites con los que puede colisionar.
        """
        super().__init__(groups)
        self.player = player
        
        # Animación
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.animate_speed = 6  # Velocidad de animación
        
        # Rectángulos para colisión y posición
        self.rect = self.image.get_rect(center=position)
        self.hitbox_rect = self.rect.inflate(-20, -40)  # Rectángulo reducido para colisiones
        self.collision_sprites = collision_sprites
        self.direction = pygame.Vector2()  # Dirección de movimiento
        self.speed = 200  # Velocidad del enemigo
        
        # Temporizador de muerte
        self.death_time = 0
        self.death_duration = 400  # Tiempo antes de eliminar tras morir
        
    def animate(self, dt):
        """
        Actualiza el frame de animación del enemigo según el tiempo transcurrido.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        self.frame_index += self.animate_speed * dt  # Avanza el índice de animación
        self.image = self.frames[int(self.frame_index) % len(self.frames)]  # Cambia la imagen
        
    def move(self, dt):
        """
        Mueve al enemigo hacia el jugador, gestionando colisiones.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        # Calcular dirección hacia el jugador
        player_pos = pygame.Vector2(self.player.rect.center)
        enemy_pos = pygame.Vector2(self.rect.center)
        self.direction = (player_pos - enemy_pos).normalize()
        
        # Mover en X y comprobar colisión
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        # Mover en Y y comprobar colisión
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center  # Actualizar posición visual
        
    def collision(self, direction):
        """
        Gestiona la colisión del enemigo con los sprites de colisión.
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
                    if self.direction.y < 0: self.hitbox_rect.top = sprite.rect.bottom    # Colisión arriba
        
    def destroy(self):
        """
        Inicia el proceso de destrucción del enemigo, cambiando su imagen y comenzando el temporizador de muerte.
        """
        # Iniciar temporizador de muerte
        self.death_time = pygame.time.get_ticks()
        
        # Cambiar la imagen a una silueta blanca
        surface = pygame.mask.from_surface(self.frames[0]).to_surface()
        surface.set_colorkey('black')
        self.image = surface
        
        
    def death_timer(self):
        """
        Elimina al enemigo si ha pasado el tiempo de muerte.
        """
        if pygame.time.get_ticks() - self.death_time >= self.death_duration:
            self.kill()  # Elimina el sprite del grupo
        
    def update(self, dt):
        """
        Actualiza el estado del enemigo: movimiento, animación o muerte.
        Args:
            dt (float): Delta de tiempo desde el último frame.
        """
        if self.death_time == 0:
            self.move(dt)  # Si está vivo, se mueve y anima
            self.animate(dt)
        else:
            self.death_timer()  # Si está muriendo, espera para eliminarse
         