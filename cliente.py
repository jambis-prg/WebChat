import threading
import sys
import signal
from fullRDT import RDTFull

def fixed_size_bytes_with_null(s, size, encoding='utf-8'):
    b = s.encode(encoding)
    if len(b) >= size:
        b = b[:size-1] + b'\0' # corta para caber size-1 bytes e adiciona null no final
    else:
        b = b + b'\0' + b'\0' * (size - len(b) - 1) # preenche com null bytes até size total, sempre terminando com \0
    return b

# Evento para sincronizar recebimento de resposta do servidor (nome cadastrado ou nome em uso)
msg_event = threading.Event()

# Flag para indicar se o nome foi cadastrado com sucesso
logged = False

def receive_print(client):
    global logged, msg_event

    while True:
        try:
            # print("esperando dados")
            # Recebe dados do servidor (bloqueia até receber)
            data, _ = client.receive()

            if not data:
                # print("vazio")
                continue

            # Sinaliza quando o servidor confirmou cadastro ou nome em uso
            if data == b"Nome cadastrado.\n":
                logged = True
                msg_event.set()
            elif data == b"Nome ja em uso.\n":
                msg_event.set()

            print(data.decode(), end="")

        except Exception as e:
            print(e)
            break

    # print("saiu do receive")

# Tamanho máximo da mensagem de identificação (16 bytes do texto + 20 para o nome)
HEADER = 16 # hi, meu nome eh <- possui 16 caracteres contando com o ultimo espaco
NAME_MAX_LEN = HEADER + 20

def main():
    global logged, msg_event
    
    SERVER_ADDRESS = (input("Digite o IP do servidor: "), 12345)
    CLIENT_ADDRESS = ("0.0.0.0", 0)

    client = RDTFull(SERVER_ADDRESS, CLIENT_ADDRESS, 2.0)
    print(f"Cliente rodando na porta {client.get_port_number()}")

    # Thread para receber mensagens sem bloquear o fluxo principal
    recv_thread = threading.Thread(target=receive_print, args=(client,), daemon=True)
    recv_thread.start()

    # uma saida elegante e que ainda sai da sala caso de ctrl+C
    def handler(sig, frame):
        print("\n[!] Ctrl+C detectado, encerrando conexão...")
        client.send(name + "bye".encode() + b"\n")
        sys.exit(0)
        

    signal.signal(signal.SIGINT, handler)
    # Aguardar confirmação do servidor
    while True:
        # esta dentro do loop para caso ele tente cadastrar um nome ja em uso
        # ai ele tenta novamente
        client.send(b"HI") # mensagem inicial para indentificação do usuário
        msg = fixed_size_bytes_with_null(input(), NAME_MAX_LEN)
        name = msg.split(b"hi, meu nome eh")[-1].strip()
        client.send(msg)

        # print("esperando")
        msg_event.wait()
        # print("acordou")

        if logged:
            break

    print("Entrando no chat")
    # Loop principal do chat, envia mensagens para o servidor
    while True:
        try:
            msg = input()
            client.send(name + msg.encode() + b"\n")
            
            if msg.strip() == "bye":
                break
        except:
            break

    # recv_thread.join() # Esperar a thread terminar
    client.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
