import socket
import struct
import time
from typing import Tuple

class RDTServer:
    # Construtor
    def __init__(self, listen_addr, timeout=1.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(listen_addr)

        self.seqs = {}
        self.expected_seqs = {}
        self.timeout = timeout

    # Cria um ACK
    def _make_ack(self, seq: bool) -> bytes:
        return struct.pack('B', seq)

    # Cria um pacote
    def _make_packet(self, seq: bool, payload: bytes) -> bytes:
        return struct.pack('B', seq) + payload

    # Analisa um ACK
    def _parse_ack(self, data: bytes):
        if len(data) != 1:
            return None
        seq, = struct.unpack('B', data)
        return seq

    # Analisa um pacote
    def _parse_packet(self, pkt: bytes):
        if len(pkt) < 1:
            return None, None
        seq, = struct.unpack("B", pkt[:1])

        if len(pkt) > 1:
            payload = pkt[1:]
            return seq, payload

        return seq, None

    # Envia dados para um endereço
    def send(self, data: bytes, addr):
        seq = self.seqs.get(addr, 0)                                    # número de sequência atual
        if seq == 0:
            self.seqs[addr] = 0

        pkt = self._make_packet(seq, data)                              # cria o pacote

        while True:
            self.sock.sendto(pkt, addr)                                 # envia o pacote

            start_time = time.time()                                    # inicia o temporizador
            while True:
                elapsed = time.time() - start_time
                remaining = self.timeout - elapsed
                if remaining <= 0:
                    break                                               # retransmitir

                self.sock.settimeout(remaining)
                try:                                                    # espera pelo ack
                    ack_data, addr_resposta = self.sock.recvfrom(1024)

                    if addr_resposta != addr:
                        continue
                    
                    ack_seq = self._parse_ack(ack_data)
                    if ack_seq == seq:
                        self.seqs[addr] ^= 1
                        return                                          # sucesso
                except socket.timeout:
                    break                                               # retransmitir

    # Recebe dados
    def receive(self) -> Tuple[bytes, Tuple[str, int]]:
        while True:
            try:
                pkt, addr = self.sock.recvfrom(2048)                    # recebe o pacote

                expected_seq = self.expected_seqs.get(addr, 0)          # número de sequência esperado
                if (expected_seq == 0):
                    self.expected_seqs[addr] = 0

                seq, payload = self._parse_packet(pkt)                  # analisa o pacote

                ack = self._make_ack(seq)
                if seq == expected_seq and payload:                     # verifica sequência e payload
                    self.sock.sendto(ack, addr)
                    self.expected_seqs[addr] ^= 1
                    return payload, addr
                else:
                    self.sock.sendto(ack, addr)
            except socket.timeout:
                continue

    # Remove um endereço da lista de sequências
    def remove_addr(self, addr):
        if (addr in self.seqs):
            self.seqs.pop(addr)
        if (addr in self.expected_seqs):
            self.expected_seqs.pop(addr)

    # Transmite uma mensagem para todos os endereços
    def broadcast(self, message, exclude=None):
        for addr in self.seqs.keys():
            try:
                if addr != exclude:
                    self.send(message.encode(), addr)
            except Exception as e:
                print(e)
                pass

    # Transmite uma mensagem para todos os endereços registrados
    def broadcast_to_registered(self, message, names, exclude_addr=None):
        for _, user_addr in names.items():
            if user_addr != exclude_addr:
                self.send(message.encode(), user_addr)

    # Fecha o socket
    def close(self):
        self.sock.close()
