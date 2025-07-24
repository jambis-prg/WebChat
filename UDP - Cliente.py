import socket
import struct
import sys
import os
import math
from sender import RDTSender
from receiver import RDTReceiver
from Simulador_de_rede import Simulador_de_Perdas

BUFFER_SIZE = 1024
HEADER_SIZE = 6
DATA_SIZE = BUFFER_SIZE - HEADER_SIZE
SERVER_ADDRESS = ('localhost', 12345)

# Filtra argumentos que não são opções de rede para encontrar o nome do arquivo
arquivo_args = []
i = 1
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg.startswith('--'):
        if '=' not in arg and i + 1 < len(sys.argv):
            if arg == '--loss' or arg == '--random-range':
                i += 1 
        i += 1
    else:
        arquivo_args.append(arg)
        i += 1

# Verifica se o nome do arquivo foi passado como argumento
if len(arquivo_args) != 1:
    print("Uso: python \"UDP - Cliente.py\" <nome_do_arquivo> [opções]")
    print("Exemplo: python \"UDP - Cliente.py\" arquivo.txt --loss-rate=0.05")
    sys.exit(1)

ARQUIVO_LOCAL = arquivo_args[0]

# Definir caminho do arquivo na pasta 'sample'
arquivo_path = os.path.join('sample', ARQUIVO_LOCAL)

# Verificar se o arquivo existe na pasta 'sample'
if not os.path.exists(arquivo_path):
    print(f"Arquivo '{arquivo_path}' não encontrado na pasta 'sample'.")
    sys.exit(1)

# Criar pasta Cliente se não existir
if not os.path.exists('Cliente'):
    os.makedirs('Cliente')

# Criar o simulador de rede com base nos argumentos da linha de comando
taxa_de_perda = Simulador_de_Perdas.recolher_taxa_dos_argumentos()
simu_rede = Simulador_de_Perdas(taxa_de_perda)

# Função bloqueante para envio de pacote ao servidor
def send_blocking(cliente, pacote):
    while True:
        cliente.sendto(pacote, SERVER_ADDRESS)                          # Envia pacote para o servidor
        try:
            data, _ = cliente.recvfrom(BUFFER_SIZE)                     # Recebe o pacote de reconhecimento e sai do loop
            break
        except socket.timeout:                                          # Exceção quando ocorre o timeout
            print(f"Nao foi possivel enviar o pacote ao servidor\n")

    return data                                                         # Retorna pacote de reconhecimento

cliente = RDTSender(SERVER_ADDRESS, 2.0)

# Enviar o arquivo
with open(arquivo_path, 'rb') as f:
    num_pacote = 0

    pacote = b'BEGIN' + ARQUIVO_LOCAL.encode()                          # Adiciona o nome do arquivo

    cliente.send(pacote)

    while (dados := f.read(DATA_SIZE)):                                 
        pacote = b'CHUNK' + dados                                       # Cria o pacote com o ID da sessão e os dados do arquivo
        cliente.send(pacote)
        print(f"Enviado pacote {num_pacote}\n")
        num_pacote += 1

    cliente.send(b'FINAL')

cliente.close()

cliente = RDTReceiver(SERVER_ADDRESS, simu_rede)

# Preparar para receber os pacotes numerados
pacotes = {}
print("Esperando pacotes")

num_pacote = 0

pacote = cliente.receive()
novo_nome = pacote[5:].decode()

while True:
    pacote = cliente.receive()
    cabecalho, = struct.unpack('5s', pacote[:5])                        # Extrai o cabeçalho do pacote

    if cabecalho == b'CHUNK':
        pacotes[num_pacote] = pacote[5:]
        num_pacote += 1
    else:
        break

cliente.close()
    
# Reordenar os pacotes e salvar o arquivo devolvido
arquivo_retorno = os.path.join('Cliente', novo_nome)
with open(arquivo_retorno, 'wb') as f:
    for i in range(num_pacote):
        f.write(pacotes[i])

print(f"Arquivo devolvido salvo como: {arquivo_retorno}")

cliente.close()                                                         # Fecha o socket do cliente