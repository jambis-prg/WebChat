import datetime
import random
from serverRDT import RDTServer

names = {}          # nome_usuario -> endereço (IP, porta)
friend_lists = {}   # nome_usuario -> conjunto de amigos (nomes)
ban_votes = {}      # nome_usuario -> conjunto de nomes votados para banir

SERVER_ADDRESS = ("0.0.0.0", 12345)

def format_msg(addr, sender, msg, receiver):
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    friend_tag = ""
    
    if sender in friend_lists.get(receiver, set()):
        friend_tag = "[amigo] "

    return f"{addr[0]}:{addr[1]}/~{friend_tag}{sender}: {msg} {now}"

def main():
    server = RDTServer(SERVER_ADDRESS, 2.0)
    print("Servidor ouvindo na porta 12345...")

    while True:
        msg, addr = server.receive()

        if msg == b"HI": # Envia mensagem para o usuário se identificar
            server.send(b"Identifique-se com: hi, meu nome eh <nome>\n", addr)  
            continue
        elif msg.startswith(b"hi, meu nome eh"):
                name_candidate = msg.split(b"hi, meu nome eh")[-1].strip().decode().strip('\x00')
                print(names.keys())

                if name_candidate in names.keys():
                    server.send(b"Nome ja em uso.\n", addr)
                else:
                    server.send(b"Nome cadastrado.\n", addr)
                    names[name_candidate] = addr
                    friend_lists[name_candidate] = set()

                    # Anuncia a entrada para todos que já entraaram, exceto ele mesmo
                    server.broadcast_to_registered(f"[Servidor] {name_candidate} entrou na sala.\n", names, exclude_addr=addr)
                continue
        
        nome = msg[:20].decode().strip('\x00')
        msg = msg[20:].decode()
        
        if msg.startswith("bye"):
            server.remove_addr(addr)
            server.broadcast(f"[Servidor] {nome} saiu da sala.\n")
            friend_lists.pop(nome, None)
            names.pop(nome, None)

            if (nome in ban_votes.keys()):
                ban_votes.pop(nome, None)

        elif msg.startswith("list"):
            print("comando list recebido")
            user_list = "List: " + ", ".join(names.keys()) + "\n"
            server.send(user_list.encode(), addr)
        
        elif msg.startswith("mylist"):
            amigos = "MyList: " + ", ".join(friend_lists[nome]) + "\n"
            server.send(amigos.encode(), addr)
        
        elif msg.startswith("addtomylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] == nome:
                    server.send("Voce nao pode se adicionar na lista de amigos.\n".encode(), addr)

                elif parts[1] not in names.keys():
                    server.send("Essa pessoa nao esta cadastrada.\n".encode(), addr)
                
                elif parts[1] not in friend_lists[nome]:
                    friend_lists[nome].add(parts[1])
                
                else:
                    server.send("Essa pessoa ja esta na sua lista.\n".encode(), addr)

        elif msg.startswith("rmvfrommylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] == nome:
                    server.send("Voce nao pode se remover da propria lista.\n".encode(), addr)

                elif parts[1] not in names.keys():
                    server.send("Essa pessoa nao esta cadastrada.\n".encode(), addr)
                
                elif parts[1] in friend_lists[nome]:
                    friend_lists[nome].discard(parts[1])
                
                else:
                    server.send("Essa pessoa nao esta na sua lista.\n".encode(), addr)
        
        elif msg.startswith("ban"):
            parts = msg.split()
            if len(parts) > 1:
                target = parts[1]
                
                if target not in names.keys():
                    server.send("Essa pessoa nao esta cadastrada.\n".encode(), addr)
                
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
        else:
            print(msg)
            for receiver, addr_receiver in names.items():
                if addr_receiver == addr:  # não envia para si mesmo
                    continue
                formatted_msg = format_msg(addr, nome, msg, receiver)
                server.send((formatted_msg + "\n").encode(), addr_receiver)

if __name__ == "__main__":
    main()
