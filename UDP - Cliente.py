import socket
import struct
import sys
import os

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

cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Cria o socket UDP

# Envia nome do arquivo
cliente.sendto(ARQUIVO_LOCAL.encode(), SERVER_ADDRESS)

# Envia o arquivo
with open(arquivo_path, 'rb') as f:
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

# Informa quando finaliza o envio do arquivo
cliente.sendto(b'FINAL', SERVER_ADDRESS)
print("Envio do arquivo finalizado. Aguardando resposta do servidor.")

# Recebe os pacotes numerados
pacotes = {}
maior_pacote = -1

print("Esperando pacotes")

while True:
    dados, _ = cliente.recvfrom(BUFFER_SIZE)

    if dados == b'FIM':
        print("Recebeu todos os pacotes")
        break

    indice = struct.unpack('>I', dados[:4])[0]              # Verifica o número do pacote
    conteudo = dados[4:]                                    # Contém o conteúdo do pacote

    pacotes[indice] = conteudo

    if indice > maior_pacote:
        maior_pacote = indice

# Verifica se perdeu pacotes 
falta = [i for i in range(maior_pacote + 1) if i not in pacotes]
if falta:
    print(f"Pacotes faltando: {falta}")

# Reordena os pacotes e salva o arquivo devolvido
arquivo_retorno = os.path.join('Cliente', 'devolvido_' + ARQUIVO_LOCAL)
with open(arquivo_retorno, 'wb') as f:
    for i in sorted(pacotes.keys()):
        f.write(pacotes[i])

print(f"Arquivo devolvido salvo como: {arquivo_retorno}")

cliente.sendto(b'FIM_CLIENTE', SERVER_ADDRESS)
cliente.close()                                             # Fecha o socket do cliente