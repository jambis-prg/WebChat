import socket
import struct
import os
import math
import random

BUFFER_SIZE = 1024
HEADER_SIZE = 8
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

while True:
    try:
        dados, cliente_address = servidor.recvfrom(BUFFER_SIZE)
        cabecalho, max_pacotes = struct.unpack('>5sI', dados[:9])
        
        if cabecalho == b'BEGIN':
            nome_arquivo = dados[9:].decode()
            print(f"Cliente {cliente_address} enviando o arquivo: {nome_arquivo}")
            
            sessao_id = random.randint(1, 2**32 - 1)    # Gera um ID de sessão aleatório
            
            ack = struct.pack('>I', sessao_id)
            servidor.sendto(ack, cliente_address)
            
            # Armazena os pacotes recebidos
            pacotes_recebidos = {}
            num_pacote_esperado = 0
            
            print(f"Sessão iniciada com ID: {sessao_id}")
            
            # Recebe os pacotes CHUNK
            while num_pacote_esperado < max_pacotes:
                try:
                    dados, addr = servidor.recvfrom(BUFFER_SIZE)
                    
                    if len(dados) >= 13:  # Tamanho mínimo do cabeçalho CHUNK
                        cabecalho_chunk, id_recebido, num_pacote = struct.unpack('>5s2I', dados[:13])
                        
                        if cabecalho_chunk == b'CHUNK' and id_recebido == sessao_id:
                            if num_pacote == num_pacote_esperado:
                                conteudo = dados[13:]
                                pacotes_recebidos[num_pacote] = conteudo
                                print(f"Recebido pacote {num_pacote}")
                                num_pacote_esperado += 1
                            
                            # Envia acknowledgment com o ID da sessão
                            ack_pacote = struct.pack('>I', sessao_id)
                            servidor.sendto(ack_pacote, cliente_address)
                            
                except socket.timeout:
                    print("Timeout aguardando pacote do cliente")
                    continue
            
            # Salva o arquivo no servidor
            arquivo_servidor = os.path.join('Servidor', nome_arquivo)
            with open(arquivo_servidor, 'wb') as f:
                for i in range(max_pacotes):
                    if i in pacotes_recebidos:
                        f.write(pacotes_recebidos[i])
            
            print(f"Arquivo salvo como {arquivo_servidor}")
            
            # Envia o pacote BEGIN de volta
            nome_arquivo_servidor = os.path.basename(arquivo_servidor) 
            pacote_begin = struct.pack('>5sI', b'BEGIN', sessao_id)
            pacote_begin += nome_arquivo_servidor.encode()
            send_blocking(servidor, pacote_begin, cliente_address)
            
            # Envia o arquivo de volta para o cliente
            with open(arquivo_servidor, 'rb') as f:
                max_pacotes = math.ceil(os.path.getsize(arquivo_servidor) / DATA_SIZE)   # Calcula o número máximo de pacotes
                num_pacote = 0

                while (dados := f.read(DATA_SIZE)):
                    cabecalho = struct.pack('>5s2I', b'CHUNK', sessao_id, num_pacote)
                    pacote = cabecalho + dados

                    while True:
                        ack_id = struct.unpack('>I', send_blocking(servidor=servidor, pacote=pacote, cliente_address=cliente_address))[0]
                        if (ack_id == sessao_id):
                            break
                    print(f"Enviado pacote {num_pacote}\n")
                    num_pacote += 1
            
            print(f"Arquivo {arquivo_servidor} enviado de volta para o cliente")
            
    except Exception as e:
        print(f"Erro: {e}")
        continue
