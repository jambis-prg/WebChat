import datetime
from serverRDT import RDTServer
import signal
import sys

names = {}                                          # nome_usuario -> endereço (IP, porta)
friend_lists = {}                                   # nome_usuario -> conjunto de amigos (nomes)
ban_votes = {}                                      # nome_usuario -> conjunto de nomes votados para banir

# Manipulador de sinal para Ctrl+C
def handler(sig, frame):
        print("\n[!] Ctrl+C detectado, encerrando servidor...")
        sys.exit(0)
        
signal.signal(signal.SIGINT, handler)

SERVER_ADDRESS = ("0.0.0.0", 12345)

# Formata a mensagem para exibição
def format_msg(addr, sender, msg, receiver):
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    friend_tag = ""
    
    if sender in friend_lists.get(receiver, set()):
        friend_tag = "[amigo] "

    return f"{addr[0]}:{addr[1]}/~{friend_tag}{sender}: {msg} {now}"

# Função principal do servidor
def main():
    server = RDTServer(SERVER_ADDRESS, 2.0)
    print(f"Servidor ouvindo na porta 12345...")

    # Loop principal
    while True:
        msg, addr = server.receive()                # recebe a mensagem e o endereço

        if msg == b"HI":                            # envia mensagem para o usuário se identificar
            print("[Servidor] Alguem mandou um HI.")
            server.send(b"Identifique-se com: hi, meu nome eh <nome>\n", addr)  
            continue
        elif msg.startswith(b"hi, meu nome eh"):    # trata a mensagem de identificação
            name_candidate = msg.split(b"hi, meu nome eh")[-1].strip().decode().strip('\x00')
            print(f"[Servidor] Tentativa de usar nome '{name_candidate}'")

            if name_candidate in names.keys():      # verifica se o nome já está em uso
                print("[Servidor] Nome ja em uso.")
                server.send(b"Nome ja em uso.\n", addr)
            else:
                print("[Servidor] Nome cadastrado.")
                server.send(b"Nome cadastrado.\n", addr)
                names[name_candidate] = addr
                friend_lists[name_candidate] = set()

                # Anuncia a entrada para todos que já entraram, exceto ele mesmo
                server.broadcast_to_registered(f"[Servidor] {name_candidate} entrou na sala.\n", names, exclude_addr=addr)
            continue

        # Processa a mensagem do usuário
        nome = msg[:20].decode().strip('\x00')
        msg = msg[20:].decode().lstrip()[:-1]

        if msg.startswith("bye"):                   # trata a mensagem de saída
            server.remove_addr(addr)
            print(f"[Servidor] '{nome}' saiu da sala.")
            server.broadcast(f"[Servidor] {nome} saiu da sala.\n")
            friend_lists.pop(nome, None)
            names.pop(nome, None)

            if (nome in ban_votes.keys()):
                ban_votes.pop(nome, None)

        elif msg.startswith("list"):                # trata a mensagem de listagem de usuários
            print(f"[Servidor] '{nome}' esta listando a sala.")
            user_list = "List: " + ", ".join(names.keys()) + "\n"
            server.send(user_list.encode(), addr)

        elif msg.startswith("mylist"):              # trata a mensagem de listagem de amigos
            print(f"[Servidor] '{nome}' esta listando seus amigos.")
            amigos = "MyList: " + ", ".join(friend_lists[nome]) + "\n"
            server.send(amigos.encode(), addr)

        elif msg.startswith("addtomylist"):         # trata a mensagem de adição à lista de amigos
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] == nome:
                    print(f"[Servidor] '{nome}' tentou se adicionar a lista de amigos.")
                    server.send("Voce nao pode se adicionar na lista de amigos.\n".encode(), addr)

                elif parts[1] not in names.keys():
                    print(f"[Servidor] '{nome}' tentou adicionar '{parts[1]}' na lista de amigos mas ele nao esta na sala.")
                    server.send("Essa pessoa nao esta cadastrada.\n".encode(), addr)
                
                elif parts[1] not in friend_lists[nome]:
                    print(f"[Servidor] '{nome}' adicionou '{parts[1]}' na lista de amigos.")
                    friend_lists[nome].add(parts[1])
                
                else:
                    print(f"[Servidor] '{parts}' ja esta na lista de amigos de {nome}.")
                    server.send("Essa pessoa ja esta na sua lista de amigos.\n".encode(), addr)

        elif msg.startswith("rmvfrommylist"):       # trata a mensagem de remoção da lista de amigos
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] == nome:
                    print(f"[Servidor] '{nome}' tentou se remover a lista de amigos.")
                    server.send("Voce nao pode se remover da propria lista.\n".encode(), addr)

                elif parts[1] not in names.keys():
                    print(f"[Servidor] '{nome}' tentou remover '{parts[1]}' da lista de amigos mas ele nao esta na sala.")
                    server.send("Essa pessoa nao esta cadastrada.\n".encode(), addr)
                
                elif parts[1] in friend_lists[nome]:
                    print(f"[Servidor] '{nome}' removeu '{parts[1]}' da lista de amigos.")
                    friend_lists[nome].discard(parts[1])
                
                else:
                    print(f"[Servidor] '{parts[1]}' nao esta na lista de amigos de {nome}.")
                    server.send("Essa pessoa nao esta na sua lista de amigos.\n".encode(), addr)

        elif msg.startswith("ban"):                 # trata a mensagem de banimento
            parts = msg.split()
            if len(parts) > 1:
                target = parts[1]
                
                if target not in names.keys():
                    print("[Servidor] Tentativa de banir uma pessoa nao cadastrada.")
                    server.send("Essa pessoa nao esta cadastrada.\n".encode(), addr)
                else:
                    if target not in ban_votes:
                        ban_votes[target] = set()

                    ban_votes[target].add(nome)
                    vote_count = len(ban_votes[target])
                    needed = len(names) // 2 + 1
                    server.broadcast(f"[Servidor] {nome} votou: ban {target} {vote_count}/{needed}\n")
                    
                    if vote_count >= needed:
                        banned_usr_addr = names[target]
                        server.send(b"[Servidor] Voce foi banido.\n", banned_usr_addr)
                        server.remove_addr(banned_usr_addr)
                        ban_votes.pop(target)
                        names.pop(target)

                        for i in friend_lists.values():
                            i.discard(target)
                        friend_lists.pop(target)
        else:                                       # trata mensagens de chat
            print(f"[Servidor] BroadCast Message: '{msg}' from '{nome}'")
            for receiver, addr_receiver in names.items():
                if addr_receiver == addr:           # não envia para si mesmo
                    continue
                formatted_msg = format_msg(addr, nome, msg, receiver)
                server.send((formatted_msg + "\n").encode(), addr_receiver)

# Inicializa o servidor
if __name__ == "__main__":
    main()