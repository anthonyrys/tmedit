from pge.types import Singleton

import pygame
import typing

FuncInfo = typing.NewType('FuncInfo', tuple[typing.Sequence[any], typing.Union[None, int, typing.Sequence[int]]])

@Singleton
class Input:
    '''
    Singleton class for handling pygame inputs
    '''

    def __init__(self) -> None:
        self.pressed: pygame.key.ScancodeWrapper = None

        self._keydown_funcs: dict[callable, FuncInfo] = {}
        self._keyup_funcs: dict[callable, FuncInfo] = {}

        self._itering = False
        self._del_funcs: dict[int, list[callable]] = {
            pygame.KEYDOWN: [],
            pygame.KEYUP: []
        }

    def _iter_funcs(self, key: int, funcs: dict[callable, FuncInfo]) -> None:
        '''
        Private function for handling the calling of all of the 
        connected `funcs` and removing them if they were disconnected 
        while iterating.

        The given function will be called with its given arguments as
        well as an input key.
        '''

        self._itering = True

        for func, info in funcs.items():
            if isinstance(info[1], typing.Sequence):
                if key in info[1]:
                    try:
                        func(*info[0], key)
                    except TypeError:
                        func(*info[0])    
        
            elif not info[1] or info[1] == key:
                try:
                    func(*info[0], key)
                except TypeError:
                    func(*info[0])    

        self._itering = False

        for key_type, funcs in self._del_funcs.items():
            for func in funcs:
                if key_type == pygame.KEYDOWN:
                    del self._keydown_funcs[func]
                elif key_type == pygame.KEYUP:
                    del self._keyup_funcs[func]    

        self._del_funcs[pygame.KEYDOWN].clear()   
        self._del_funcs[pygame.KEYUP].clear()

    def _run(self, events: list[pygame.Event]) -> bool:
        '''
        Ran every frame, handles all pygame `events`.
        '''

        for event in events:
            if event.type == pygame.QUIT:
                return True
            
            if event.type == pygame.KEYDOWN:
                self._iter_funcs(event.key, self._keydown_funcs)

            if event.type == pygame.KEYUP:
                self._iter_funcs(event.key, self._keyup_funcs)

        self.pressed = pygame.key.get_pressed()

        return False

    def connect(self, keys: typing.Union[None, int, typing.Sequence[int]],
                key_type: int, func: callable, *args: typing.Sequence[any]) -> None:
        '''
        Connect a function to the input service.

        Takes a list of pygame `keys` you want the function to be
        called to (`None` if you want it to be ran regardless of 
        which input key).

        `key_type` to determine if it should be called on a keydown
        or keyup. An `AssertionError` will be raised if its not either
        `pygame.KEYDOWN` or `pygame.KEYUP`.

        The `func` you want to be called and its `args`.
        '''
        
        assert key_type == pygame.KEYDOWN or key_type == pygame.KEYUP

        if key_type == pygame.KEYDOWN:
            self._keydown_funcs[func] = (args, keys)
        elif key_type == pygame.KEYUP:
            self._keyup_funcs[func] = (args, keys)

    def disconnect(self, func: callable, key_type: int) -> None:
        '''
        Disconnect a function from the input service.

        Takes the `func` as well as a `key_type`. 
        
        An `AssertionError` will be raised if `key_type`
        is not either `pygame.KEYDOWN` or `pygame.KEYUP`.
        '''
                
        assert key_type == pygame.KEYDOWN or key_type == pygame.KEYUP
      
        if key_type == pygame.KEYDOWN:
            if not self._itering:
                del self._keydown_funcs[func]
            else:
                self._del_funcs[pygame.KEYDOWN].append(func)

        elif key_type == pygame.KEYUP:
            if not self._itering:
                del self._keyup_funcs[func]
            else:
                self._del_funcs[pygame.KEYUP].append(func)
