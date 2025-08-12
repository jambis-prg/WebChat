import socket
import struct
import time
from typing import Tuple

# servidor implementando RDT para multiplos recivers e podendo mandar para todos eles
# o RDT reciver implementado em receiver.py tem o erro de bugar o numero de sequencia
# caso fosse usado para receber de multiplos "ip's" diferentes, nesse caso esse lida com 
# isso mantendo um numero de sequencia para cada ip que ele recebe alguma mensagem
class RDTServer:
    def __init__(self, listen_addr, timeout=1.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(listen_addr)

        self.seqs = {}
        self.expected_seqs = {}
        self.timeout = timeout

    def _make_ack(self, seq: bool) -> bytes:
        return struct.pack('B', seq)
        
    def _make_packet(self, seq: bool, payload: bytes) -> bytes:
        return struct.pack('B', seq) + payload

    def _parse_ack(self, data: bytes):
        if len(data) != 1:
            return None
        seq, = struct.unpack('B', data)
        return seq
    
    def _parse_packet(self, pkt: bytes):
        if len(pkt) < 1:
            return None, None
        seq, = struct.unpack("B", pkt[:1])

        if len(pkt) > 1:
            payload = pkt[1:]
            return seq, payload

        return seq, None

    def send(self, data: bytes, addr):
        seq = self.seqs.get(addr, 0)
        if seq == 0:
            self.seqs[addr] = 0
        
        pkt = self._make_packet(seq, data)

        while True:
            self.sock.sendto(pkt, addr)
            print(f"[RDT] Pacote {seq} enviado para {addr}.")

            start_time = time.time()
            while True:
                elapsed = time.time() - start_time
                remaining = self.timeout - elapsed
                if remaining <= 0:
                    print("[RDT] Timeout expirado. Retransmitindo...")
                    break  # retransmitir

                self.sock.settimeout(remaining)
                try:
                    ack_data, addr_resposta = self.sock.recvfrom(1024)

                    if addr_resposta != addr:
                        continue
                    
                    ack_seq = self._parse_ack(ack_data)
                    if ack_seq == seq:
                        print(f"[RDT] ACK {ack_seq} recebido corretamente de {addr}.")
                        self.seqs[addr] ^= 1
                        return  # sucesso
                    else:
                        print(f"[RDT] ACK {ack_seq} incorreto. Ignorando...")
                except socket.timeout:
                    print("[RDT] Timeout parcial. Retransmitindo...")
                    break  # retransmitir

    def receive(self) -> Tuple[bytes, Tuple[str, int]]:
        while True:
            try:
                pkt, addr = self.sock.recvfrom(2048)

                expected_seq = self.expected_seqs.get(addr, 0)
                if (expected_seq == 0):
                    self.expected_seqs[addr] = 0
                
                seq, payload = self._parse_packet(pkt)

                ack = self._make_ack(seq)
                if seq == expected_seq and payload:
                    print(f"[RDT] Pacote {seq} recebido corretamente.")
                    self.sock.sendto(ack, addr)
                    self.expected_seqs[addr] ^= 1
                    return payload, addr
                else:
                    print(f"[RDT] Pacote duplicado {seq}. Reenviando último ACK.")
                    self.sock.sendto(ack, addr)
            except socket.timeout:
                continue

    def remove_addr(self, addr):
        if (addr in self.seqs):
            self.seqs.pop(addr)
        if (addr in self.expected_seqs):
            self.expected_seqs.pop(addr)
            
    def broadcast(self, message, exclude=None):
        for addr in self.seqs.keys():
            try:
                # print(f'{addr} x {exclude}')
                if addr != exclude:
                    self.send(message.encode(), addr)
            except Exception as e:
                print(e)
                pass

    def broadcast_to_registered(self, message, names, exclude_addr=None):
        for _, user_addr in names.items():
            if user_addr != exclude_addr:
                self.send(message.encode(), user_addr)
    
    def close(self):
        self.sock.close()
