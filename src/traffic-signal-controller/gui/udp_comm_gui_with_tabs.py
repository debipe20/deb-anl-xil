import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading

class EthernetCommGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Signal Lights")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, expand=True)
        
        # Tab 1: IP Address Setup
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text="IP Setup")
        
        self.label_ip = tk.Label(self.tab1, text="Target IP Address:")
        self.label_ip.pack(padx=10, pady=5)
        
        self.entry_ip = tk.Entry(self.tab1, width=30)
        self.entry_ip.pack(padx=10, pady=5)
        
        self.label_port = tk.Label(self.tab1, text="Target Port:")
        self.label_port.pack(padx=10, pady=5)
        
        self.entry_port = tk.Entry(self.tab1, width=10)
        self.entry_port.pack(padx=10, pady=5)
        
        self.connect_button = tk.Button(self.tab1, text="Start", command=self.start_udp)
        self.connect_button.pack(padx=10, pady=5)
        
        self.send_button = tk.Button(self.tab1, text="Send Message", command=self.send_message)
        self.send_button.pack(padx=10, pady=5)
        self.send_button.config(state=tk.DISABLED)
        
        self.message_entry = tk.Entry(self.tab1, width=50)
        self.message_entry.pack(padx=10, pady=5)
        
        self.output = tk.Text(self.tab1, height=10, width=50, state=tk.DISABLED)
        self.output.pack(padx=10, pady=10)
        
        # Tab 2: Traffic Lights
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text="Traffic Lights")
        
        self.traffic_canvas = tk.Canvas(self.tab2, width=50, height=150)
        self.traffic_canvas.pack(padx=10, pady=5)
        
        self.red_light = self.traffic_canvas.create_oval(10, 10, 40, 40, fill='gray')
        self.yellow_light = self.traffic_canvas.create_oval(10, 55, 40, 85, fill='gray')
        self.green_light = self.traffic_canvas.create_oval(10, 100, 40, 130, fill='gray')
        
        self.sock = None
        self.target_address = None
    
    def update_traffic_light(self, light_color):
        # Reset all lights to gray
        self.traffic_canvas.itemconfig(self.red_light, fill='gray')
        self.traffic_canvas.itemconfig(self.yellow_light, fill='gray')
        self.traffic_canvas.itemconfig(self.green_light, fill='gray')
        
        # Set the appropriate light color
        if light_color == 'red':
            self.traffic_canvas.itemconfig(self.red_light, fill='red')
        elif light_color == 'yellow':
            self.traffic_canvas.itemconfig(self.yellow_light, fill='yellow')
        elif light_color == 'green':
            self.traffic_canvas.itemconfig(self.green_light, fill='green')
    
    def start_udp(self):
        try:
            target_ip = self.entry_ip.get()
            target_port = int(self.entry_port.get())
            self.target_address = (target_ip, target_port)
            
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.update_traffic_light('green')  # Green light indicates ready to communicate
            self.output.config(state=tk.NORMAL)
            self.output.insert(tk.END, f"UDP Socket created. Ready to communicate with {target_ip}:{target_port}\n")
            self.output.config(state=tk.DISABLED)
            self.send_button.config(state=tk.NORMAL)
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            self.update_traffic_light('red')  # Red light indicates an error
            messagebox.showerror("Socket Error", f"Could not create UDP socket: {e}")
    
    def send_message(self):
        message = self.message_entry.get()
        if self.sock and self.target_address:
            try:
                self.update_traffic_light('yellow')  # Yellow light indicates sending data
                self.sock.sendto(message.encode('utf-8'), self.target_address)
                self.output.config(state=tk.NORMAL)
                self.output.insert(tk.END, f"Sent: {message}\n")
                self.output.config(state=tk.DISABLED)
                self.update_traffic_light('green')  # Green light after sending
            except Exception as e:
                self.update_traffic_light('red')  # Red light indicates an error
                messagebox.showerror("Send Error", f"Could not send message: {e}")
    
    def receive_message(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                if data:
                    self.update_traffic_light('yellow')  # Yellow light indicates receiving data
                    self.output.config(state=tk.NORMAL)
                    self.output.insert(tk.END, f"Received from {addr}: {data.decode('utf-8')}\n")
                    self.output.config(state=tk.DISABLED)
                    self.update_traffic_light('green')  # Green light after receiving
            except Exception as e:
                self.update_traffic_light('red')  # Red light indicates an error
                self.output.config(state=tk.NORMAL)
                self.output.insert(tk.END, f"Error receiving data: {e}\n")
                self.output.config(state=tk.DISABLED)
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = EthernetCommGUI(root)
    root.mainloop()
