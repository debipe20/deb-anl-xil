import tkinter as tk
from tkinter import messagebox
import socket
import threading

class EthernetCommGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UDP Ethernet Communication")
        
        self.label = tk.Label(root, text="Target IP Address:")
        self.label.pack(padx=10, pady=5)
        
        self.entry_ip = tk.Entry(root, width=30)
        self.entry_ip.pack(padx=10, pady=5)
        
        self.label_port = tk.Label(root, text="Target Port:")
        self.label_port.pack(padx=10, pady=5)
        
        self.entry_port = tk.Entry(root, width=10)
        self.entry_port.pack(padx=10, pady=5)
        
        self.connect_button = tk.Button(root, text="Start", command=self.start_udp)
        self.connect_button.pack(padx=10, pady=5)
        
        self.send_button = tk.Button(root, text="Send Message", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)
        self.send_button.config(state=tk.DISABLED)
        
        self.message_entry = tk.Entry(root, width=50)
        self.message_entry.pack(padx=10, pady=5)
        
        self.output = tk.Text(root, height=10, width=50, state=tk.DISABLED)
        self.output.pack(padx=10, pady=10)
        
        self.sock = None
        self.target_address = None
    
    def start_udp(self):
        try:
            target_ip = self.entry_ip.get()
            target_port = int(self.entry_port.get())
            self.target_address = (target_ip, target_port)
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.output.config(state=tk.NORMAL)
            self.output.insert(tk.END, f"UDP Socket created. Ready to communicate with {target_ip}:{target_port}\n")
            self.output.config(state=tk.DISABLED)
            self.send_button.config(state=tk.NORMAL)
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Socket Error", f"Could not create UDP socket: {e}")
    
    def send_message(self):
        message = self.message_entry.get()
        if self.sock and self.target_address:
            try:
                self.sock.sendto(message.encode('utf-8'), self.target_address)
                self.output.config(state=tk.NORMAL)
                self.output.insert(tk.END, f"Sent: {message}\n")
                self.output.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("Send Error", f"Could not send message: {e}")
    
    def receive_message(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data:
                    self.output.config(state=tk.NORMAL)
                    self.output.insert(tk.END, f"Received from {addr}: {data.decode('utf-8')}\n")
                    self.output.config(state=tk.DISABLED)
            except Exception as e:
                self.output.config(state=tk.NORMAL)
                self.output.insert(tk.END, f"Error receiving data: {e}\n")
                self.output.config(state=tk.DISABLED)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = EthernetCommGUI(root)
    root.mainloop()
