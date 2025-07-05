import socket
import struct
import sys
import os
import math

BUFFER_SIZE = 1024
HEADER_SIZE = 8
DATA_SIZE = BUFFER_SIZE - HEADER_SIZE
SERVER_ADDRESS = ('localhost', 12345)

# --------------------------------- Obtendo Arquivo ------------------------------

# Verifica se o nome do arquivo foi passado como argumento
if len(sys.argv) != 2:
    print("Uso: python \"UDP - Cliente.py\" <nome_do_arquivo>")
    sys.exit(1)

ARQUIVO_LOCAL = sys.argv[1]

# Definir caminho do arquivo na pasta 'sample'
arquivo_path = os.path.join('sample', ARQUIVO_LOCAL)

# Verifica se o arquivo existe na pasta 'sample'
if not os.path.exists(arquivo_path):
    print(f"Arquivo '{arquivo_path}' não encontrado na pasta 'sample'.")
    sys.exit(1)

# Criar pasta Cliente se não existir
if not os.path.exists('Cliente'):
    os.makedirs('Cliente')

# --------------------------- Comunicação ------------------------------------

# Função bloqueante para envio de pacote ao servidor
# Ele fica tentando enviar o pacote ao servidor até um momento em que o servidor
# Responde com um pacote de reconhecimento, o servidor tem até 2 segundos para responder
# Esse pacote, caso contrário ele dará timeout e o cliente reenviará o pacote
def send_blocking(cliente, pacote):
    while True:
        cliente.sendto(pacote, SERVER_ADDRESS) # Envia pacote para o servidor
        try:
            # Sai do loop apenas se conseguir receber um pacote de reconhecimento
            # Do servidor indicando que recebeu o pacote
            data, _ = cliente.recvfrom(BUFFER_SIZE) 
            break
        except socket.timeout: # Exceção quando ocorre o timeout
            print(f"Nao foi possivel enviar o pacote ao servidor\n")

    return data # Retornando pacote de reconhecimento

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)              # Cria o socket UDP
cliente.settimeout(2.0)                                                 # Define o timeout do socket para 2 segundos

# Envia o arquivo
with open(arquivo_path, 'rb') as f:
    max_pacotes = math.ceil(os.path.getsize(arquivo_path) / DATA_SIZE)   # Calcula o número máximo de pacotes
    num_pacote = 0

    pacote = struct.pack('>5sI', b'BEGIN', max_pacotes)             # Cria o pacote de início com o nome do arquivo e número máximo de pacotes
    pacote += ARQUIVO_LOCAL.encode() # Adiciona o nome do arquivo
    id, = struct.unpack('>I', send_blocking(cliente=cliente, pacote=pacote)) # Obtendo o ID

    while (dados := f.read(DATA_SIZE)):                                 
        cabecalho = struct.pack('>5s2I', b'CHUNK', id, num_pacote)
        pacote = cabecalho + dados                                  # Cria o pacote com o ID da sessão e os dados do arquivo

        # Garante que apenas envie o proximo pacote se for o ID da sessao atual
        while True:
            ack_id, = struct.unpack('>I', send_blocking(cliente=cliente, pacote=pacote))
            if (ack_id == id):
                break
        
        print(f"Enviado pacote {num_pacote}\n")
        num_pacote += 1

# Prepara para receber os pacotes numerados
pacotes = {}
print("Esperando pacotes")

cliente.settimeout(None)                                                # Remove o temporizador para receber os pacotes

num_pacote = 0

# Garante o recebimento dos dados e garante que se o pacote de reconhecimento for perdido na transmissao
# Como o servidor renviará o mesmo pacote msm o cliente tendo recebido o cliente apenas reenviará o pacote de reconhecimento
# Garantindo que os dois não saim de sincronia
while True:
    data, _ = cliente.recvfrom(BUFFER_SIZE) # Recebe pacote do servidor
    cabecalho, sessao_id = struct.unpack('>5sI', data[:9]) # Lê cabecalho
    if (cabecalho == b'CHUNK' and sessao_id == id): # Verifica se o servidor ja esta enviando os pacotes
        indice = struct.unpack('>I', data[9:13])
        if (indice == num_pacote):
            pacotes[num_pacote] = data[13:]
            num_pacote += 1
    elif (cabecalho == b'BEGIN' and sessao_id == id): # Verifica se o servidor iniciou a comunicao
        novo_nome = str(data[9:].decode())
    ack_id = struct.pack('>I', sessao_id) # Prepara o pacote de reconhecimento
    cliente.sendto(ack_id, SERVER_ADDRESS) # Enviado pacote de reconhecimento

    if (num_pacote >= max_pacotes):
        break

# Reordena os pacotes e salva o arquivo devolvido
arquivo_retorno = os.path.join('Cliente', novo_nome)
with open(arquivo_retorno, 'wb') as f:
    for i in range(max_pacotes):
        f.write(pacotes[i])

print(f"Arquivo devolvido salvo como: {arquivo_retorno}")

cliente.close()                                                         # Fecha o socket do cliente