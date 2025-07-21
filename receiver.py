# rdt_receiver.py

import socket
import struct

class RDTReceiver:
    def __init__(self, listen_addr):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(listen_addr)
        self.expected_seq = 0

    def _checksum(self, data: bytes) -> int:
        if len(data) % 2 == 1:
            data += b'\x00'
        s = sum(struct.unpack('!%dH' % (len(data) // 2), data))
        while s > 0xFFFF:
            s = (s & 0xFFFF) + (s >> 16)
        return ~s & 0xFFFF

    def _make_ack(self, seq: int) -> bytes:
        checksum = self._checksum(struct.pack('!B', seq))
        return struct.pack('!BH', seq, checksum)

    def _parse_packet(self, pkt: bytes):
        if len(pkt) < 3:
            return None, None, False
        seq, recv_checksum = struct.unpack('!BH', pkt[:3])
        payload = pkt[3:]
        calc_checksum = self._checksum(struct.pack('!B', seq) + payload)
        valid = (recv_checksum == calc_checksum)
        return seq, payload, valid

    def receive(self) -> bytes:
        while True:
            pkt, addr = self.sock.recvfrom(2048)
            seq, payload, valid = self._parse_packet(pkt)

            if not valid:
                print("[RDT] Pacote corrompido. Reenviando último ACK.")
                ack = self._make_ack(1 - self.expected_seq)
                self.sock.sendto(ack, addr)
                continue

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
