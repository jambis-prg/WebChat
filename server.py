import socket
import threading
import datetime
import random
from sender import RDTSender
from receiver import RDTReceiver
from typing import Tuple

def gen_random():
    N = 4  # número de bytes
    max_value = 2**(8*N) - 1  # máximo para N bytes
    
    num = random.randint(0, max_value)
    print(num)
    return num.to_bytes(N, byteorder='big')

clients = {}
names = set()
friend_lists = {}
ban_votes = {}

def broadcast(message, exclude=None):
    for addr, sender in clients.items():
        try:
            print(f'{addr} x {exclude}')
            if addr != exclude:
                sender.send(message.encode())
        except Exception as e:
            print(e)
            pass

def format_msg(addr, user, msg):
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    return f"{addr[0]}:{addr[1]}/~{user}: {msg} {now}"

SERVER_ADDRESS = ("0.0.0.0", 12345)
def main():
    servidor = RDTReceiver(SERVER_ADDRESS, None)
    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.bind((SERVER_ADDRESS, 12345)) 
    # server.listen()
    print("Servidor ouvindo na porta 12345...")

    while True:
        # conn, addr = server.accept()
        msg, addr = servidor.receive()

        if (addr in clients.keys()):
            cliente = clients[addr]
        else:
            cliente = RDTSender(addr, 2.0)
            clients[addr] = cliente
        
        # se ele esta iniciando a conversa
        # se ele ja esta logado
        # threading.Thread(target=handle_client, args=(
        #     conn, addr), daemon=True).start()
        
        # se for um HI, ele vai mandar a mensagem para se identificar e esperar um nome
        if msg == b"HI":
            cliente.send(b"Identifique-se com: hi, meu nome eh <nome>\n")  
        elif msg.startswith(b"hi, meu nome eh"):
                name_candidate = msg.split(b"hi, meu nome eh")[-1].strip() # melhorar esse split
                if name_candidate in names:
                    cliente.send(b"Nome ja em uso.\n")
                else:
                    cliente.send(b"Nome cadastrado.\n")
                    name = name_candidate
                    names.add(name)
                    friend_lists[name] = set()
                    broadcast(f"[Servidor] {
                              name} entrou na sala.\n", exclude=addr)
                continue
        
        nome = msg[:20].decode()
        msg = msg[20:].decode()
        
        if msg == "bye":
            del clients[addr]
            del friend_lists[nome]
            
        elif msg == "list":
            user_list = "\n".join(names.values()) + "\n"
            cliente.send(user_list.encode())
            
        elif msg == "mylist":
            amigos = "\n".join(friend_lists[nome]) + "\n"
            cliente.send(amigos.encode())
            
        elif msg.startswith("addtomylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] not in names.keys():
                    cliente.send("Essa pessoa nao esta cadastrada.\n".encode())
                friend_lists[nome].add(parts[1])
                
        elif msg.startswith("rmvfrommylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] not in names.keys():
                    cliente.send("Essa pessoa nao esta cadastrada.\n".encode())
                friend_lists[nome].discard(parts[1])
                
        elif msg.startswith("ban"):
            parts = msg.split()
            if len(parts) > 1:
                target = parts[1]
                
                if target not in names.keys():
                    cliente.send("Essa pessoa nao esta cadastrada.\n".encode())
                
                if target not in ban_votes:
                    ban_votes[target] = set()

                ban_votes[target].add(nome)
                vote_count = len(ban_votes[target])
                needed = len(names) // 2 + 1
                broadcast(f"[Servidor] {nome} ban {vote_count}/{needed}\n")
                
                if vote_count > needed:
                    banned_usr = clients[target]
                    banned_usr.send(b"[Servidor] Voce foi banido.\n")
                    del clients[target]
                    del ban_votes[target]
                    del friend_lists[target]
                    names.discard(target)
                    for i in friend_lists.values():
                        i.discart(target)
        else:
            broadcast(format_msg(addr, nome, msg) +
                      "\n", exclude=addr)
        
        

if __name__ == "__main__":
    main()
