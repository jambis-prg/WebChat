import socket
import struct
import os

BUFFER_SIZE = 1024
DATA_SIZE = 1020
SERVER_ADDRESS = ('localhost', 12345)

# Cria a pasta 'Servidor' se não existir
if not os.path.exists('Servidor'):
    os.makedirs('Servidor')

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     # Cria o socket UDP
servidor.bind(SERVER_ADDRESS)                                   # Associa o socket ao endereço do servidor

print(f"Servidor UDP iniciado em {SERVER_ADDRESS}")
print("Aguardando conexões...")

# Recebe o nome do arquivo
nome_arquivo, cliente_address = servidor.recvfrom(BUFFER_SIZE)
nome_arquivo = nome_arquivo.decode()
print(f"Cliente {cliente_address} enviando o arquivo: {nome_arquivo}")

# Armazena os pacotes recebidos
pacotes_recebidos = {}

while True:
    dados, addr = servidor.recvfrom(BUFFER_SIZE)

    if dados == b'FINAL':
        print("Fim do envio do cliente.")
        break

    if len(dados) > 4:
        num_pacote = struct.unpack('>I', dados[:4])[0]
        conteudo = dados[4:]
        pacotes_recebidos[num_pacote] = conteudo
        print(f"Recebido pacote {num_pacote}")

# Salva o arquivo no servidor
arquivo_servidor = os.path.join('Servidor', nome_arquivo)
with open(arquivo_servidor, 'wb') as f:
    for i in sorted(pacotes_recebidos.keys()):
        f.write(pacotes_recebidos[i])

print(f"Arquivo salvo como {arquivo_servidor}")

# Envia o arquivo, que acabou de salvar, de volta para o cliente
with open(arquivo_servidor, 'rb') as f:
    num_pacote = 0
    
    while True:
        dados = f.read(DATA_SIZE)

        if not dados:
            break

        cabecalho = struct.pack('>I', num_pacote)               # Cria o cabeçalho com o número do pacote
        pacote = cabecalho + dados                              # Combina o cabeçalho com os dados
        servidor.sendto(pacote, cliente_address)

        print(f"Enviado pacote {num_pacote} de volta")
        num_pacote += 1

servidor.sendto(b'FIM', cliente_address)
servidor.close()