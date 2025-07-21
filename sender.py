import socket
import struct
import time

class RDTSender:
    def __init__(self, receiver_addr, timeout=1.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver_addr = receiver_addr
        self.seq = 0
        self.timeout = timeout

    def _checksum(self, data: bytes) -> int:
        if len(data) % 2 == 1:
            data += b'\x00'
        s = sum(struct.unpack('!%dH' % (len(data) // 2), data))
        while s > 0xFFFF:
            s = (s & 0xFFFF) + (s >> 16)
        return ~s & 0xFFFF

    def _make_packet(self, seq: int, payload: bytes) -> bytes:
        header = struct.pack('!B', seq)
        checksum = self._checksum(header + payload)
        return struct.pack('!BH', seq, checksum) + payload

    def _parse_ack(self, data: bytes):
        if len(data) != 3:
            return None
        seq, recv_checksum = struct.unpack('!BH', data)
        calc_checksum = self._checksum(struct.pack('!B', seq))
        if recv_checksum == calc_checksum:
            return seq
        return None

    def send(self, data: bytes):
        pkt = self._make_packet(self.seq, data)

        while True:
            self.sock.sendto(pkt, self.receiver_addr)
            print(f"[RDT] Pacote {self.seq} enviado.")

            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                remaining = self.timeout - elapsed
                if remaining <= 0:
                    print("[RDT] Timeout expirado. Retransmitindo...")
                    break  # retransmitir

                self.sock.settimeout(remaining)
                try:
                    ack_data, _ = self.sock.recvfrom(1024)
                    ack_seq = self._parse_ack(ack_data)
                    if ack_seq == self.seq:
                        print(f"[RDT] ACK {ack_seq} recebido corretamente.")
                        self.seq ^= 1
                        return  # sucesso
                    else:
                        print(f"[RDT] ACK {ack_seq} incorreto. Ignorando...")
                except socket.timeout:
                    print("[RDT] Timeout parcial. Retransmitindo...")
                    break  # retransmitir

    def close(self):
        self.sock.close()
