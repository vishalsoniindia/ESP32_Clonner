import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import serial.tools.list_ports
import subprocess
import threading
import os
import sys
import webbrowser  # To open links in the default web browser

class ESP32ClonerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Cloner by Glitchtronics")
        
        # Variables
        self.selected_port = tk.StringVar()
        self.flash_size = tk.StringVar()
        self.mode = tk.StringVar(value="Read")
        self.file_to_write = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status_message = tk.StringVar(value="Ready")
        
        # GUI Components
        self.create_widgets()
    
    def create_widgets(self):
        # COM Port Selection
        ttk.Label(self.root, text="Select COM Port:").grid(row=0, column=0, padx=10, pady=5)
        self.port_menu = ttk.Combobox(self.root, textvariable=self.selected_port, state="readonly")
        self.port_menu.grid(row=0, column=1, padx=10, pady=5)
        self.scan_ports()
        ttk.Button(self.root, text="Rescan", command=self.scan_ports).grid(row=0, column=2, padx=10, pady=5)
        
        # Flash Size Selection
        ttk.Label(self.root, text="Flash Size:").grid(row=1, column=0, padx=10, pady=5)
        self.flash_size_menu = ttk.Combobox(self.root, textvariable=self.flash_size, state="readonly", 
                                            values=["1MB", "2MB", "4MB", "8MB", "16MB"])
        self.flash_size_menu.grid(row=1, column=1, padx=10, pady=5)
        
        # Mode Selection
        ttk.Label(self.root, text="Mode:").grid(row=2, column=0, padx=10, pady=5)
        ttk.Radiobutton(self.root, text="Read File", variable=self.mode, value="Read", command=self.update_mode).grid(row=2, column=1, padx=10, pady=5, sticky="w")
        ttk.Radiobutton(self.root, text="Write File", variable=self.mode, value="Write", command=self.update_mode).grid(row=2, column=2, padx=10, pady=5, sticky="w")
        
        # File to Write
        self.file_frame = ttk.Frame(self.root)
        self.file_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=5)
        ttk.Label(self.file_frame, text="File to Write:").grid(row=0, column=0, padx=5)
        ttk.Entry(self.file_frame, textvariable=self.file_to_write, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(self.file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Output Folder Selection
        self.output_frame = ttk.Frame(self.root)
        self.output_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=5)
        ttk.Label(self.output_frame, text="Output Folder:").grid(row=0, column=0, padx=5)
        ttk.Entry(self.output_frame, textvariable=self.output_folder, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(self.output_frame, text="Browse", command=self.browse_output_folder).grid(row=0, column=2, padx=5)
        
        # Status Message
        self.status_label = ttk.Label(self.root, textvariable=self.status_message, foreground="red")
        self.status_label.grid(row=5, column=0, columnspan=3, padx=10, pady=5)
        
        # Action Button
        ttk.Button(self.root, text="Start", command=self.start_action).grid(row=6, column=1, pady=10)
        
        # Links at the bottom
        ttk.Label(self.root, text="Links:", font=("Arial", 10, "bold")).grid(row=7, column=0, columnspan=3, pady=5)
        coffee_link = ttk.Label(self.root, text="Buy Me a Coffee", foreground="blue", cursor="hand2")
        coffee_link.grid(row=8, column=0, columnspan=1, padx=5, pady=5)
        coffee_link.bind("<Button-1>", lambda e: self.open_link("https://ko-fi.com/glitchtronics"))

        youtube_link = ttk.Label(self.root, text="YouTube Channel", foreground="blue", cursor="hand2")
        youtube_link.grid(row=8, column=2, columnspan=1, padx=5, pady=5)
        youtube_link.bind("<Button-1>", lambda e: self.open_link("https://www.youtube.com/@GlitchTronics"))
        
        # Initialize visibility
        self.update_mode()

    def open_link(self, url):
        webbrowser.open_new(url)
    
    def scan_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_menu['values'] = [port.device for port in ports]
        if ports:
            self.port_menu.current(0)
        else:
            self.update_status("No COM ports detected!")
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select a file to write", 
                                               filetypes=[("All Files", "*.*")])
        if file_path:
            self.file_to_write.set(file_path)
    
    def browse_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select a folder to save the file")
        if folder_path:
            if ' ' in folder_path:  # Check if the folder path contains spaces
                result = messagebox.askretrycancel("Warning", "The folder name contains spaces. This may cause issues. Do you want to select a different folder?")
                if result:
                    self.browse_output_folder()  # Allow the user to select a new folder
                    return
                else:
                    self.update_status("Operation canceled due to folder name issue.")
                    return
            self.output_folder.set(folder_path)
    
    def update_mode(self):
        if self.mode.get() == "Write":
            self.file_frame.grid()
            self.output_frame.grid_remove()
        else:
            self.file_frame.grid_remove()
            self.output_frame.grid()
    
    def update_status(self, message):
        self.status_message.set(message)
    
    def start_action(self):
        self.update_status("Processing...")
        port = self.selected_port.get()
        flash_size = self.flash_size.get()
        mode = self.mode.get()
        
        if not port:
            self.update_status("Error: Please select a COM port.")
            return
        
        if not flash_size:
            self.update_status("Error: Please select a flash size.")
            return
        
        if mode == "Write" and not self.file_to_write.get():
            self.update_status("Error: Please select a file to write.")
            return
        
        if mode == "Read" and not self.output_folder.get():
            self.update_status("Error: Please select an output folder.")
            return
        
        # Run the operation in a separate thread
        thread = threading.Thread(target=self.run_action, args=(port, flash_size, mode))
        thread.start()
    
    def run_action(self, port, flash_size, mode):
        try:
            if mode == "Write":
                self.flash_file(port)
            elif mode == "Read":
                self.read_flash(port, flash_size)
            self.update_status("Operation completed successfully!")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
    
    def flash_file(self, port):
        file_path = self.file_to_write.get()
        command = [
            "esptool.exe",
            "--port", port,
            "write_flash", "0x00000", file_path
        ]
        self.execute_in_background(command)
    
    def read_flash(self, port, flash_size):
        size_bytes = int(flash_size[:-2]) * 1024 * 1024
        output_path = f"{self.output_folder.get()}/firmware.bin"
        command = [
            "esptool.exe",
            "--port", port,
            "read_flash", "0x00000", hex(size_bytes), output_path
        ]
        self.execute_in_background(command)
    
    def execute_in_background(self, command):
        # Get the current directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Open the subprocess and capture its output
        if sys.platform == "win32":
            process = subprocess.Popen(["start", "cmd", "/K", f"cd {script_dir} && " + " ".join(command)], shell=True)
        else:
            process = subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"cd {script_dir} && " + " ".join(command) + "; exec bash"], shell=False)
        
        # Monitor the process and update status when it completes
        process.wait()  # Wait for the process to finish
        if process.returncode != 0:
            self.update_status("Operation failed. Terminal was closed prematurely.")
        else:
            self.update_status("Operation completed successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32ClonerApp(root)
    root.mainloop()
