import socket
import struct
import time
from typing import Tuple

class RDTFull:
    # Inicializa o RDT
    def __init__(self, receiver_addr, listen_addr, timeout=1.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind(listen_addr)
        self.receiver_addr = receiver_addr

        self.seq = 0
        self.expected_seq = 0
        self.timeout = timeout

    # Cria um pacote de ACK
    def _make_ack(self, seq: bool) -> bytes:
        return struct.pack('B', seq)

    # Cria um pacote de dados
    def _make_packet(self, seq: bool, payload: bytes) -> bytes:
        return struct.pack('B', seq) + payload

    # Analisa um pacote de ACK
    def _parse_ack(self, data: bytes):
        if len(data) != 1:
            return None
        seq, = struct.unpack('B', data)
        return seq

    # Analisa um pacote de dados
    def _parse_packet(self, pkt: bytes):
        if len(pkt) < 1:
            return None, None
        seq, = struct.unpack("B", pkt[:1])

        if len(pkt) > 1:
            payload = pkt[1:]
            return seq, payload

        return seq, None

    # Envia dados
    def send(self, data: bytes):
        pkt = self._make_packet(self.seq, data)             # cria o pacote

        while True:
            self.sock.sendto(pkt, self.receiver_addr)       # envia o pacote

            start_time = time.time()                        # marca o tempo de envio
            while True:
                elapsed = time.time() - start_time
                remaining = self.timeout - elapsed
                if remaining <= 0:
                    break                                   # retransmitir

                self.sock.settimeout(remaining)
                try:                                        # espera pelo ACK
                    ack_data, _ = self.sock.recvfrom(1024)
                    ack_seq = self._parse_ack(ack_data)
                    if ack_seq == self.seq:
                        self.seq ^= 1
                        return                              # sucesso
                except socket.timeout:
                    break                                   # retransmitir

    # Recebe dados
    def receive(self) -> Tuple[bytes, Tuple[str, int]]:
        while True:
            try:
                pkt, addr = self.sock.recvfrom(2048)        # recebe o pacote
                seq, payload = self._parse_packet(pkt)      # analisa o pacote

                if seq == self.expected_seq and payload:    # verifica sequência e payload
                    ack = self._make_ack(seq)
                    self.sock.sendto(ack, addr)
                    self.expected_seq ^= 1
                    return payload, addr
                else:
                    ack = self._make_ack(1 - self.expected_seq)
                    self.sock.sendto(ack, addr)
            except socket.timeout:
                continue

    # Fecha o socket
    def close(self):
        self.sock.close()

    # Retorna o número da porta
    def get_port_number(self):
        return self.sock.getsockname()[1]
