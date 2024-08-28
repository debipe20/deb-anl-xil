import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import subprocess

class EthernetCommGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UDP Ethernet Communication with Traffic Lights")
        
        # Set the theme to "clam" for a more modern look
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 12))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=[5, 5], relief='flat')
        self.style.configure('TLabel', font=('Segoe UI', 11))
        self.style.configure('TEntry', font=('Segoe UI', 11), padding=[5, 5])
        self.style.configure('TText', font=('Segoe UI', 11), padding=[5, 5])
        
        # Create notebook for tabs with a custom background color
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=10, pady=10, expand=True)
        
        # Tab 1: IP Address Setup
        self.tab1 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.tab1, text="IP Setup")
        
        self.label_ip = ttk.Label(self.tab1, text="Target IP Address:", style='TLabel')
        self.label_ip.pack(padx=10, pady=5)
        
        self.entry_ip = ttk.Entry(self.tab1, width=30, style='TEntry')
        self.entry_ip.pack(padx=10, pady=5)
        
        self.label_port = ttk.Label(self.tab1, text="Target Port:", style='TLabel')
        self.label_port.pack(padx=10, pady=5)
        
        self.entry_port = ttk.Entry(self.tab1, width=10, style='TEntry')
        self.entry_port.pack(padx=10, pady=5)
        
        self.connect_button = ttk.Button(self.tab1, text="Start", command=self.start_udp, style='TButton')
        self.connect_button.pack(padx=10, pady=10)
        
        self.ping_button = ttk.Button(self.tab1, text="Ping Target", command=self.ping_target, style='TButton')
        self.ping_button.pack(padx=10, pady=10)
        
        self.send_button = ttk.Button(self.tab1, text="Send Message", command=self.send_message, style='TButton')
        self.send_button.pack(padx=10, pady=10)
        self.send_button.config(state=tk.DISABLED)
        
        self.message_entry = ttk.Entry(self.tab1, width=50, style='TEntry')
        self.message_entry.pack(padx=10, pady=5)
        
        self.output = tk.Text(self.tab1, height=10, width=50, font=('Segoe UI', 11), bg="#f0f0f0", relief="flat", borderwidth=0)
        self.output.pack(padx=10, pady=10)
        self.output.config(state=tk.DISABLED)
        
        # Tab 2: Traffic Lights
        self.tab2 = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.tab2, text="Traffic Lights")
        
        self.traffic_canvas = tk.Canvas(self.tab2, width=50, height=150, bg='#282c34', highlightthickness=0)
        self.traffic_canvas.pack(padx=10, pady=10)
        
        self.red_light = self.traffic_canvas.create_oval(10, 10, 40, 40, fill='gray', outline='')
        self.yellow_light = self.traffic_canvas.create_oval(10, 55, 40, 85, fill='gray', outline='')
        self.green_light = self.traffic_canvas.create_oval(10, 100, 40, 130, fill='gray', outline='')
        
        self.sock = None
        self.target_address = None
    
    def update_traffic_light(self, light_color):
        # Reset all lights to gray
        self.traffic_canvas.itemconfig(self.red_light, fill='gray')
        self.traffic_canvas.itemconfig(self.yellow_light, fill='gray')
        self.traffic_canvas.itemconfig(self.green_light, fill='gray')
        
        # Set the appropriate light color
        if light_color == 'red':
            self.traffic_canvas.itemconfig(self.red_light, fill='#e81123')  # Windows 11 Red
        elif light_color == 'yellow':
            self.traffic_canvas.itemconfig(self.yellow_light, fill='#ffb900')  # Windows 11 Yellow
        elif light_color == 'green':
            self.traffic_canvas.itemconfig(self.green_light, fill='#16c60c')  # Windows 11 Green
    
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
    
    def ping_target(self):
        target_ip = self.entry_ip.get()
        try:
            # Use the `ping` command to ping the target IP address
            output = subprocess.run(["ping", "-c", "4", target_ip], capture_output=True, text=True)
            # Display the output in the text box
            self.output.config(state=tk.NORMAL)
            self.output.insert(tk.END, f"Pinging {target_ip}...\n")
            self.output.insert(tk.END, output.stdout)
            self.output.config(state=tk.DISABLED)
        except Exception as e:
            self.output.config(state=tk.NORMAL)
            self.output.insert(tk.END, f"Error pinging {target_ip}: {e}\n")
            self.output.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = EthernetCommGUI(root)
    root.mainloop()
