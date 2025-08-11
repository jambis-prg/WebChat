import socket
import struct
import time
from typing import Tuple

class RDTFull:
    def __init__(self, receiver_addr, listen_addr, timeout=1.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(listen_addr)
        self.receiver_addr = receiver_addr

        self.seq = 0
        self.expected_seq = 0
        self.timeout = timeout

    def _make_ack(self, seq: int) -> bytes:
        return struct.pack('B', seq)
        
    def _make_packet(self, seq: int, payload: bytes) -> bytes:
        return struct.pack('B', seq) + payload

    def _parse_ack(self, data: bytes):
        if len(data) != 1:
            return None
        seq, = struct.unpack('B', data)
        return seq
    
    def _parse_packet(self, pkt: bytes):
        if len(pkt) < 3:
            return None, None, False
        seq, = struct.unpack("B", pkt[:1])
        payload = pkt[1:]
        return seq, payload

    def send(self, data: bytes):
        pkt = self._make_packet(self.seq, data)

        while True:
            self.sock.sendto(pkt, self.receiver_addr)
            #print(f"[RDT] Pacote {self.seq} enviado.")

            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                remaining = self.timeout - elapsed
                if remaining <= 0:
                    #print("[RDT] Timeout expirado. Retransmitindo...")
                    break  # retransmitir

                self.sock.settimeout(remaining)
                try:
                    ack_data, _ = self.sock.recvfrom(1024)
                    ack_seq = self._parse_ack(ack_data)
                    if ack_seq == self.seq:
                        #print(f"[RDT] ACK {ack_seq} recebido corretamente.")
                        self.seq ^= 1
                        return  # sucesso
                    #else:
                        #print(f"[RDT] ACK {ack_seq} incorreto. Ignorando...")
                except socket.timeout:
                    #print("[RDT] Timeout parcial. Retransmitindo...")
                    break  # retransmitir

    def receive(self) -> Tuple[bytes, Tuple[str, int]]:
        while True:
            try:
                pkt, addr = self.sock.recvfrom(2048)
                seq, payload = self._parse_packet(pkt)

                if seq == self.expected_seq:
                    #print(f"[RDT] Pacote {seq} recebido corretamente.")
                    ack = self._make_ack(seq)
                    self.sock.sendto(ack, addr)
                    self.expected_seq ^= 1
                    return payload, addr
                else:
                    #print(f"[RDT] Pacote duplicado {seq}. Reenviando último ACK.")
                    ack = self._make_ack(1 - self.expected_seq)
                    self.sock.sendto(ack, addr)
            except socket.timeout:
                continue

    def close(self):
        self.sock.close()
