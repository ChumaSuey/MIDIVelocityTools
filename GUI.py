import os
import sys

# Fix for TclError on Windows
# Dynamically locate Tcl/Tk libraries based on the Python installation
base_path = sys.base_prefix
tcl_path = os.path.join(base_path, 'tcl', 'tcl8.6')
tk_path = os.path.join(base_path, 'tcl', 'tk8.6')

if os.path.exists(tcl_path):
    os.environ["TCL_LIBRARY"] = tcl_path
if os.path.exists(tk_path):
    os.environ["TK_LIBRARY"] = tk_path

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import sv_ttk
import threading
from MIDINormalizer import normalize_midi
from MIDIEqualizer import equalize_midi
from MIDIFixes import fix_midi

class MIDIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MIDI Velocity Tools")
        self.root.geometry("800x600")

        # Variables
        self.input_file_path = tk.StringVar()
        self.output_file_name = tk.StringVar()
        self.normalize_level = tk.IntVar(value=127)
        self.equalize_level = tk.IntVar(value=70)
        
        # New Normalization Options
        self.ignore_muted_var = tk.BooleanVar(value=True)
        self.velocity_threshold = tk.IntVar(value=0)

        # Apply Theme
        sv_ttk.set_theme("dark")

        # UI Layout
        self.create_widgets()

    def create_widgets(self):
        # File Selection
        file_frame = ttk.LabelFrame(self.root, text="File Selection", padding=(20, 10))
        file_frame.pack(fill="x", padx=10, pady=5)
        
        # Configure columns so the entry field expands
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Input MIDI:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Entry(file_frame, textvariable=self.input_file_path).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(file_frame, text="Output Name (Optional):").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        ttk.Entry(file_frame, textvariable=self.output_file_name).grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=5)

        # Actions
        action_frame = ttk.LabelFrame(self.root, text="Actions", padding=(20, 10))
        action_frame.pack(fill="x", padx=10, pady=5)

        # Normalize Section
        ttk.Label(action_frame, text="Normalize Target Velocity (1-127):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(action_frame, textvariable=self.normalize_level, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Button(action_frame, text="Normalize", command=self.run_normalize).grid(row=0, column=2, padx=10, pady=5)

        # Advanced Normalization Options settings
        ttk.Checkbutton(action_frame, text="Ignore Muted Channels (CC7=0)", variable=self.ignore_muted_var).grid(row=1, column=0, sticky="w", columnspan=2, pady=5)
        
        ttk.Label(action_frame, text="Ignore Notes Velocity ≤ :").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(action_frame, textvariable=self.velocity_threshold, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Equalize Section
        ttk.Label(action_frame, text="Equalize Level (%):").grid(row=3, column=0, sticky="w", pady=10)
        ttk.Entry(action_frame, textvariable=self.equalize_level, width=10).grid(row=3, column=1, sticky="w", padx=5, pady=10)
        ttk.Button(action_frame, text="Equalize", command=self.run_equalize).grid(row=3, column=2, padx=10, pady=10)

        # Fix/Sanitize Section - Centered and Spaced
        ttk.Separator(action_frame, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky='ew', pady=10)
        ttk.Button(action_frame, text="Sanitize / Fix Channels", command=self.run_fix).grid(row=5, column=0, columnspan=3, pady=5)

        # Log Area
        log_frame = ttk.LabelFrame(self.root, text="Logs & Stats", padding=(10, 10))
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_area.pack(fill="both", expand=True)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid *.midi")])
        if filename:
            self.input_file_path.set(filename)

    def get_output_path(self, suffix):
        input_path = self.input_file_path.get()
        if not input_path:
            return None
        
        custom_name = self.output_file_name.get().strip()
        directory = os.path.dirname(input_path)
        
        if custom_name:
            if not custom_name.lower().endswith(('.mid', '.midi')):
                custom_name += '.mid'
            return os.path.join(directory, custom_name)
        else:
            base, ext = os.path.splitext(input_path)
            return f"{base}_{suffix}{ext}"

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def run_normalize(self):
        input_path = self.input_file_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return

        target = self.normalize_level.get()
        ignore_muted = self.ignore_muted_var.get()
        threshold = self.velocity_threshold.get()
        output_path = self.get_output_path("normalized")

        self.log_area.delete(1.0, tk.END)
        self.log(f"Starting Normalization on {os.path.basename(input_path)}...")
        self.log(f"Target: {target}, Ignore Muted: {ignore_muted}, Velocity Threshold: {threshold}")
        
        # Run in a separate thread to keep GUI responsive
        threading.Thread(target=self._normalize_thread, args=(input_path, output_path, target, ignore_muted, threshold)).start()

    def _normalize_thread(self, input_path, output_path, target, ignore_muted, threshold):
        try:
            logs = normalize_midi(input_path, output_path, target, ignore_muted, threshold)
            for line in logs:
                self.log(line)
            self.log("Done.")
        except Exception as e:
            self.log(f"Error: {e}")

    def run_equalize(self):
        input_path = self.input_file_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return

        level = self.equalize_level.get()
        output_path = self.get_output_path("equalized")

        self.log_area.delete(1.0, tk.END)
        self.log(f"Starting Equalization on {os.path.basename(input_path)}...")

        # Run in a separate thread to keep GUI responsive
        threading.Thread(target=self._equalize_thread, args=(input_path, output_path, level)).start()

    def _equalize_thread(self, input_path, output_path, level):
        try:
            logs = equalize_midi(input_path, output_path, level)
            for line in logs:
                self.log(line)
            self.log("Done.")
        except Exception as e:
            self.log(f"Error: {e}")

    def run_fix(self):
        input_path = self.input_file_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return

        output_path = self.get_output_path("fixed")

        self.log_area.delete(1.0, tk.END)
        self.log(f"Starting Sanitization on {os.path.basename(input_path)}...")

        # Run in a separate thread to keep GUI responsive
        threading.Thread(target=self._fix_thread, args=(input_path, output_path)).start()

    def _fix_thread(self, input_path, output_path):
        try:
            logs = fix_midi(input_path, output_path)
            for line in logs:
                self.log(line)
            self.log("Done.")
        except Exception as e:
            self.log(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MIDIApp(root)
    root.mainloop()
