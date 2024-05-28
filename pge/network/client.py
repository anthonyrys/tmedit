from pge.types import Singleton

import threading
import typing
import pickle
import socket
import time

@Singleton
class Client:
    '''
    Client singleton for the network socket.
    '''

    def __init__(self, ip: str, port: int, tick_rate: typing.Optional[int] = 120) -> None:
        '''
        Creates the `Client` instance.

        Takes the server `ip` address and `port`, as well as an 
        optional `tick_rate` for sending packets.
        '''

        self.BUFFER_SIZE: int = 1048
        self.SLEEP_TIME: float = 1 / tick_rate

        self.tick_rate: int = tick_rate
        
        self._ip: str = ip
        self._port: int = port

        self._socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.settimeout(0.1)

        self.send_packet: any = None
        self.recv_packet: any = None

        self._running: bool = True

        thread_send: threading.Thread = threading.Thread(target=self._run_s)
        thread_recv: threading.Thread = threading.Thread(target=self._run_r)

        thread_send.start()
        thread_recv.start()

    def kill(self) -> None:
        '''
        Kills the `Client` threads.
        '''

        self._running = False

    def _run_s(self) -> None:
        '''
        Thread which handles the `Client` package sending.

        The `Client` will continuosly send 'CONNECTING' to
        the server until it receives a packet back.

        If `send_packet` is not `None`, it will be sent to
        the server.
        '''

        while self._running:
            time.sleep(self.SLEEP_TIME)

            if self.recv_packet == None:
                self._socket.sendto(pickle.dumps('CONNECTING'), (self._ip, self._port))
            
            elif self.send_packet:
                data: bytes = pickle.dumps(self.send_packet)
                self._socket.sendto(data, (self._ip, self._port))

    def _run_r(self) -> None:
        '''
        Thread which handles the `Client` package receiving.

        When receiving a packet, it will update `recv_packet`.
        '''

        while self._running:
            try:
                data: tuple[bytes, tuple[str, int]] = self._socket.recvfrom(self.BUFFER_SIZE)
                self.recv_packet = pickle.loads(data[0])

            except socket.error:
                ...
