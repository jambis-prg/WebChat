import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox


class ChatApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Cliente TCP")

        self.sock = None
        self.connected = False
        self.server_ip = "127.0.0.1"
        self.server_port = None
        self.username = None

        self.frame_conn = None
        self.frame_chat = None

        self.create_conn_screen()

    def create_conn_screen(self):
        if self.frame_chat:
            self.frame_chat.destroy()

        self.frame_conn = tk.Frame(self.master)
        self.frame_conn.pack(padx=20, pady=20)

        tk.Label(self.frame_conn, text="Porta do servidor:").pack(pady=5)
        self.entry_port = tk.Entry(self.frame_conn)
        self.entry_port.pack(pady=5)

        tk.Label(self.frame_conn, text="Seu nome:").pack(pady=5)
        self.entry_name = tk.Entry(self.frame_conn)
        self.entry_name.pack(pady=5)

        btn_connect = tk.Button(
            self.frame_conn, text="Conectar", command=self.connect_to_server
        )
        btn_connect.pack(pady=10)

    def create_chat_screen(self):
        if self.frame_conn:
            self.frame_conn.destroy()

        self.frame_chat = tk.Frame(self.master)
        self.frame_chat.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.text_area = scrolledtext.ScrolledText(
            self.frame_chat, wrap=tk.WORD, state="disabled", height=20
        )
        self.text_area.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.entry_msg = tk.Entry(self.frame_chat)
        self.entry_msg.pack(padx=5, pady=(0, 5), fill=tk.X)
        self.entry_msg.bind("<Return>", self.send_message)

        btn_send = tk.Button(self.frame_chat, text="Enviar", command=self.send_message)
        btn_send.pack(padx=5, pady=(0, 5))

    def connect_to_server(self):
        try:
            port = int(self.entry_port.get())
            self.username = self.entry_name.get().strip()
            if not self.username:
                messagebox.showerror("Erro", "Digite um nome.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Porta inválida.")
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.server_ip, port))
            self.server_port = port
            self.connected = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.create_chat_screen()
            self.add_message(f"Conectado ao servidor {self.server_ip}:{port}\n")

            # envia identificação automática
            self.sock.sendall(f"hi, meu nome eh {self.username}\n".encode())

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar: {e}")

    def receive_messages(self):
        while self.connected:
            try:
                data = self.sock.recv(1024)
                if not data:
                    self.safe_add_message("Conexão encerrada pelo servidor.\n")
                    break
                self.safe_add_message(data.decode())
            except:
                break

    def send_message(self, event=None):
        msg = self.entry_msg.get().strip()
        if msg:
            try:
                self.sock.sendall((msg + "\n").encode())
                self.entry_msg.delete(0, tk.END)
            except Exception as e:
                self.safe_add_message(f"Erro ao enviar: {e}\n")

    def add_message(self, message):
        """Insere texto na área de mensagens (apenas na thread principal)."""
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, message)
        self.text_area.config(state="disabled")
        self.text_area.see(tk.END)

    def safe_add_message(self, message):
        """Garante que a atualização da UI ocorra na thread principal."""
        self.master.after(0, self.add_message, message)


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
