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

lock = threading.Lock()
_msg = None
msg_event = threading.Event()

def receive_print(client):
    global _msg, msg_event
    while True:
        try:
            with lock:
                print("esperando dados")
                data, _ = client.receive()
                _msg = data

            if not data:
                # _msg = ""
                print("vazio")
                continue
            print(f"msg___{_msg}")
            if _msg == b"Nome cadastrado.\n":
                print("acorda fdp")
                msg_event.set()  # Notifica que chegou mensagem
            print(data.decode(), end="")
        except Exception as e:
            print(e)
            break
    print("saiu do lock")

HEADER = 16 # hi, meu nome eh <- possui 16 caracteres contando com o ultimo espaco
NAME_MAX_LEN = HEADER + 20

def main():
    global _msg, msg_event
    server_ip = "0.0.0.0"
    
    SERVER_ADDRESS = (server_ip, 12345)
    CLIENT_ADDRESS = (server_ip, 8080)

    client = RDTFull(SERVER_ADDRESS, CLIENT_ADDRESS, 2.0)
    threading.Thread(target=receive_print, args=(client,), daemon=True).start()
    client.send(b"HI") # mensagem inicial para ele se indentificar

    while True:
        msg = fixed_size_bytes_with_null(input(), NAME_MAX_LEN)
        name = msg.split(b"hi, meu nome eh")[-1].strip() # melhorar esse split
        client.send(msg)

        print("esperando")
        msg_event.wait()

        print("acordou")
        print(f"msg: {_msg.decode()}")
        if _msg == b"Nome cadastrado.\n":
            break

    print("Comecando programa")
    while True:
        try:
            msg = input()
            client.send(name + msg.encode() + b"\n")
            if msg.strip() == "bye":
                break
        except:
            break

    client.close()


if __name__ == "__main__":
    main()
