import datetime
import random
from serverRDT import RDTServer

def gen_random():
    N = 4  # número de bytes
    max_value = 2**(8*N) - 1  # máximo para N bytes
    
    num = random.randint(0, max_value)
    # print(num)
    return num.to_bytes(N, byteorder='big')

names = {}
friend_lists = {}
ban_votes = {}

def format_msg(addr, user, msg):
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    return f"{addr[0]}:{addr[1]}/~{user}: {msg} {now}"

SERVER_ADDRESS = ("0.0.0.0", 12345)

def main():
    server = RDTServer(SERVER_ADDRESS, 2.0)
    print("Servidor ouvindo na porta 12345...")

    while True:
        msg, addr = server.receive()

        # se for um HI, ele vai mandar a mensagem para se identificar e esperar um nome
        if msg == b"HI":
            server.send(b"Identifique-se com: hi, meu nome eh <nome>\n", addr)  
            continue
        elif msg.startswith(b"hi, meu nome eh"):
                name_candidate = msg.split(b"hi, meu nome eh")[-1].strip().decode().strip('\x00') # melhorar esse split
                print(names.keys())
                if name_candidate in names.keys():
                    server.send(b"Nome ja em uso.\n", addr)
                else:
                    server.send(b"Nome cadastrado.\n", addr)
                    names[name_candidate] = addr
                    friend_lists[name_candidate] = set()
                    server.broadcast(f"[Servidor] {name_candidate} entrou na sala.\n", exclude=addr)
                continue
        
        nome = msg[:20].decode().strip('\x00')
        msg = msg[20:].decode()
        
        if msg.startswith("bye"):
            server.remove_addr(addr)
            server.broadcast(f"[Servidor] {nome} saiu da sala.\n")
            _ = friend_lists.pop(nome, None)
            _ = names.pop(nome, None)
            if (nome in ban_votes.keys()):
                _ = ban_votes.pop(nome, None)
            
        elif msg.startswith("list"):
            print("comando list recebido")
            user_list = "List:" + "\n".join(names.keys()) + "\n"
            server.send(user_list.encode(), addr)
            
        elif msg.startswith("mylist"):
            amigos = "MyList:" + "\n".join(friend_lists[nome]) + "\n"
            server.send(amigos.encode(), addr)
            
        elif msg.startswith("addtomylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] not in names.keys():
                    server.send("Essa pessoa nao esta cadastrada.\n".encode(), addr)
                elif parts[1] not in friend_lists[nome]:
                    friend_lists[nome].add(parts[1])
                else:
                    server.send("Essa pessoa ja esta na sua lista.\n".encode(), addr)
                
        elif msg.startswith("rmvfrommylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] not in names.keys():
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
                server.broadcast(f"[Servidor] {nome} ban {vote_count}/{needed}\n")
                
                if vote_count >= needed:
                    banned_usr_addr = names[target]
                    server.send(b"[Servidor] Voce foi banido.\n", banned_usr_addr)
                    server.remove_addr(banned_usr_addr)
                    ban_votes.pop(target)
                    friend_lists.pop(target)
                    names.pop(target)
                    
                    for i in friend_lists.values():
                        i.discard(target)
        else:
            print(msg)
            server.broadcast(format_msg(addr, nome, msg) + "\n", exclude=addr)
        
        

if __name__ == "__main__":
    main()
