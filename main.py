from settings import *
from player import *
from sprites import *
from os.path import join
from pytmx.util_pygame import load_pygame 
from groups import AllSprites
from battery import Battery

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Shadowed Forest")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.battery_sprites = pygame.sprite.Group()
        
        self.light_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.light_surface.fill((10, 10, 20))
        self.light_surface.set_alpha(230)
        
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
        
        for obj in map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites, self.battery_sprites)
        
        num_batteries = 7
        for _ in range(num_batteries):
            x = random.randint(0, WINDOW_WIDTH - 20)
            y = random.randint(0, WINDOW_HEIGHT - 20)
            Battery((x, y), (self.all_sprites, self.battery_sprites))
    
    def run(self):
        while self.running:
            dt = self.clock.tick() / 1000
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            self.all_sprites.update(dt)
            
            self.display_surface.fill('black')
            # Dibujar sprites con el offset basado en la posición del jugador
            self.all_sprites.draw(self.player.rect.center)
            
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
            
            pygame.draw.rect(self.display_surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            fill_color = (0, 255, 0) if current_charge > 20 else (255, 0, 0)
            fill_width = (current_charge / max_charge) * bar_width
            pygame.draw.rect(self.display_surface, fill_color, (bar_x, bar_y, fill_width, bar_height))
            
            pygame.display.update()
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()