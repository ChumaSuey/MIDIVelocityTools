import os
import sys

# Fix for TclError on Windows
# Dynamically locate Tcl/Tk libraries based on the Python installation
if not getattr(sys, 'frozen', False):
    base_path = sys.base_prefix
    tcl_path = os.path.join(base_path, 'tcl', 'tcl8.6').replace("\\", "/")
    tk_path = os.path.join(base_path, 'tcl', 'tk8.6').replace("\\", "/")

    if os.path.exists(tcl_path):
        os.environ["TCL_LIBRARY"] = tcl_path
    if os.path.exists(tk_path):
        os.environ["TK_LIBRARY"] = tk_path

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image

# Backend Imports
from MIDINormalizer import normalize_midi
from MIDIEqualizer import equalize_midi
from MIDIFixes import fix_midi

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class MIDIApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("MIDI Velocity Tools (MIDI-VT)")
        self.geometry(f"{1100}x700")

        # Variables
        self.input_file_path = tk.StringVar()
        self.output_file_name = tk.StringVar()
        
        # Normalization Variables
        self.normalize_level = tk.IntVar(value=127)
        self.ignore_muted_var = tk.BooleanVar(value=True)
        self.velocity_threshold = tk.IntVar(value=0)
        
        # Equalization Variables
        self.equalize_level = tk.IntVar(value=75) # switched to 75% (originally 80%) because of FL Studio velocity line
        # UI Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="MIDI-VT", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_normalize = ctk.CTkButton(self.sidebar_frame, text="Normalize", command=self.show_normalize, corner_radius=8)
        self.sidebar_button_normalize.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_equalize = ctk.CTkButton(self.sidebar_frame, text="Equalize", command=self.show_equalize, corner_radius=8)
        self.sidebar_button_equalize.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_fix = ctk.CTkButton(self.sidebar_frame, text="Sanitize / Fix", command=self.show_fix, corner_radius=8)
        self.sidebar_button_fix.grid(row=3, column=0, padx=20, pady=10)

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))
        self.appearance_mode_optionemenu.set("Dark")

        # Main Tool Area
        self.main_tool_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.main_tool_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.main_tool_frame.grid_columnconfigure(0, weight=1)
        self.main_tool_frame.grid_rowconfigure(2, weight=1) # Log area takes most space

        # File Selection Area (Always visible at top of Main Tool Area)
        self.file_frame = ctk.CTkFrame(self.main_tool_frame, corner_radius=10)
        self.file_frame.grid(row=0, column=0, padx=0, pady=(0, 20), sticky="ew")
        self.file_frame.grid_columnconfigure(1, weight=1)

        self.label_input = ctk.CTkLabel(self.file_frame, text="Input MIDI:", font=ctk.CTkFont(weight="bold"))
        self.label_input.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.entry_input = ctk.CTkEntry(self.file_frame, textvariable=self.input_file_path, placeholder_text="Path to .mid file...")
        self.entry_input.grid(row=0, column=1, padx=10, pady=(15, 5), sticky="ew")
        self.button_browse = ctk.CTkButton(self.file_frame, text="Browse", width=100, command=self.browse_file)
        self.button_browse.grid(row=0, column=2, padx=15, pady=(15, 5))

        self.label_output = ctk.CTkLabel(self.file_frame, text="Output Name:", font=ctk.CTkFont(weight="bold"))
        self.label_output.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="w")
        self.entry_output = ctk.CTkEntry(self.file_frame, textvariable=self.output_file_name, placeholder_text="Optional: custom output name")
        self.entry_output.grid(row=1, column=1, columnspan=2, padx=10, pady=(5, 15), sticky="ew")

        # dynamic_content_frame for specific tool options
        self.dynamic_frame = ctk.CTkFrame(self.main_tool_frame, corner_radius=10)
        self.dynamic_frame.grid(row=1, column=0, padx=0, pady=(0, 20), sticky="nsew")
        self.dynamic_frame.grid_columnconfigure(0, weight=1)

        # Log Area (Bottom of Main Tool Area)
        self.log_frame = ctk.CTkFrame(self.main_tool_frame, corner_radius=10)
        self.log_frame.grid(row=2, column=0, padx=0, pady=(0, 20), sticky="nsew")
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)

        self.log_header = ctk.CTkLabel(self.log_frame, text="Logs & Stats", font=ctk.CTkFont(size=14, weight="bold"))
        self.log_header.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")
        
        self.log_area = ctk.CTkTextbox(self.log_frame, height=200, font=("Consolas", 12))
        self.log_area.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

        # Progress Bar (Hidden by default)
        self.progress_bar = ctk.CTkProgressBar(self.main_tool_frame, mode="indeterminate")
        self.progress_bar.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.stop()

        # Initialize with Normalize view
        self.show_normalize()

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid *.midi")])
        if filename:
            self.input_file_path.set(filename)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def clear_dynamic_frame(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

    def show_normalize(self):
        self.clear_dynamic_frame()
        self.sidebar_button_normalize.configure(fg_color=("gray75", "gray25"))
        self.sidebar_button_equalize.configure(fg_color="transparent")
        self.sidebar_button_fix.configure(fg_color="transparent")

        title = ctk.CTkLabel(self.dynamic_frame, text="MIDI Normalization", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Row 1: Target Velocity
        target_label = ctk.CTkLabel(self.dynamic_frame, text="Target Velocity (1-127):")
        target_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        target_entry = ctk.CTkEntry(self.dynamic_frame, textvariable=self.normalize_level, width=60)
        target_entry.grid(row=1, column=1, padx=20, pady=5, sticky="w")

        # Row 2: Ignore Muted
        muted_check = ctk.CTkCheckBox(self.dynamic_frame, text="Ignore Muted Channels (CC7=0)", variable=self.ignore_muted_var)
        muted_check.grid(row=2, column=0, columnspan=2, padx=20, pady=5, sticky="w")

        # Row 3: Threshold
        threshold_label = ctk.CTkLabel(self.dynamic_frame, text="Ignore Notes Velocity ≤ :")
        threshold_label.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        threshold_entry = ctk.CTkEntry(self.dynamic_frame, textvariable=self.velocity_threshold, width=60)
        threshold_entry.grid(row=3, column=1, padx=20, pady=5, sticky="w")

        # Action Button
        run_btn = ctk.CTkButton(self.dynamic_frame, text="RUN NORMALIZATION", fg_color="#2ecc71", hover_color="#27ae60", 
                                 font=ctk.CTkFont(weight="bold"), command=self.run_normalize)
        run_btn.grid(row=4, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="ew")

    def show_equalize(self):
        self.clear_dynamic_frame()
        self.sidebar_button_normalize.configure(fg_color="transparent")
        self.sidebar_button_equalize.configure(fg_color=("gray75", "gray25"))
        self.sidebar_button_fix.configure(fg_color="transparent")

        title = ctk.CTkLabel(self.dynamic_frame, text="MIDI Equalization", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Row 1: Level
        level_label = ctk.CTkLabel(self.dynamic_frame, text="Equalize Level (%):")
        level_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        level_entry = ctk.CTkEntry(self.dynamic_frame, textvariable=self.equalize_level, width=60)
        level_entry.grid(row=1, column=1, padx=20, pady=5, sticky="w")

        # Action Button
        run_btn = ctk.CTkButton(self.dynamic_frame, text="RUN EQUALIZATION", fg_color="#3498db", hover_color="#2980b9", 
                                 font=ctk.CTkFont(weight="bold"), command=self.run_equalize)
        run_btn.grid(row=2, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="ew")

    def show_fix(self):
        self.clear_dynamic_frame()
        self.sidebar_button_normalize.configure(fg_color="transparent")
        self.sidebar_button_equalize.configure(fg_color="transparent")
        self.sidebar_button_fix.configure(fg_color=("gray75", "gray25"))

        title = ctk.CTkLabel(self.dynamic_frame, text="Sanitize & Fix Channels", font=ctk.CTkFont(size=18, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        info_label = ctk.CTkLabel(self.dynamic_frame, text="This process attempts to fix channel conflicts and sanitize MIDI data.", 
                                   wraplength=400, justify="left")
        info_label.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        # Action Button
        run_btn = ctk.CTkButton(self.dynamic_frame, text="RUN SANITIZATION", fg_color="#e67e22", hover_color="#d35400", 
                                 font=ctk.CTkFont(weight="bold"), command=self.run_fix)
        run_btn.grid(row=2, column=0, padx=20, pady=(20, 20), sticky="ew")

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

    def start_process(self):
        self.log_area.delete("1.0", tk.END)
        self.progress_bar.start()

    def end_process(self):
        self.progress_bar.stop()
        self.progress_bar.set(0)

    def run_normalize(self):
        input_path = self.input_file_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return

        target = self.normalize_level.get()
        ignore_muted = self.ignore_muted_var.get()
        threshold = self.velocity_threshold.get()
        output_path = self.get_output_path("normalized")

        self.start_process()
        self.log(f"Starting Normalization on {os.path.basename(input_path)}...")
        self.log(f"Target: {target}, Ignore Muted: {ignore_muted}, Velocity Threshold: {threshold}")
        
        threading.Thread(target=self._normalize_thread, args=(input_path, output_path, target, ignore_muted, threshold), daemon=True).start()

    def _normalize_thread(self, input_path, output_path, target, ignore_muted, threshold):
        try:
            logs = normalize_midi(input_path, output_path, target, ignore_muted, threshold)
            for line in logs:
                self.log(line)
            self.log("Done.")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.after(0, self.end_process)

    def run_equalize(self):
        input_path = self.input_file_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return

        level = self.equalize_level.get()
        output_path = self.get_output_path("equalized")

        self.start_process()
        self.log(f"Starting Equalization on {os.path.basename(input_path)}...")

        threading.Thread(target=self._equalize_thread, args=(input_path, output_path, level), daemon=True).start()

    def _equalize_thread(self, input_path, output_path, level):
        try:
            logs = equalize_midi(input_path, output_path, level)
            for line in logs:
                self.log(line)
            self.log("Done.")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.after(0, self.end_process)

    def run_fix(self):
        input_path = self.input_file_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return

        output_path = self.get_output_path("fixed")

        self.start_process()
        self.log(f"Starting Sanitization on {os.path.basename(input_path)}...")

        threading.Thread(target=self._fix_thread, args=(input_path, output_path), daemon=True).start()

    def _fix_thread(self, input_path, output_path):
        try:
            logs = fix_midi(input_path, output_path)
            for line in logs:
                self.log(line)
            self.log("Done.")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.after(0, self.end_process)

if __name__ == "__main__":
    app = MIDIApp()
    app.mainloop()
