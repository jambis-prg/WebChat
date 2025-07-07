import socket
import struct
import os
import math
import random

BUFFER_SIZE = 1024
HEADER_SIZE = 13
DATA_SIZE = BUFFER_SIZE - HEADER_SIZE
SERVER_ADDRESS = ('localhost', 12345)

# Cria a pasta 'Servidor' se não existir
if not os.path.exists('Servidor'):
    os.makedirs('Servidor')

# Função bloqueante para envio de pacote ao cliente
def send_blocking(servidor, pacote, cliente_address):
    while True:
        servidor.sendto(pacote, cliente_address)
        try:
            data, _ = servidor.recvfrom(BUFFER_SIZE)
            break
        except socket.timeout:
            print(f"Timeout ao enviar pacote para o cliente")
    return data

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(SERVER_ADDRESS)
servidor.settimeout(2.0)

print(f"Servidor UDP iniciado em {SERVER_ADDRESS}")
print("Aguardando conexões...")

send_back = False

while True:
    try:
        dados, cliente_address = servidor.recvfrom(BUFFER_SIZE)
        cabecalho, data_int = struct.unpack('>5sI', dados[:9])
        
        if cabecalho == b'BEGIN':
            nome_arquivo = dados[9:].decode()
            max_pacotes = data_int
            print(f"Cliente {cliente_address} enviando o arquivo: {nome_arquivo}")
            
            sessao_id = random.randint(1, 2**32 - 1)    # Gera um ID de sessão aleatório
            
            # Armazena os pacotes recebidos
            pacotes_recebidos = {}
            num_pacote_esperado = 0
            num_pacote = 0
            
            print(f"Sessão iniciada com ID: {sessao_id}")
        elif cabecalho == b'CHUNK':
            id_recebido = data_int
            num_pacote, = struct.unpack('>I', dados[9:13])
            if id_recebido == sessao_id and num_pacote == num_pacote_esperado:
                pacotes_recebidos[num_pacote] = dados[13:]
                num_pacote_esperado += 1
                print(f"{num_pacote_esperado}/{max_pacotes}")

                if (num_pacote_esperado >= max_pacotes):
                    send_back = True
                    

        # Envia acknowledgment com o ID da sessão
        ack_pacote = struct.pack('>I', sessao_id)
        servidor.sendto(ack_pacote, cliente_address)

        if (send_back):
            send_back = False
            # Salva o arquivo no servidor
            arquivo_servidor = os.path.join('Servidor', nome_arquivo)
            with open(arquivo_servidor, 'wb') as f:
                for i in range(max_pacotes):
                    f.write(pacotes_recebidos[i])

            print(f"Arquivo salvo como {arquivo_servidor}")
            
            # Envia o pacote BEGIN de volta
            nome_arquivo_servidor = os.path.basename(arquivo_servidor) 
            pacote_begin = struct.pack('>5sI', b'BEGIN', sessao_id)
            pacote_begin += ("servidor_" + nome_arquivo_servidor).encode()
            send_blocking(servidor, pacote_begin, cliente_address)
            
            # Envia o arquivo de volta para o cliente
            with open(arquivo_servidor, 'rb') as f:
                indice_pacote = 0
                while (dados := f.read(DATA_SIZE)):
                    cabecalho = struct.pack('>5s2I', b'CHUNK', sessao_id, indice_pacote)
                    pacote = cabecalho + dados

                    while True:
                        ack_id, = struct.unpack('>I', send_blocking(servidor=servidor, pacote=pacote, cliente_address=cliente_address))
                        if (ack_id == sessao_id):
                            break

                    print(f"Enviado pacote {indice_pacote}\n")
                    indice_pacote += 1
            
            print(f"Arquivo {arquivo_servidor} enviado de volta para o cliente")
    except Exception as e:
        print(f"Erro: {e}")
        continue
