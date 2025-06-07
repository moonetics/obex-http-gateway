import tkinter as tk
from tkinter import filedialog, messagebox
import bluetooth
from PyOBEX.client import Client
import threading
import os

# Konstanta OBEX
GATEWAY_NAME = "BT-Gateway"
OBEX_PUSH_UUID = "00001105-0000-1000-8000-00805F9B34FB"

class GatewayClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OBEX Push Client GUI")
        self.root.geometry("500x400")

        # File selection
        self.file_path = tk.StringVar()
        file_frame = tk.Frame(root)
        file_frame.pack(pady=10, fill=tk.X, padx=10)
        tk.Label(file_frame, text="File:").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=self.file_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(file_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT, padx=5)

        # Device list
        list_frame = tk.Frame(root)
        list_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)
        tk.Label(list_frame, text="Discovered Devices:").pack(anchor=tk.W)
        self.listbox = tk.Listbox(list_frame)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Scan Devices", command=self.scan_devices).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Send File", command=self.send_file).pack(side=tk.LEFT, padx=5)

        # Status
        self.status = tk.StringVar(value="Ready")
        tk.Label(root, textvariable=self.status, anchor=tk.W).pack(fill=tk.X, padx=10, pady=5)

        # Storage for devices
        self.devices = []

    def browse_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path.set(path)
            self.status.set(f"Selected file: {os.path.basename(path)}")

    def scan_devices(self):
        def _scan():
            self.status.set("Scanning for devices...")
            self.listbox.delete(0, tk.END)
            self.devices.clear()
            try:
                found = bluetooth.discover_devices(duration=8, lookup_names=True)
                if not found:
                    messagebox.showinfo("Scan", "No Bluetooth devices found.")
                for addr, name in found:
                    display = f"{addr}  -  {name}"
                    self.devices.append((addr, name))
                    self.listbox.insert(tk.END, display)
                self.status.set(f"Scan complete: {len(found)} devices found.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to scan: {e}")
                self.status.set("Error during scan")

        threading.Thread(target=_scan, daemon=True).start()

    def send_file(self):
        sel = self.listbox.curselection()
        file = self.file_path.get()
        if not sel:
            messagebox.showwarning("Send", "Select a device from the list.")
            return
        if not file:
            messagebox.showwarning("Send", "Select a file first.")
            return

        addr, name = self.devices[sel[0]]
        self.status.set(f"Connecting to {name} ({addr})...")

        def _send():
            try:
                services = bluetooth.find_service(uuid=OBEX_PUSH_UUID, address=addr)
                if not services:
                    raise RuntimeError("OBEX Push service not found on selected device.")
                port = services[0]['port']
                self.status.set(f"Found OBEX Push on port {port}, sending...")
                client = Client(addr, port)
                client.connect()
                with open(file, 'rb') as f:
                    data = f.read()
                client.put(os.path.basename(file), data)
                client.disconnect()
                self.status.set("File sent successfully.")
                messagebox.showinfo("Success", "File has been sent.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send file: {e}")
                self.status.set("Send failed")

        threading.Thread(target=_send, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = GatewayClientGUI(root)
    root.mainloop()