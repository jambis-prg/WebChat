import socket
import threading
from sender import RDTSender
from receiver import RDTReceiver

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

def receive_print(rdt_revice):
    while True:
        try:
            data, _ = rdt_revice.receive()
            if not data:
                break
            print(data.decode(), end="")
        except:
            break

NAME_MAX_LEN = 20

def main():
    # server_ip = input("Digite o IP do servidor: ")
    server_ip = "127.0.0.1"
    # server_port = int(input("Digite a porta do servidor: "))
    server_port = 12346
    
    SERVER_ADDRESS = (server_ip, server_port)
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect((server_ip, server_port))
    sender = RDTSender(SERVER_ADDRESS, 2.0)
    receiver = RDTReceiver(SERVER_ADDRESS, None)

    sender.send(b"HI") # mensagem inicial para ele se indentificar
    msg, _ = rdt_revice.receive()
    print(data) # printando a msg para se identificar

    while True:
        name = fixed_size_bytes_with_null(input(), NAME_MAX_LEN)
        sender.send(name)
        msg, addr = receiver.receive()
        print(msg)
        if msg == b"Nome cadastrado.\n":
            break
    
    
    threading.Thread(target=receive_print, args=(receiver,), daemon=True).start()

    while True:
        try:
            msg = input()
            if msg.strip().lower() == "bye":
                # sock.sendall(b"bye\n")
                sender.sendto(name + b"bye\n", SERVER_ADDRESS)
                break
            # sock.sendall((msg + "\n").encode())
            sender.sendto(name + msg.encode() + b"\n")
        except:
            break

    # sock.close()


if __name__ == "__main__":
    main()
