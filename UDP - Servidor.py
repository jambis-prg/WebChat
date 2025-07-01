import socket
import struct

BUFFER_SIZE = 1024
DATA_SIZE = 1020
SERVER_ADDRESS = ('localhost', 12345)

servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
servidor.bind(SERVER_ADDRESS)

# Recebe o nome do arquivo
nome_arquivo, cliente_address = servidor.recvfrom(BUFFER_SIZE)
nome_arquivo = nome_arquivo.decode()

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
with open("servidor_" + nome_arquivo, 'wb') as f:
    for i in sorted(pacotes_recebidos.keys()):
        f.write(pacotes_recebidos[i])

print(f"Arquivo salvo como {"servidor_" + nome_arquivo}")

# Altera o nome do arquivo para devolução
nome_modificado = "devolvido_" + nome_arquivo
print(f"Arquivo será devolvido como: {nome_modificado}")

# Reabre e envia o arquivo modificado de volta
with open(nome_arquivo, 'rb') as f:
    num_pacote = 0
    
    while True:
        dados = f.read(DATA_SIZE)

        if not dados:
            break

        cabecalho = struct.pack('>I', num_pacote)
        pacote = cabecalho + dados
        servidor.sendto(pacote, cliente_address)

        print(f"Enviado pacote {num_pacote} de volta")
        num_pacote += 1

# Indica ao cliente que o envio terminou
servidor.sendto(b'FIM', cliente_address)

# Espera por solicitações de reenvio
# while True:
#     dados, addr = servidor.recvfrom(BUFFER_SIZE)

#     if dados == b'FIM_CLIENTE':
#         print("Conexão finalizada com cliente.")
#         break

#     try:
#         indice = int(dados.decode())
#         print(f"Reenvio solicitado para pacote {indice}")

#         with open(nome_arquivo, 'rb') as f:
#             f.seek(indice * DATA_SIZE)
#             conteudo = f.read(DATA_SIZE)
#             cabecalho = struct.pack('>I', indice)
#             pacote = cabecalho + conteudo
#             servidor.sendto(pacote, addr)
#             print(f"Reenviado pacote {indice}")
#     except:
#         print("Erro ao interpretar solicitação do cliente.")
