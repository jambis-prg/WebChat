import socket
import struct
import sys
import os
import math
from sender import RDTSender
from receiver import RDTReceiver

BUFFER_SIZE = 1024
HEADER_SIZE = 6
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

cliente = RDTSender(SERVER_ADDRESS, 2.0)

# Envia o arquivo
with open(arquivo_path, 'rb') as f:
    num_pacote = 0

    pacote = b'BEGIN' + ARQUIVO_LOCAL.encode() # Adiciona o nome do arquivo

    cliente.send(pacote)

    while (dados := f.read(DATA_SIZE)):                                 
        pacote = b'CHUNK' + dados # Cria o pacote com o ID da sessão e os dados do arquivo
        cliente.send(pacote)
        print(f"Enviado pacote {num_pacote}\n")
        num_pacote += 1

    cliente.send(b'FINAL')

cliente.close()

cliente = RDTReceiver(SERVER_ADDRESS)

# Prepara para receber os pacotes numerados
pacotes = {}
print("Esperando pacotes")

num_pacote = 0

pacote = cliente.receive()
novo_nome = pacote[5:].decode()

while True:
    pacote = cliente.receive()
    cabecalho, = struct.unpack('5s', pacote[:5])

    if cabecalho == b'CHUNK':
        pacotes[num_pacote] = pacote[5:]
        num_pacote += 1
    else:
        break

cliente.close()
    
# Reordena os pacotes e salva o arquivo devolvido
arquivo_retorno = os.path.join('Cliente', novo_nome)
with open(arquivo_retorno, 'wb') as f:
    for i in range(num_pacote):
        f.write(pacotes[i])

print(f"Arquivo devolvido salvo como: {arquivo_retorno}")

cliente.close()                                                         # Fecha o socket do cliente
