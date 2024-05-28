from pge.core import Core
from pge.utils import generate_import_dict, scale

from scripts import IMAGE_PATH
from scripts import Tile

import pygame
import pygame.gfxdraw
import os

class Tool:
    def __init__(self, tmedit, keybind):
        assert Core.instanced
        self.core = Core()
        self.tmedit = tmedit

        self.keybind = keybind
        self.image = scale(pygame.image.load(os.path.join(IMAGE_PATH, 'tools', f'{self.__class__.__name__.lower()}.png')), 2)

    def on_mouse_down(self, event):
        ...

    def on_mouse_up(self, event):
        ...

    def undo(self, action):
        ...
        
    def update(self):
        ...
    
    def render_pre(self):
        ...

    def render_post(self):
        if not pygame.mouse.get_focused():
            return False

        self.core.screen.blit(self.image, self.image.get_rect(center=pygame.mouse.get_pos()))

class Move(Tool):
    def __init__(self, tmedit):
        super().__init__(tmedit, pygame.K_ESCAPE)

    def on_mouse_down(self, event):
        if event.button != 1 or self.tmedit.mouse_down:
            return
        
        self.tmedit.mouse_down = True
        self.tmedit.offset_anchor = pygame.Vector2(pygame.mouse.get_pos())
    
    def on_mouse_up(self, event):
        if event.button != 1 or not self.tmedit.mouse_down:
            return

        self.tmedit.mouse_down = False  
        position = pygame.mouse.get_pos()

        x = position[0] - self.tmedit.offset_anchor.x
        y = position[1] - self.tmedit.offset_anchor.y

        self.tmedit.offset.x += x
        self.tmedit.offset.y += y

        if self.tmedit.viewport.x == 0 and self.tmedit.offset.x > 0:
            self.tmedit.offset.x = 0

        if self.tmedit.viewport.x == -self.tmedit.tilemap.bounds.x and self.tmedit.offset.x < -self.tmedit.tilemap.bounds.x:
            self.tmedit.offset.x = -self.tmedit.tilemap.bounds.x

        if self.tmedit.viewport.y == 0 and self.tmedit.offset.y > 0:
            self.tmedit.offset.y = 0

        if self.tmedit.viewport.y == -self.tmedit.tilemap.bounds.y and self.tmedit.offset.y < -self.tmedit.tilemap.bounds.y:
            self.tmedit.offset.y = -self.tmedit.tilemap.bounds.y

        self.tmedit.offset_anchor = pygame.Vector2()

    def update(self):   
        if not self.tmedit.mouse_down:
            return
        
        position = pygame.mouse.get_pos()

        x = position[0] - self.tmedit.offset_anchor.x
        y = position[1] - self.tmedit.offset_anchor.y

        self.tmedit.viewport.x = self.tmedit.offset.x + x
        self.tmedit.viewport.y = self.tmedit.offset.y + y

class Brush(Tool):
    def __init__(self, tmedit):
        super().__init__(tmedit, pygame.K_b)

    def on_mouse_down(self, event):
        if event.button != 1 or not self.tmedit.mouse_focus:
            return
        
        selected = self.tmedit.sidebar.selected
        dimensions = self.tmedit.tilemap.data['config']['tile']['dimensions']

        chunks = [c for c in self.tmedit.renderable_chunks if self.tmedit.tilemap.chunks[c][0].collidepoint(self.tmedit.mouse_position)]
        
        if self.tmedit.modes['snapping']:
            position = ((dimensions[0] * round(self.tmedit.mouse_position.x / dimensions[0])), (dimensions[1] * round(self.tmedit.mouse_position.y / dimensions[1])))
            for tile in self.tmedit.tilemap.chunks[chunks[0]][1]:
                if tile.position == position and tile.strata == self.tmedit.settings['strata']:
                    return

        else:
            position = self.tmedit.mouse_position

        image = self.tmedit.tilemap.images[selected['tileset']][selected['index']]
        image = pygame.transform.rotate(image, -self.tmedit.settings['orientation'])
        image = pygame.transform.flip(image, self.tmedit.settings['flipped'], False)  

        tile = Tile(image, image.get_size(), self.tmedit.settings['flipped'], selected['index'], self.tmedit.settings['orientation'], 
                    position, self.tmedit.settings['strata'], selected['tile'], selected['tileset'])

        self.tmedit.tilemap.chunks[chunks[0]][1].append(tile)
        self.tmedit.actions.append(('brush', (chunks[0], tile)))

    def undo(self, action):
        self.tmedit.tilemap.chunks[action[1][0]][1].remove(action[1][1])
        
    def render_pre(self):
        if not self.tmedit.mouse_focus:
            return
        
        image = self.tmedit.tilemap.images[self.tmedit.sidebar.selected['tileset']][self.tmedit.sidebar.selected['index']]
        image = pygame.transform.rotate(image, -self.tmedit.settings['orientation'])
        image = pygame.transform.flip(image, self.tmedit.settings['flipped'], False)

        dimensions = self.tmedit.tilemap.data['config']['tile']['dimensions']

        if self.tmedit.modes['snapping']:
            position = ((dimensions[0] * round(self.tmedit.mouse_position.x / dimensions[0])), (dimensions[1] * round(self.tmedit.mouse_position.y / dimensions[1])))
        else:
            position = self.tmedit.mouse_position

        self.tmedit.tilemap.surface.blit(image, position)

        image = pygame.mask.from_surface(image).to_surface(setcolor=(255, 255, 255, 55), unsetcolor=(0, 0, 0, 0))
        self.tmedit.tilemap.surface.blit(image, position)

class Erase(Tool):
    def __init__(self, tmedit):
        super().__init__(tmedit, pygame.K_e)
                    
    def on_mouse_down(self, event):
        if event.button != 1 or not self.tmedit.mouse_focus:
            return
        
        selected = self.get_selected()
        if not selected:
            return
        
        self.tmedit.tilemap.chunks[selected[0]][1].remove(selected[1])
        self.tmedit.actions.append(('erase', selected))

    def get_selected(self):
        chunks = [c for c in self.tmedit.renderable_chunks if self.tmedit.tilemap.chunks[c][0].collidepoint(self.tmedit.mouse_position)]

        for chunk in chunks:
            tiles = self.tmedit.tilemap.chunks[chunk][1]
            for tile in tiles:
                if tile.rect.collidepoint(self.tmedit.mouse_position) and tile.strata == self.tmedit.settings['strata']:
                    return (chunk, tile)
                
    def undo(self, action):
        self.tmedit.tilemap.chunks[action[1][0]][1].append(action[1][1])

    def render_pre(self):
        if not self.tmedit.mouse_focus:
            return
        
        selected = self.get_selected()
        if not selected:
            return
        
        image = pygame.mask.from_surface(selected[1].image).to_surface(setcolor=(255, 0, 0, 55), unsetcolor=(0, 0, 0, 0))
        self.tmedit.tilemap.surface.blit(image, selected[1].position)

TOOLS = generate_import_dict('Tool', 'Tile')
