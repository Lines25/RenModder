import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import subprocess
import os
import sys
import io

class StreamRedirect(io.StringIO):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

class PatcherThread(threading.Thread):
    def __init__(self, folder_path, mode, action, queue):
        super().__init__()
        self.folder_path = folder_path
        self.mode = mode
        self.action = action
        self.queue = queue

    def run(self):
        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            main_script = os.path.join(script_dir, "main.py")
            
            # Run the CLI script
            process = subprocess.Popen(
                [sys.executable, main_script, self.folder_path, self.mode, self.action],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output:
                    self.queue.put(("progress", output))
                
                error = process.stderr.readline()
                if error:
                    self.queue.put(("progress", f"Error: {error}"))
                
                # Check if process has finished
                if process.poll() is not None:
                    break
            
            # Get any remaining output
            remaining_output, remaining_error = process.communicate()
            if remaining_output:
                self.queue.put(("progress", remaining_output))
            if remaining_error:
                self.queue.put(("progress", f"Error: {remaining_error}"))
            
            if process.returncode == 0:
                self.queue.put(("progress", "Operation completed successfully!\n"))
            else:
                self.queue.put(("progress", "Operation failed!\n"))
            
            self.queue.put(("finished", None))
            
        except Exception as e:
            self.queue.put(("progress", f"Error: {str(e)}\n"))
            self.queue.put(("finished", None))

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("RenModder GUI")
        self.root.minsize(600, 400)
        
        self.selected_folder = None
        self.worker = None
        self.queue = queue.Queue()
        
        self.create_widgets()
        self.setup_layout()
        
        # Start queue checking
        self.check_queue()

    def create_widgets(self):
        # Folder selection frame
        self.folder_frame = ttk.Frame(self.root)
        self.folder_label = ttk.Label(self.folder_frame, text="No folder selected")
        self.select_button = ttk.Button(
            self.folder_frame, 
            text="Select Folder",
            command=self.select_folder
        )
        
        # Mode selection frame
        self.mode_frame = ttk.Frame(self.root)
        self.mode_label = ttk.Label(self.mode_frame, text="Mode:")
        self.mode_var = tk.StringVar(value="mod")
        self.mode_mod = ttk.Radiobutton(
            self.mode_frame, 
            text="Mod Support", 
            variable=self.mode_var, 
            value="mod"
        )
        self.mode_dev = ttk.Radiobutton(
            self.mode_frame, 
            text="Dev Mode", 
            variable=self.mode_var, 
            value="dev"
        )
        
        # Action buttons frame
        self.button_frame = ttk.Frame(self.root)
        self.patch_button = ttk.Button(
            self.button_frame,
            text="Patch Folder",
            command=lambda: self.process_folder("patch"),
            state="disabled"
        )
        self.unpatch_button = ttk.Button(
            self.button_frame,
            text="Unpatch Folder",
            command=lambda: self.process_folder("unpatch"),
            state="disabled"
        )
        
        # Log output
        self.log_output = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            height=15
        )
        self.log_output.configure(state='disabled')
        
        # Redirect stdout
        self.stdout_redirect = StreamRedirect(self.log_output)
        sys.stdout = self.stdout_redirect

    def setup_layout(self):
        # Folder selection layout
        self.folder_frame.pack(fill=tk.X, padx=5, pady=5)
        self.folder_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.select_button.pack(side=tk.RIGHT, padx=5)
        
        # Mode selection layout
        self.mode_frame.pack(fill=tk.X, padx=5, pady=5)
        self.mode_label.pack(side=tk.LEFT, padx=5)
        self.mode_mod.pack(side=tk.LEFT, padx=5)
        self.mode_dev.pack(side=tk.LEFT, padx=5)
        
        # Button layout
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)
        self.patch_button.pack(side=tk.LEFT, expand=True, padx=5)
        self.unpatch_button.pack(side=tk.LEFT, expand=True, padx=5)
        
        # Log output layout
        self.log_output.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

    def select_folder(self):
        folder_path = filedialog.askdirectory(
            title="Select Folder to Patch"
        )
        
        if folder_path:
            self.selected_folder = folder_path
            self.folder_label.config(text=os.path.basename(folder_path))
            self.patch_button.config(state="normal")
            self.unpatch_button.config(state="normal")
            self.log_write(f"Selected folder: {folder_path}\n")

    def process_folder(self, action):
        if not self.selected_folder:
            messagebox.showwarning("Error", "Please select a folder first")
            return
            
        self.patch_button.config(state="disabled")
        self.unpatch_button.config(state="disabled")
        
        mode = self.mode_var.get()
        self.worker = PatcherThread(self.selected_folder, mode, action, self.queue)
        self.worker.start()

    def check_queue(self):
        try:
            while True:
                msg_type, msg = self.queue.get_nowait()
                if msg_type == "progress":
                    self.log_write(msg)
                elif msg_type == "finished":
                    self.on_process_complete()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_queue)

    def log_write(self, message):
        self.log_output.configure(state='normal')
        self.log_output.insert(tk.END, message)
        self.log_output.see(tk.END)
        self.log_output.configure(state='disabled')

    def on_process_complete(self):
        self.patch_button.config(state="normal")
        self.unpatch_button.config(state="normal")

    def on_closing(self):
        # Restore stdout
        sys.stdout = sys.__stdout__
        self.root.destroy()

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()