import pygame
from settings import *

class Drop(pygame.sprite.Sprite):
    def __init__(self, pos, groups, drop_type):
        """
        Inicializa un objeto de drop (salud o batería) en la posición dada.
        Args:
            pos (tuple): Posición inicial del drop (x, y).
            groups (iterable): Grupos de sprites a los que pertenece.
            drop_type (str): Tipo de drop ('health' o 'battery').
        """
        super().__init__(groups)
        self.drop_type = drop_type
        if drop_type == 'health':
            self.image = pygame.image.load(join('Resources', 'img', 'drop', 'Health.png')).convert_alpha()
        elif drop_type == 'battery':
            self.image = pygame.image.load(join('Resources', 'img', 'drop', 'Battery.png')).convert_alpha()
        
        self.image = pygame.transform.scale(self.image, (60, 60))
        
        self.rect = self.image.get_rect(center=pos)
    
    def update(self, *args):
        """
        Método de actualización, por ahora vacío ya que los drops son estáticos.
        """
        pass