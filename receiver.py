import socket
import struct
import random
from typing import Tuple
from Simulador_de_rede import Simulador_de_Perdas

class RDTReceiver:
    def __init__(self, listen_addr, simu_rede=None):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind(listen_addr)
        self.expected_seq = 0
        
        if simu_rede is None:
            taxa_de_perda = Simulador_de_Perdas.recolher_taxa_dos_argumentos()
            self.simu_rede = Simulador_de_Perdas(taxa_de_perda)
        else:
            self.simu_rede = simu_rede

    def _make_ack(self, seq: int) -> bytes:
        return struct.pack('B', seq)

    def _parse_packet(self, pkt: bytes):
        if len(pkt) < 3:
            return None, None, False

        seq, = struct.unpack("B", pkt[:1])
        payload = pkt[1:]
        return seq, payload
    
    def close(self):
        self.sock.close()

    def receive(self) -> Tuple[bytes, Tuple[str, int]]:
        while True:
            pkt, addr = self.sock.recvfrom(2048)
            seq, payload = self._parse_packet(pkt)

            if seq == self.expected_seq:
                # Simular perda de pacote
                if self.simu_rede.simula_perda_de_pacote(f"Pacote seq={seq}"):
                    continue

                print(f"[RDT] Pacote {seq} recebido corretamente.")
                ack = self._make_ack(seq)
                self.sock.sendto(ack, addr)
                self.expected_seq ^= 1
                return payload, addr
            else:
                print(f"[RDT] Pacote duplicado {seq}. Reenviando último ACK.")
                ack = self._make_ack(1 - self.expected_seq)
                self.sock.sendto(ack, addr)
