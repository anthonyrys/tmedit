from pge.types import Singleton

from pge.core import Input
from pge.core import Font
from pge.core import Sound

from pge.network import Client

import pygame
import typing
import time

@Singleton
class Core:
    '''
    The entrypoint for pge.
    '''

    def __init__(self, title: str, screen_dimensions: tuple[int, int], frame_rate: int,
                 flags: typing.Optional[int] = 0, icon: typing.Optional[str] = None,
                 mouse: typing.Optional[bool] = True, opengl: typing.Optional[bool] = False) -> None:
        '''
        Initializes the pygame library given a `title`, `screen_dimensions`, 
        `frame_rate`.

        Optionally, provide any display `flags`, an `icon` image, if the 
        `mouse` will be visible, or if the screen will be using an `opengl`
        context.
        '''

        pygame.init()
        pygame.mixer.init()

        pygame.display.set_caption(title)
        if icon:
            pygame.display.set_icon(icon)
        
        pygame.mouse.set_visible(mouse)

        self.title: str = title
        
        self.screen_dimensions: tuple[int, int] = screen_dimensions
        self.frame_rate: int = frame_rate

        self.mouse: bool = mouse
        self.opengl: bool = opengl
        self.quit: bool = False

        self.screen: pygame.Surface = pygame.display.set_mode(screen_dimensions, flags)
        self.screen_color: tuple[int, int, int] = (0, 0, 0)

        self.clock: pygame.Clock = pygame.time.Clock()

        self.delta_time: float = time.time()
        self.last_time: float = time.time()
        self.frame_count: float = 0

        self.events: list[pygame.Event] = None
        
        self.input_service: Input = Input()
        self.font_service: Font = Font()
        self.sound_service: Sound = Sound()
        
    def __del__(self) -> None:
        '''
        Deinitializes the pygame modules.
        '''

        pygame.mixer.quit()
        pygame.quit()

    def run(self, func: typing.Optional[typing.Callable] = None, *args: typing.Sequence[any]) -> None:
        '''
        Run the main loop.

        Polls pygame events, calculates delta time, and maintains frame rate.

        In addition, can run a given `func` and it's `args` each loop.
        '''

        while not self.quit:
            self.events = pygame.event.get()
            self.quit = self.input_service._run(self.events)
            
            self.delta_time = (time.time() - self.last_time) * self.frame_rate
            self.last_time = time.time()

            self.frame_count += 1 * self.delta_time
            
            if func:
                func(*args)

            pygame.display.flip()
            self.clock.tick(self.frame_rate)

        if Client.instanced:
            Client().kill()
