# rdt_receiver.py

import socket
import struct

class RDTReceiver:
    def __init__(self, listen_addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(listen_addr)
        self.expected_seq = 0

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

    def receive(self) -> bytes:
        while True:
            pkt, addr = self.sock.recvfrom(2048)
            seq, payload = self._parse_packet(pkt)

            if seq == self.expected_seq:
                print(f"[RDT] Pacote {seq} recebido corretamente.")
                ack = self._make_ack(seq)
                self.sock.sendto(ack, addr)
                self.expected_seq ^= 1
                return payload
            else:
                print(f"[RDT] Pacote duplicado {seq}. Reenviando último ACK.")
                ack = self._make_ack(1 - self.expected_seq)
                self.sock.sendto(ack, addr)
