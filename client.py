import threading
import sys
import signal
from clientRDT import RDTFull

# Função para criar uma representação em bytes de tamanho fixo com null-termination
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

# Função para receber e imprimir mensagens do servidor
def receive_print(client):
    global logged, msg_event    # variáveis globais para controle de estado

    while True:
        try:
            # Recebe dados do servidor (bloqueia até receber)
            data, _ = client.receive()

            if not data:
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

# Função para tratar o sinal de interrupção (Ctrl+C)
def handler(client, name, sig, frame):
    print("\n[!] Ctrl+C detectado, encerrando conexão...")
    client.send(name + "bye".encode() + b"\n")
    sys.exit(0)

# Tamanho máximo da mensagem de identificação (16 bytes do texto + 20 para o nome)
HEADER = 16     # hi, meu nome eh <- possui 16 caracteres contando com o ultimo espaco
NAME_MAX_LEN = HEADER + 20

# Função principal do cliente
def main():
    global logged, msg_event

    SERVER_ADDRESS = (input("Digite o IP do servidor: "), 12345)    # Endereço do servidor
    CLIENT_ADDRESS = ("0.0.0.0", 0)                                 # Endereço do cliente

    client = RDTFull(SERVER_ADDRESS, CLIENT_ADDRESS, 2.0)
    print(f"[Cliente] Rodando na porta {client.get_port_number()}")

    # Thread para receber mensagens sem bloquear o fluxo principal
    recv_thread = threading.Thread(target=receive_print, args=(client,), daemon=True)
    recv_thread.start()

    signal.signal(signal.SIGINT, handler)

    # Aguardar confirmação do servidor (se mantém no loop caso tentem cadastrar um nome já em uso)
    while True:
        client.send(b"HI") # mensagem inicial para indentificação do usuário
        msg = fixed_size_bytes_with_null(input(), NAME_MAX_LEN)
        name = msg.split(b"hi, meu nome eh")[-1].strip()

        client.send(msg)
        msg_event.wait()

        if logged:
            break

    # Loop principal do chat, envia mensagens para o servidor
    while True:
        try:
            msg = input()
            client.send(name + msg.encode() + b"\n")
            
            if msg.strip() == "bye":
                break
        except:
            break

    client.close()
    sys.exit(0)

# Ponto de entrada do programa
if __name__ == "__main__":
    main()