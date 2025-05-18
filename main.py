from settings import *
from player import *
from sprites import *
from pytmx.util_pygame import load_pygame 
from groups import AllSprites
from random import randint, choice
from battery import Battery

class Game:
    def __init__(self):
        """
        Inicializa el juego, configurando la ventana, los grupos de sprites, los temporizadores, el audio y cargando los recursos necesarios.
        """
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Shadowed Forest")
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
        
        # Cargar imágenes y preparar el escenario
        self.load_images()
        self.setup()
        
    def load_images(self):
        """
        Carga las imágenes necesarias para las balas y los enemigos, organizando los frames de animación por tipo de enemigo.
        """
        self.bullet_surface = pygame.image.load(join('Resources', 'img', 'gun', 'bullet.png')).convert_alpha()
        
        # Cargar los frames de animación de cada tipo de enemigo
        folders = list(walk(join('Resources', 'img', 'enemies')))[0][1]
        self.enemy_frames = {}
        for folder in folders:
            for folder_path, _, file_names in walk(join('Resources', 'img', 'enemies', folder)):
                self.enemy_frames[folder] = []
                for file_name in sorted(file_names, key=lambda x: int(x.split('.')[0])):
                    full_path = join(folder_path, file_name)
                    surf = pygame.image.load(full_path).convert_alpha()
                    self.enemy_frames[folder].append(surf)
        
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
        
        # Crear jugador y guardar posiciones de spawn de enemigos
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.battery_sprites)
                self.gun = Gun(self.player, self.all_sprites)
            else:
                self.spawn_positions.append((obj.x, obj.y))
        
        # Colocar baterías en posiciones aleatorias
        num_batteries = 7
        for _ in range(num_batteries):
            x = random.randint(0, WINDOW_WIDTH - 20)
            y = random.randint(0, WINDOW_HEIGHT - 20)
            Battery((x, y), (self.all_sprites, self.battery_sprites))
    
    def bullet_collision(self):
        """
        Detecta colisiones entre balas y enemigos. Si hay colisión, destruye al enemigo y elimina la bala.
        """
        if self.bullet_sprites:
            for bullet in self.bullet_sprites:
                # Verificar colisión de cada bala con los enemigos
                collision_sprites = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False, pygame.sprite.collide_mask)
                if collision_sprites:
                    self.impact_sound.play()  # Sonido de impacto
                    for sprite in collision_sprites:
                        sprite.destroy()  # Destruir enemigo
                    bullet.kill()  # Eliminar bala
    
    def player_collision(self):
        """
        Detecta colisiones entre el jugador y los enemigos. Si ocurre, termina el juego.
        """
        if pygame.sprite.spritecollide(self.player, self.enemy_sprites, False, pygame.sprite.collide_mask):
            self.running = False  # Fin del juego
    
    def run(self):
        """
        Bucle principal del juego. Gestiona eventos, actualizaciones de sprites, colisiones, renderizado y HUD.
        """
        while self.running:
            dt = self.clock.tick() / 1000  # Delta de tiempo para animaciones y movimientos
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False  # Salir del juego
                
                if event.type == self.enemy_event:
                    # Crear un nuevo enemigo en una posición aleatoria
                    Enemy(choice(self.spawn_positions), choice(list(self.enemy_frames.values())), (self.all_sprites, self.enemy_sprites), self.player, self.collision_sprites)
                   
            self.gun_timer()  # Actualizar cooldown del arma
            self.input()  # Procesar entrada del jugador
            self.all_sprites.update(dt)  # Actualizar todos los sprites
            self.bullet_collision()  # Verificar colisiones de balas
            self.player_collision()  # Verificar colisión del jugador
            
            self.display_surface.fill('black')  # Limpiar pantalla
            # Dibujar sprites con el offset basado en la posición del jugador
            self.all_sprites.draw(self.player.rect.center)
            
            # Simular la linterna y la oscuridad
            self.light_surface.fill((10, 10, 20))
            light_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            pygame.draw.circle(self.light_surface, (255, 255, 255), light_pos, self.player.light_radius)
            self.light_surface.set_colorkey((255, 255, 255))
            self.display_surface.blit(self.light_surface, (0, 0))
            
            # Dibujar barra de carga de la linterna (HUD, sin offset)
            bar_width = 200
            bar_height = 20
            bar_x = 10
            bar_y = 10
            max_charge = 100
            current_charge = self.player.light_charge
            
            pygame.draw.rect(self.display_surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))  # Fondo de la barra
            fill_color = (0, 255, 0) if current_charge > 20 else (255, 0, 0)  # Verde si hay carga, rojo si es baja
            fill_width = (current_charge / max_charge) * bar_width
            pygame.draw.rect(self.display_surface, fill_color, (bar_x, bar_y, fill_width, bar_height))  # Barra de carga
            
            pygame.display.update()  # Actualizar pantalla
            
        pygame.quit()  # Salir de pygame

if __name__ == "__main__":
    game = Game()
    game.run()