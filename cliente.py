import threading
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

msg_event = threading.Event()
logged = False

def receive_print(client):
    global logged, msg_event
    while True:
        try:
            print("esperando dados")
            data, _ = client.receive()

            if not data:
                print("vazio")
                continue

            if data == b"Nome cadastrado.\n":
                logged = True
                msg_event.set()  # Notifica que chegou mensagem
            elif data == b"Nome ja em uso.\n":
                msg_event.set()

            print(data.decode(), end="")
        except Exception as e:
            print(e)
            break
    print("saiu do lock")

HEADER = 16 # hi, meu nome eh <- possui 16 caracteres contando com o ultimo espaco
NAME_MAX_LEN = HEADER + 20

def main():
    global logged, msg_event
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
        if logged:
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
