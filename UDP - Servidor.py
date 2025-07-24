import socket
import struct
import os
import math
import random
import sys
from sender import RDTSender
from receiver import RDTReceiver
from Simulador_de_rede import Simulador_de_Perdas

BUFFER_SIZE = 1024
HEADER_SIZE = 6
DATA_SIZE = BUFFER_SIZE - HEADER_SIZE
SERVER_ADDRESS = ('localhost', 12345)

# Criar a pasta 'Servidor' se não existir
if not os.path.exists('Servidor'):
    os.makedirs('Servidor')

# Criar o simulador de rede com base nos argumentos da linha de comando
taxa_de_perda = Simulador_de_Perdas.recolher_taxa_dos_argumentos()
simu_rede = Simulador_de_Perdas(taxa_de_perda)

# Função bloqueante para envio de pacote ao cliente
def send_blocking(servidor, pacote, cliente_address):
    while True:
        servidor.sendto(pacote, cliente_address)
        try:
            data, _ = servidor.recvfrom(BUFFER_SIZE)                            # Recebe o pacote de reconhecimento e sai do loop
            break
        except socket.timeout:
            print(f"Timeout ao enviar pacote para o cliente")
    return data

while True:
    servidor = RDTReceiver(SERVER_ADDRESS, simu_rede)                           # Cria o socket do servidor com o simulador de rede

    # Preparar para receber os pacotes numerados
    pacotes = {}
    print("Esperando pacotes")

    num_pacote = 0

    pacote = servidor.receive()
    nome_arquivo = pacote[5:].decode()

    while True:
        pacote = servidor.receive()
        cabecalho, = struct.unpack('5s', pacote[:5])

        if cabecalho == b'CHUNK':
            pacotes[num_pacote] = pacote[5:]
            num_pacote += 1
        else:
            break

    servidor.close()                                                            # Fecha o socket do servidor

    arquivo_servidor = os.path.join('Servidor', nome_arquivo)                   # Cria o caminho completo do arquivo no servidor

    with open(arquivo_servidor, 'wb') as f:
        for i in range(num_pacote):
            f.write(pacotes[i])

    servidor = RDTSender(SERVER_ADDRESS, 2.0)

    # Enviar o arquivo
    with open(arquivo_servidor, 'rb') as f:                                     # Abre o arquivo para leitura
        num_pacote = 0

        nome_arquivo_servidor = os.path.basename(arquivo_servidor) 
        pacote = b'BEGIN' + ("servidor_" + nome_arquivo_servidor).encode()      # Adiciona o nome do arquivo com prefixo 'servidor_'

        servidor.send(pacote)

        while (dados := f.read(DATA_SIZE)):                                 
            pacote = b'CHUNK' + dados                                           # Cria o pacote com o ID da sessão e os dados do arquivo
            servidor.send(pacote)
            print(f"Enviado pacote {num_pacote}\n")
            num_pacote += 1

        servidor.send(b'FINAL')

    servidor.close()                                                            # Fecha o socket do servidor