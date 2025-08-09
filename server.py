import socket
import threading
import datetime
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
friend_lists = {}
ban_votes = {}

def broadcast(message, exclude=None):
    for nome, addr in clients:
        try:
            if nome != exclude:
                sender = RDTSender(addr, 2.0)
                sender.send(message)
        except:
            pass

def format_msg(addr, user, msg):
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    return f"{addr[0]}:{addr[1]}/~{user}: {msg} {now}"

# def handle_client(conn, addr):
#     name = None
#     try:
#         conn.send(b"Identifique-se com: hi, meu nome eh <nome>\n")
#         while True:
#             msg = conn.recv(1024).decode().strip()
#             while True:
#                 msg = conn.recv(1024)
#                 if not msg:
#                     break  # cliente desconectou

#                 msg = msg.decode().strip()
#                 if msg == "":
#                     continue  # ignora linhas vazias

#             if msg.startswith("hi, meu nome eh"):
#                 name_candidate = msg.split("hi, meu nome eh")[-1].strip()
#                 if name_candidate in clients.values():
#                     conn.send(b"Nome ja em uso.\n")
#                 else:
#                     name = name_candidate
#                     clients[conn] = name
#                     friend_lists[name] = set()
#                     broadcast(f"[Servidor] {
#                               name} entrou na sala.\n", exclude=conn)
#                     break
#             else:
#                 conn.send(b"Comando invalido. Use: hi, meu nome eh <nome>\n")

#         while True:
#             msg = conn.recv(1024).decode().strip()
#             if msg == "bye":
#                 break
#             elif msg == "list":
#                 user_list = "\n".join(clients.values()) + "\n"
#                 conn.send(user_list.encode())
#             elif msg == "mylist":
#                 amigos = "\n".join(friend_lists[name]) + "\n"
#                 conn.send(amigos.encode())
#             elif msg.startswith("addtomylist"):
#                 parts = msg.split()
#                 if len(parts) > 1:
#                     friend_lists[name].add(parts[1])
#             elif msg.startswith("rmvfrommylist"):
#                 parts = msg.split()
#                 if len(parts) > 1:
#                     friend_lists[name].discard(parts[1])
#             elif msg.startswith("ban"):
#                 parts = msg.split()
#                 if len(parts) > 1:
#                     target = parts[1]
#                     if target not in clients.values():
#                         conn.send(b"Usuario nao encontrado.\n")
#                         continue
#                     if target not in ban_votes:
#                         ban_votes[target] = set()
#                     ban_votes[target].add(name)
#                     vote_count = len(ban_votes[target])
#                     needed = len(clients) // 2 + 1
#                     broadcast(f"[Servidor] {name} ban {vote_count}/{needed}\n")
#                     if vote_count >= needed:
#                         for c, n in list(clients.items()):
#                             if n == target:
#                                 c.send(b"[Servidor] Voce foi banido.\n")
#                                 c.close()
#                                 del clients[c]
#                                 break
#                         del ban_votes[target]
#             else:
#                 tag = (
#                     "[ amigo ] "
#                     if any(
#                         name in friend_lists[u] and u == clients[conn]
#                         for u in friend_lists
#                     )
#                     else ""
#                 )
#                 broadcast(format_msg(addr, tag + name, msg) +
#                           "\n", exclude=conn)
#     finally:
#         if conn in clients:
#             del clients[conn]
#             broadcast(f"[Servidor] {name} saiu da sala.\n")
#         conn.close()

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
        cliente = RDTSender(addr, 2.0)
        
        # se ele esta iniciando a conversa
        # se ele ja esta logado
        # threading.Thread(target=handle_client, args=(
        #     conn, addr), daemon=True).start()
        
        # se for um HI, ele vai mandar a mensagem para se identificar e esperar um nome
        if msg == b"HI":
            cliente.send(b"Identifique-se com: hi, meu nome eh <nome>\n")  
        elif msg.startswith("hi, meu nome eh"):
                name_candidate = msg.split("hi, meu nome eh")[-1].strip() # melhorar esse split
                if name_candidate in clients.values():
                    cliente.send(b"Nome ja em uso.\n")
                else:
                    cliente.send(b"Nome cadastrado.\n")
                    name = name_candidate
                    clients[name] = adrr
                    friend_lists[name] = set()
                    broadcast(f"[Servidor] {
                              name} entrou na sala.\n", exclude=name)
                    break
        
        nome = msg[:20].decode()
        msg = msg[20:].decode()
        
        if msg == "bye":
            del clients[nome]
            del friend_lists[nome]
            
        elif msg == "list":
            user_list = "\n".join(clients.values()) + "\n"
            cliente.send(user_list.encode())
            
        elif msg == "mylist":
            amigos = "\n".join(friend_lists[name]) + "\n"
            cliente.send(amigos.encode())
            
        elif msg.startswith("addtomylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] not in clients.keys():
                    cliente.send("Essa pessoa nao esta cadastrada.\n".encode())
                friend_lists[nome].add(parts[1])
                
        elif msg.startswith("rmvfrommylist"):
            parts = msg.split()
            if len(parts) > 1:
                if parts[1] not in clients.keys():
                    cliente.send("Essa pessoa nao esta cadastrada.\n".encode())
                friend_lists[name].discard(parts[1])
                
        elif msg.startswith("ban"):
            parts = msg.split()
            if len(parts) > 1:
                target = parts[1]
                
                if target not in clients.keys():
                    cliente.send("Essa pessoa nao esta cadastrada.\n".encode())
                
                if target not in ban_votes:
                    ban_votes[target] = set()

                ban_votes[target].add(name)
                vote_count = len(ban_votes[target])
                needed = len(clients) // 2 + 1
                broadcast(f"[Servidor] {name} ban {vote_count}/{needed}\n")
                
                if vote_count > needed:
                    banned_usr = RDTSender(clients[target], 2.0)
                    banned_usr.send(b"[Servidor] Voce foi banido.\n")
                    del clients[c]
                    del ban_votes[target]
                    del friend_lists[target]
                    for i in friend_lists.values():
                        i.discart(target)
        else:
            broadcast(format_msg(addr, name, msg) +
                      "\n", exclude=conn)
        
        

if __name__ == "__main__":
    main()
