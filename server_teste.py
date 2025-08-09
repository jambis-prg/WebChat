import socket
import threading
import datetime

clients = {}
friend_lists = {}
ban_votes = {}
# tem alguns erros de saida de clientes e o nome nao esta certinho
# no caso do lado do cliente


def broadcast(message, exclude=None):
    for client in clients:
        if client != exclude:
            try:
                client.sendall(message.encode())
            except:
                pass


def format_msg(addr, user, msg):
    now = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    return f"{addr[0]}:{addr[1]}/~{user}: {msg} {now}"


def handle_client(conn, addr):
    name = None
    try:
        conn.send(b"Identifique-se com: hi, meu nome eh <nome>\n")
        print("A identificar")

        while True:
            msg = conn.recv(1024).decode().strip()
            print("msg recebida =" + msg)

            if not msg:
                break  # cliente desconectou
            if msg == "":
                continue  # ignora linhas vazias

            if msg.startswith("hi, meu nome eh"):
                name_candidate = msg.split("hi, meu nome eh")[-1].strip()
                print("Candidato - " + name_candidate)
                if name_candidate in clients.values():
                    conn.send(b"Nome ja em uso.\n")
                else:
                    name = name_candidate
                    print(name + " conectado")
                    clients[conn] = name
                    friend_lists[name] = set()
                    broadcast(f"[Servidor] {name} entrou na sala.\n", exclude=conn)
                    break
            else:
                conn.send(b"Comando invalido. Use: hi, meu nome eh <nome>\n")
                print("Comando invalido -" + msg)

        while True:
            msg = conn.recv(1024).decode().strip()
            print("-----" + msg)
            if not msg:
                break
            if msg == "bye":
                break
            elif msg == "list":
                user_list = "List:\n" + "\n".join(clients.values()) + "\n"
                conn.send(user_list.encode())
            elif msg == "mylist":
                amigos = "Mylist:\n" + "\n".join(friend_lists[name]) + "\n"
                conn.send(amigos.encode())
            elif msg.startswith("addtomylist"):
                parts = msg.split()
                if len(parts) > 1:
                    friend_lists[name].add(parts[1])
            elif msg.startswith("rmvfrommylist"):
                parts = msg.split()
                if len(parts) > 1:
                    friend_lists[name].discard(parts[1])
            elif msg.startswith("ban"):
                parts = msg.split()
                if len(parts) > 1:
                    target = parts[1]
                    if target not in clients.values():
                        conn.send(b"Usuario nao encontrado.\n")
                        continue
                    if target not in ban_votes:
                        ban_votes[target] = set()
                    ban_votes[target].add(name)
                    vote_count = len(ban_votes[target])
                    needed = len(clients) // 2 + 1
                    broadcast(f"[Servidor] {name} ban {vote_count}/{needed}\n")
                    if vote_count >= needed:
                        for c, n in list(clients.items()):
                            if n == target:
                                c.send(b"[Servidor] Voce foi banido.\n")
                                c.close()
                                del clients[c]
                                break
                        del ban_votes[target]
            else:
                tag = (
                    "[ amigo ] "
                    if any(
                        name in friend_lists[u] and u == clients[conn]
                        for u in friend_lists
                    )
                    else ""
                )
                broadcast(format_msg(addr, tag + name, msg) + "\n", exclude=conn)
    finally:
        if conn in clients:
            del clients[conn]
            broadcast(f"[Servidor] {name} saiu da sala.\n")
        conn.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 12345))
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.listen()
    print("Servidor ouvindo na porta 12345...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
