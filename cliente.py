import socket
import threading
from sender import RDTSender
from receiver import RDTReceiver
from fullRDT import RDTFull

def fixed_size_bytes_with_null(s, size, encoding='utf-8'):
    b = s.encode(encoding)
    if len(b) >= size:
        # corta para caber size-1 bytes e adiciona null no final
        b = b[:size-1] + b'\0'
    else:
        # preenche com null bytes até size total, sempre terminando com \0
        b = b + b'\0' + b'\0' * (size - len(b) - 1)
    return b
    
# def receive(sock):
#     while True:
#         try:
#             data = sock.recv(1024)
#             if not data:
#                 break
#             print(data.decode(), end="")
#         except:
#             break

def receive_print(client):
    while True:
        try:
            data, _ = client.receive()
            if not data:
                break
            print(data.decode(), end="")
        except:
            break

HEADER = 16 #hi, meu nome eh <- possui 16 caracteres contando com o ultio espaco
NAME_MAX_LEN = HEADER + 20

def main():
    server_ip = "0.0.0.0"
    
    SERVER_ADDRESS = (server_ip, 12345)
    CLIENT_ADDRESS = (server_ip, 8080)
    client = RDTFull(SERVER_ADDRESS, CLIENT_ADDRESS, 2.0)
    client.send(b"HI") # mensagem inicial para ele se indentificar
    msg, _ = client.receive()
    print(msg) # printando a msg para se identificar

    while True:
        msg = fixed_size_bytes_with_null(input(), NAME_MAX_LEN)
        client.send(msg)
        name = msg.split(b"hi, meu nome eh")[-1].strip() # melhorar esse split
        msg, _ = client.receive()
        print(msg)
        if msg == b"Nome cadastrado.\n":
            break
    
    
    threading.Thread(target=receive_print, args=(client,), daemon=True).start()

    while True:
        try:
            msg = input()
            if msg.strip().lower() == "bye":
                client.send(name + b"bye\n", SERVER_ADDRESS)
                break
            client.send(name + msg.encode() + b"\n")
        except:
            break

    client.close()


if __name__ == "__main__":
    main()
