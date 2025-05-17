import pygame
import os
from os.path import join

class Battery(pygame.sprite.Sprite):
    def __init__(self, pos, groups):
        super().__init__(groups)
        current_dir = os.path.dirname(__file__)
        self.image = pygame.Surface((20, 20))  # Tamaño inicial del sprite de batería
        self.image.fill((0, 255, 0))  # Color verde temporal
        self.rect = self.image.get_rect(center=pos)
    
    def update(self, *args):
        # Método que acepta cualquier número de argumentos, ignorando dt por ahora
        pass