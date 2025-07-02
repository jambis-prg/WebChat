import socket
import struct
import sys
import os
import math

BUFFER_SIZE = 1024
DATA_SIZE = 1020
SERVER_ADDRESS = ('localhost', 12345)

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

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)              # Cria o socket UDP
cliente.settimeout(2.0)                                                 # Define o timeout do socket para 2 segundos

# Envia nome do arquivo
cliente.sendto(ARQUIVO_LOCAL.encode(), SERVER_ADDRESS)

# Envia o arquivo
with open(arquivo_path, 'rb') as f:
    max_pacotes = math.ceil(os.path.gesize(arquivo_path) / DATA_SIZE)   # Calcula o número máximo de pacotes
    num_pacote = 0

    while True:
        pacote = struct.pack('>5sI', b'BEGIN', max_pacotes)             # Cria o pacote de início com o nome do arquivo e número máximo de pacotes
        cliente.sendto(pacote, SERVER_ADDRESS) 

        try:
            data, _ = cliente.recvfrom(BUFFER_SIZE)                    
            id = struct.unpack('>I', data)                              # Recebe o ID da sessão do servidor
            break
        except socket.timeout:
            print(f"Nao foi possivel iniciar a comunicacao com o servidor\n")

    while (dados := f.read(DATA_SIZE)):                                 
        while True:
            cabecalho = struct.pack('>I', id) 
            pacote = cabecalho + dados                                  # Cria o pacote com o ID da sessão e os dados do arquivo
            cliente.sendto(pacote, SERVER_ADDRESS)
            
            try:
                ack, _ = cliente.recvfrom(1)                            # Espera pela confirmação do servidor
                break
            except socket.timeout:
                print(f"Nao foi possivel enviar o pacote {num_pacote}, reenviando\n")

        print(f"Enviado pacote {num_pacote}\n")
        num_pacote += 1

# Prepara para receber os pacotes numerados
pacotes = {}
print("Esperando pacotes")

cliente.settimeout(None)                                                # Remove o temporizador para receber os pacotes

for i in range(max_pacotes):                                            # Recebe os pacotes numerados
    data, _ = cliente.recvfrom(BUFFER_SIZE)
    session_id = struct.unpack('>I', data[:4])
    if session_id != id:
        continue                                                        # Verifica se o ID da sessão corresponde ao esperado
    pacotes[i] = data[4:]
    cliente.sendto(b'\x01', SERVER_ADDRESS)                             # Envia confirmação de recebimento do pacote

# Reordena os pacotes e salva o arquivo devolvido
arquivo_retorno = os.path.join('Cliente', 'devolvido_' + ARQUIVO_LOCAL)
with open(arquivo_retorno, 'wb') as f:
    for i in range(max_pacotes):
        f.write(pacotes[i])

print(f"Arquivo devolvido salvo como: {arquivo_retorno}")

cliente.close()                                                         # Fecha o socket do cliente