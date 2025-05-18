from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        """
        Grupo personalizado de sprites que permite dibujar todos los sprites con un offset basado en la posición del objetivo (por ejemplo, el jugador).
        """
        super().__init__()
        self.display_surface = pygame.display.get_surface()  # Superficie donde se dibujan los sprites
        self.offset = pygame.Vector2()  # Offset para centrar la cámara en el objetivo
        
    def draw(self, target_position):
        """
        Dibuja todos los sprites del grupo aplicando un offset para centrar la vista en la posición objetivo.
        Separa los sprites en dos capas: suelo y objetos, y los dibuja en orden de profundidad (eje Y).
        Args:
            target_position (tuple): Posición (x, y) del objetivo a centrar (usualmente el jugador).
        """
        # Calcular el offset para centrar la cámara en el objetivo
        self.offset.x = -(target_position[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_position[1] - WINDOW_HEIGHT / 2)
        
        # Separar sprites de suelo y objetos según el atributo 'ground'
        ground_sprites = [sprite for sprite in self if hasattr(sprite, 'ground')]
        object_sprites = [sprite for sprite in self if not hasattr(sprite, 'ground')]
        
        # Dibujar primero el suelo y luego los objetos, ordenados por la coordenada Y (profundidad)
        for layer in [ground_sprites, object_sprites]:            
            for sprite in sorted(layer, key=lambda sprite: sprite.rect.centery):
                self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)  # Dibujar sprite con offset
    