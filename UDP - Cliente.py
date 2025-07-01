import socket
import struct
import sys

BUFFER_SIZE = 1024
DATA_SIZE = 1020
SERVER_ADDRESS = ('localhost', 12345)
ARQUIVO_LOCAL = sys.argv[1]

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# envia nome do arquivo
cliente.sendto(ARQUIVO_LOCAL.encode(), SERVER_ADDRESS)

# envia o arquivo
with open(ARQUIVO_LOCAL, 'rb') as f:
    num_pacote = 0

    while True:
        dados = f.read(DATA_SIZE)

        if not dados:
            break

        cabecalho = struct.pack('>I', num_pacote) 
        pacote = cabecalho + dados
        cliente.sendto(pacote, SERVER_ADDRESS)

        print(f"Enviado pacote {num_pacote}")
        num_pacote += 1

# dizer qnd acabar de enviar o arq
cliente.sendto(b'FINAL', SERVER_ADDRESS)

# receber os pacotes numerados

pacotes = {}
maior_pacote = -1

print("Esperando pacotes")

while True:
    dados, _ = cliente.recvfrom(BUFFER_SIZE)

    if dados == b'FIM':
        print("Recebeu todos os pacotes")
        break

    indice = struct.unpack('>I', dados[:4])[0] # pega os 4 bytes para vê o num do pacote
    conteudo = dados[4:] #o resto eh o conteudo

    pacotes[indice] = conteudo

    if indice > maior_pacote:
        maior_pacote = indice

# verifica se perdeu pacotes 
falta = [i for i in range(maior_pacote + 1) if i not in pacotes]
if falta:
    print(f"Pacotes faltando: {falta}")

# pedir os pacotes faltando
# for num in falta:
#     tentativas = 3

#     while tentativas > 0:
#         cliente.sendto(f"{num}".encode(), SERVER_ADDRESS) #solicita o pacote num

#         dados, _ = cliente.recvfrom(BUFFER_SIZE) #recebe o pacote

#         if len(dados) > 4:
#             recebido = struct.unpack('>I', dados[:4])[0]

#             if recebido == num:
#                 pacotes[num] = dados[4:]
#                 print(f"Recebeu pacote {num}")
#                 break

#         tentativas -= 1
#         print(f"Tentando novamente pacote {num}")

# juntar todos os pacotes num arquivo
with open('devolvido_cliente_' + ARQUIVO_LOCAL, 'wb') as f:
    for i in sorted(pacotes.keys()):
        f.write(pacotes[i])

cliente.sendto(b'FIM_CLIENTE', SERVER_ADDRESS)