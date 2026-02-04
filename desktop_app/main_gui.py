import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import threading
import sys
import webbrowser
import glob
from PIL import Image, ImageTk
from processor import process_video_crossfade

# Configuration
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        self.title("Oopl - VJ Loop Crossfader")
        self.title("Oopl - VJ Loop Crossfader")
        self.geometry("550x720")
        self.minsize(500, 550)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Log area expands

        self.queue_items = [] # List of dicts: {'path': str, 'var': BooleanVar, 'widget': CheckBox}
        self.is_processing = False
        self.focused_slider = None
        
        # Global Key Bindings
        self.bind("<Left>", lambda e: self.on_global_arrow_key(-1))
        self.bind("<Right>", lambda e: self.on_global_arrow_key(1))

        # --- Icon & Branding ---
        # Determine path to assets
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
            # Fallback if mapped differently
            if not os.path.exists(asset_dir):
                 asset_dir = os.path.join(sys._MEIPASS, "assets")
        else:
            asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

        self.logo_img = None
        
        # 1. Set Window Icon (Titlebar & Taskbar) - Prefer .ico on Windows
        ico_path = os.path.join(asset_dir, "icon.ico")
        png_path = os.path.join(asset_dir, "icon.png")
        
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception as e:
                print(f"Failed to set iconbitmap: {e}")
        elif os.path.exists(png_path):
            try:
                # Fallback for non-Windows or if ico missing
                icon_img = ImageTk.PhotoImage(Image.open(png_path))
                self.wm_iconphoto(True, icon_img)
            except Exception as e:
                print(f"Failed to set iconphoto: {e}")

        # 2. Load UI Logo (Toolbar)
        if os.path.exists(png_path):
            try:
                pil_img = Image.open(png_path)
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(32, 32))
            except Exception as e:
                print(f"Failed to load logo image: {e}")

        # Title Row
        self.frame_title = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_title.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        if self.logo_img:
            self.lbl_logo = ctk.CTkLabel(self.frame_title, text="", image=self.logo_img)
            self.lbl_logo.pack(side="left", padx=(0, 10))
            
        self.label_title = ctk.CTkLabel(self.frame_title, text="Oopl", font=("Arial", 18, "bold"))
        self.label_title.pack(side="left")

        # Attribution (Top Right)
        self.frame_attribution = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_attribution.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="e")
        
        self.lbl_attr_text = ctk.CTkLabel(self.frame_attribution, text="by ", font=("Arial", 12))
        self.lbl_attr_text.grid(row=0, column=0)
        
        self.lbl_attr_link = ctk.CTkLabel(self.frame_attribution, text="busy squirrel", font=("Arial", 12), text_color="#3399FF", cursor="hand2")
        self.lbl_attr_link.grid(row=0, column=1)
        self.lbl_attr_link.bind("<Button-1>", lambda e: webbrowser.open_new("https://sqrl.biz"))

        # Settings Frame (Moved to Row 1)
        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.frame_settings.grid_columnconfigure(1, weight=1)

        # Row 0: Format Selection
        self.label_format = ctk.CTkLabel(self.frame_settings, text="Format:")
        self.label_format.grid(row=0, column=0, padx=10, pady=4)

        self.seg_format = ctk.CTkSegmentedButton(self.frame_settings, values=["MP4", "HAP", "ProRes", "MJPEG"], command=self.update_quality_config)
        self.seg_format.set("MP4")
        self.seg_format.grid(row=0, column=1, padx=10, pady=4, sticky="ew")

        # Row 1: Quality Slider
        self.label_quality = ctk.CTkLabel(self.frame_settings, text="Quality:")
        self.label_quality.grid(row=1, column=0, padx=10, pady=4)
        
        # Initial config for MP4 (0-17 mapping to CRF 35-18)
        self.slider_quality = ctk.CTkSlider(self.frame_settings, from_=0, to=17, number_of_steps=17, command=self.update_quality_label)
        self.slider_quality.set(12) # Default around CRF 23 (35 - 12 = 23)
        self.slider_quality.grid(row=1, column=1, padx=10, pady=4, sticky="ew")
        
        self.label_quality_val = ctk.CTkLabel(self.frame_settings, text="CRF 23", width=80)
        self.label_quality_val.grid(row=1, column=2, padx=5, pady=4)

        # Row 3: Crossfade Control (Moved down)
        self.check_crossfade = ctk.CTkCheckBox(self.frame_settings, text="Crossfade", command=self.toggle_crossfade)
        self.check_crossfade.select() # Default ON
        self.check_crossfade.grid(row=3, column=0, padx=10, pady=4, sticky="w")
        
        self.slider_duration = ctk.CTkSlider(self.frame_settings, from_=0, to=59.5, number_of_steps=595, command=self.update_duration_label)
        self.slider_duration.set(1.0)
        self.slider_duration.grid(row=3, column=1, padx=10, pady=4, sticky="ew")
        
        self.label_crossfade_val = ctk.CTkLabel(self.frame_settings, text="1.0s", width=60)
        self.label_crossfade_val.grid(row=3, column=2, padx=5, pady=4)
        # Editable Crossfade Logic
        self.custom_crossfade_val = None
        self.label_crossfade_val.bind("<Button-1>", self.edit_crossfade_value)
        
        self.entry_crossfade_val = ctk.CTkEntry(self.frame_settings, width=60)
        self.entry_crossfade_val.bind("<Return>", self.submit_crossfade_value)
        self.entry_crossfade_val.bind("<FocusOut>", self.submit_crossfade_value)

        # Row 2: Set Start (Moved up)
        self.check_start = ctk.CTkCheckBox(self.frame_settings, text="Set Start", command=self.toggle_start)
        self.check_start.grid(row=2, column=0, padx=10, pady=4, sticky="w")
        
        self.slider_start = ctk.CTkSlider(self.frame_settings, from_=0, to=60.0, number_of_steps=600, command=self.update_start_label, state="disabled")
        self.slider_start.set(0.0)
        self.slider_start.grid(row=2, column=1, padx=10, pady=4, sticky="ew")
        
        self.label_start_val = ctk.CTkLabel(self.frame_settings, text="0.0s", width=60)
        self.label_start_val.grid(row=2, column=2, padx=5, pady=4)
        self.label_start_val.configure(text_color="gray")
        # Editable Start Value Logic
        self.custom_start_val = None
        self.label_start_val.bind("<Button-1>", self.edit_start_value)
        
        self.entry_start_val = ctk.CTkEntry(self.frame_settings, width=60)
        self.entry_start_val.bind("<Return>", self.submit_start_value)
        self.entry_start_val.bind("<FocusOut>", self.submit_start_value)

        # Row 4: Set Length
        self.check_length = ctk.CTkCheckBox(self.frame_settings, text="Set Length", command=self.toggle_length)
        self.check_length.grid(row=4, column=0, padx=10, pady=4, sticky="w")
        
        self.slider_length = ctk.CTkSlider(self.frame_settings, from_=0, to=60.0, number_of_steps=600, command=self.update_length_label, state="disabled")
        self.slider_length.set(10.0)
        self.slider_length.grid(row=4, column=1, padx=10, pady=4, sticky="ew")
        
        self.label_length_val = ctk.CTkLabel(self.frame_settings, text="10.0s", width=60)
        self.label_length_val.grid(row=4, column=2, padx=5, pady=4)
        self.label_length_val.configure(text_color="gray")
        # Editable Length Value Logic
        self.custom_length_val = None
        self.label_length_val.bind("<Button-1>", self.edit_length_value)
        
        self.entry_length_val = ctk.CTkEntry(self.frame_settings, width=60)
        self.entry_length_val.bind("<Return>", self.submit_length_value)
        self.entry_length_val.bind("<FocusOut>", self.submit_length_value)

        # Row 5: Scale Control
        self.check_scale = ctk.CTkCheckBox(self.frame_settings, text="Scale", command=self.toggle_scale)
        self.check_scale.grid(row=5, column=0, padx=10, pady=4, sticky="w")
        
        self.frame_scale = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.frame_scale.grid(row=5, column=1, columnspan=2, padx=10, pady=4, sticky="w")
        
        self.btn_4k = ctk.CTkButton(self.frame_scale, text="4K", width=40, command=lambda: self.set_scale(3840, 2160))
        self.btn_4k.pack(side="left", padx=(0, 5))
        
        self.btn_1080 = ctk.CTkButton(self.frame_scale, text="1080", width=40, command=lambda: self.set_scale(1920, 1080))
        self.btn_1080.pack(side="left", padx=(0, 5))
        
        self.btn_720 = ctk.CTkButton(self.frame_scale, text="720", width=40, command=lambda: self.set_scale(1280, 720))
        self.btn_720.pack(side="left", padx=(0, 5))
        
        # Spacer for key alignment
        self.label_spacer_scale = ctk.CTkLabel(self.frame_scale, text="", width=40)
        self.label_spacer_scale.pack(side="left")
        
        self.entry_width = ctk.CTkEntry(self.frame_scale, width=50)
        self.entry_width.pack(side="left", padx=(5, 0))
        self.entry_width.bind("<FocusIn>", lambda e: self.entry_width.select_range(0, "end"))
        
        self.label_x = ctk.CTkLabel(self.frame_scale, text="x", width=10)
        self.label_x.pack(side="left")
        
        self.entry_height = ctk.CTkEntry(self.frame_scale, width=50)
        self.entry_height.pack(side="left")
        self.entry_height.bind("<FocusIn>", lambda e: self.entry_height.select_range(0, "end"))
        
        # Initialize disabled
        self.toggle_scale()

        # Row 6: Filename configuration
        self.label_filename = ctk.CTkLabel(self.frame_settings, text="Filename:")
        self.label_filename.grid(row=6, column=0, padx=10, pady=4)
        
        # Frame for controls
        self.frame_filename = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.frame_filename.grid(row=6, column=1, columnspan=2, padx=10, pady=4, sticky="w")
        
        self.var_name_mode = ctk.StringVar(value="Append")
        self.radio_prepend = ctk.CTkRadioButton(self.frame_filename, text="Prepend", variable=self.var_name_mode, value="Prepend")
        self.radio_prepend.pack(side="left", padx=(0, 10))
        
        self.radio_append = ctk.CTkRadioButton(self.frame_filename, text="Append", variable=self.var_name_mode, value="Append")
        self.radio_append.pack(side="left", padx=(0, 10))
        
        self.entry_name_text = ctk.CTkEntry(self.frame_filename, width=100)
        self.entry_name_text.pack(side="left")
        self.entry_name_text.bind("<FocusIn>", lambda e: self.entry_name_text.select_range(0, "end"))
        self.entry_name_text.insert(0, "_oopl")

        # Row 7: Output Directory
        self.label_output = ctk.CTkLabel(self.frame_settings, text="Output To:")
        self.label_output.grid(row=7, column=0, padx=10, pady=4)
        
        self.frame_output = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.frame_output.grid(row=7, column=1, columnspan=2, padx=10, pady=4, sticky="ew")
        
        self.custom_output_dir = None # Default: None (Same as Input)
        
        self.btn_output_dir = ctk.CTkButton(self.frame_output, text="Choose...", width=80, command=self.select_output_dir)
        self.btn_output_dir.pack(side="left", padx=(0, 5))
        
        self.btn_reset_output = ctk.CTkButton(self.frame_output, text="Reset", width=60, fg_color="gray", command=self.reset_output_dir)
        self.btn_reset_output.pack(side="left", padx=(0, 5))
        
        self.label_output_path = ctk.CTkLabel(self.frame_output, text="Same as Input", text_color="gray", anchor="w")
        self.label_output_path.pack(side="left", fill="x", expand=True)

        # Keyboard bindings
        self.slider_quality.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_quality))
        self.slider_duration.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_duration))
        self.slider_start.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_start))
        self.slider_length.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_length))
        self.slider_length.bind("<ButtonRelease-1>", self.on_length_release)

        # Queue Management Frame (Row 2)
        self.frame_queue = ctk.CTkFrame(self)
        self.frame_queue.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.frame_queue.grid_columnconfigure(3, weight=1) # Spacer? No, just let them sit.
        # Let's use columns for buttons.
        
        # Row 0: Header Controls
        self.label_queue = ctk.CTkLabel(self.frame_queue, text="Queue:", font=ctk.CTkFont(weight="bold"))
        self.label_queue.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.btn_files = ctk.CTkButton(self.frame_queue, text="+ Files", command=self.select_files, width=80)
        self.btn_files.grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_folder = ctk.CTkButton(self.frame_queue, text="+ Folder", command=self.select_folder, width=80)
        self.btn_folder.grid(row=0, column=2, padx=5, pady=5)
        
        # Row 0: Status Label (Integrated) - Moves to Column 3, expands
        self.label_status = ctk.CTkLabel(self.frame_queue, text="No files selected", text_color="gray", font=("Arial", 12))
        self.label_status.grid(row=0, column=3, padx=10, pady=5, sticky="ew")
        
        self.btn_clear = ctk.CTkButton(self.frame_queue, text="Clear", command=self.clear_queue, width=60, fg_color="firebrick")
        self.btn_clear.grid(row=0, column=4, padx=10, pady=5, sticky="e")
        
        self.frame_queue.grid_columnconfigure(3, weight=1) # Status label expands
        
        # Row 1: Queue List (Scrollable)
        # Using a wrapper frame to enforce height limit
        self.frame_queue_container = ctk.CTkFrame(self.frame_queue, height=160, fg_color="transparent")
        self.frame_queue_container.grid(row=1, column=0, columnspan=5, padx=10, pady=5, sticky="ew")
        self.frame_queue_container.grid_propagate(False) # FORCE height
        self.frame_queue_container.grid_columnconfigure(0, weight=1)
        self.frame_queue_container.grid_rowconfigure(0, weight=1)

        self.scroll_queue = ctk.CTkScrollableFrame(self.frame_queue_container, height=150) # Height is relative now
        self.scroll_queue.grid(row=0, column=0, sticky="nsew")
        self.scroll_queue.grid_columnconfigure(0, weight=1)

        # Process Button (Row 3)
        self.btn_process = ctk.CTkButton(self, text="Start Batch", command=self.start_processing, state="disabled")
        self.btn_process.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Log Area (Row 4)
        self.textbox_log = ctk.CTkTextbox(self, width=600, height=150)
        self.textbox_log.grid(row=4, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.log("Ready. Select files or a folder to begin.")
        
        # Configure Drop Target
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_files)
        
        # Click-away handling (Clear focus on background click)
        self.bind("<Button-1>", self.on_click_background)
        self.frame_settings.bind("<Button-1>", self.on_click_background)
        self.frame_queue.bind("<Button-1>", self.on_click_background)

    def on_click_background(self, event):
        # Only clear focus if we didn't click on an input widget
        try:
            widget_class = event.widget.winfo_class()
            if widget_class in ["Entry", "Text", "TEntry"]:
                return
        except:
            pass
        self.focus()

    def select_files(self):
        file_paths = ctk.filedialog.askopenfilenames(filetypes=[("Video Files", "*.mov *.mp4 *.avi *.mkv")])
        if file_paths:
            self.add_files_to_queue(list(file_paths))

    def select_folder(self):
        folder_path = ctk.filedialog.askdirectory()
        if folder_path:
            new_files = []
            extensions = ['*.mov', '*.mp4', '*.avi', '*.mkv']
            # Recursive search
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext.replace('*', '')) for ext in extensions):
                        new_files.append(os.path.join(root, file))
            self.add_files_to_queue(new_files)

    def select_output_dir(self):
        dir_path = ctk.filedialog.askdirectory()
        if dir_path:
            self.custom_output_dir = dir_path
            # Truncate for display if needed
            display_path = dir_path
            if len(display_path) > 30:
                display_path = "..." + display_path[-27:]
            
            self.label_output_path.configure(text=display_path, text_color=("black", "white"))
            
    def reset_output_dir(self):
        self.custom_output_dir = None
        self.label_output_path.configure(text="Same as Input", text_color="gray")

    def drop_files(self, event):
        files_to_process = self.parse_dropped_files(event.data)
        if files_to_process:
            self.add_files_to_queue(files_to_process)
        else:
            self.log("Dropped: No valid video files found.")

    def parse_dropped_files(self, data):
        # TkinterDnD returns a string with space-separated paths.
        # Paths with spaces are enclosed in curly braces {}.
        # We need to parse this properly.
        paths = []
        if not data:
            return paths
            
        # Helper to process a potential path
        def process_path(path):
            path = path.strip('{}')
            if os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in ['.mov', '.mp4', '.avi', '.mkv']:
                    paths.append(path)
            elif os.path.isdir(path):
                extensions = ['*.mov', '*.mp4', '*.avi', '*.mkv']
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if any(file.lower().endswith(ext.replace('*', '')) for ext in extensions):
                            paths.append(os.path.join(root, file))

        # Basic parsing logic (handles most cases)
        # We can split by space but respect braces
        import re
        # Regex to match content inside braces OR non-space sequences
        pattern = re.compile(r'\{.*?\}|\S+')
        matches = pattern.findall(data)
        
        for match in matches:
            process_path(match)
            
        return paths

    def add_files_to_queue(self, paths):
        added_count = 0
        existing_paths = {item['path'] for item in self.queue_items}
        
        for path in paths:
            if path not in existing_paths:
                # Create Checkbox
                filename = os.path.basename(path)
                # Truncate if too long logic? Checkbox handles it mostly, but let's be safe visually if needed.
                # Only if extremely long.
                
                chk_var = ctk.BooleanVar(value=True)
                chk = ctk.CTkCheckBox(self.scroll_queue, text=filename, variable=chk_var)
                chk.grid(row=len(self.queue_items), column=0, padx=5, pady=2, sticky="w")
                
                self.queue_items.append({
                    'path': path,
                    'var': chk_var,
                    'widget': chk
                })
                existing_paths.add(path)
                added_count += 1
        
        if added_count > 0:
            self.log(f"Added {added_count} file(s) to queue.")
        else:
            self.log("No new unique files added.")
            
        self.update_status()

    def clear_queue(self):
        for item in self.queue_items:
            item['widget'].destroy()
        self.queue_items.clear()
        self.log("Queue cleared.")
        self.update_status()

    def update_status(self):
        count = len(self.queue_items)
        if count > 0:
            self.label_status.configure(text=f"{count} files queued", text_color=("black", "white"))
            self.btn_process.configure(state="normal")
        else:
            self.label_status.configure(text="No files queued", text_color="red")
            self.btn_process.configure(state="disabled")

    def update_duration_label(self, value):
        self.custom_crossfade_val = None
        self.label_crossfade_val.configure(text=f"{value:.1f}s")
        if self.check_length.get():
             self.check_constraints()

    def get_effective_crossfade(self):
        if self.custom_crossfade_val is not None:
            return self.custom_crossfade_val
        return self.slider_duration.get()

    def get_effective_length(self):
        if self.custom_length_val is not None:
            return self.custom_length_val
        return self.slider_length.get()

    def close_active_edits(self):
        # Force submit/close on any open entries to prevent multiple boxes
        if self.entry_start_val.winfo_viewable():
            self.submit_start_value(None)
        if self.entry_crossfade_val.winfo_viewable():
            self.submit_crossfade_value(None)
        if self.entry_length_val.winfo_viewable():
            self.submit_length_value(None)

    def _focus_and_select(self, entry):
        entry.focus_set()
        entry.select_range(0, "end")

    def edit_crossfade_value(self, event):
        self.close_active_edits()
        if self.check_crossfade.get():
            self.label_crossfade_val.grid_remove()
            self.entry_crossfade_val.grid(row=3, column=2, padx=5, pady=4)
            
            current_text = self.label_crossfade_val.cget("text").replace("s", "")
            self.entry_crossfade_val.delete(0, "end")
            self.entry_crossfade_val.insert(0, current_text)
            
            # Defer focus prevents race condition with closing other boxes
            self.after(50, lambda: self._focus_and_select(self.entry_crossfade_val))

    def submit_crossfade_value(self, event):
        text = self.entry_crossfade_val.get()
        try:
            val = float(text)
            if val < 0: val = 0.0
            
            self.custom_crossfade_val = val
            self.label_crossfade_val.configure(text=f"{val:.1f}s")
            
            # Update Slider
            if val <= 59.5:
                self.slider_duration.set(val)
            else:
                self.slider_duration.set(59.5)
            
            # Re-check constraints (updates Length if needed)
            if self.check_length.get():
                self.check_constraints()
                
        except ValueError:
            pass
        
        self.entry_crossfade_val.grid_remove()
        self.label_crossfade_val.grid(row=3, column=2, padx=5, pady=4)

    def update_start_label(self, value):
        self.label_start_val.configure(text=f"{value:.1f}s")

    def update_quality_config(self, value=None):
        fmt = self.seg_format.get()
        if fmt == "MP4":
            # CRF 18 (Best) to 35 (Worst)
            # Slider 0 (Worst) to 17 (Best) -> CRF = 35 - val
            self.slider_quality.configure(from_=0, to=17, number_of_steps=17)
            self.slider_quality.set(12) # Default CRF 23
            self.update_quality_label(self.slider_quality.get())
            # Default Audio: Keep (AAC)
            # self.var_audio_mode.set("keep")
            
        elif fmt == "MJPEG":
            # Qscale 2 (Best) to 31 (Worst)
            # Slider 0 (Worst) to 29 (Best) -> Q = 31 - val
            self.slider_quality.configure(from_=0, to=29, number_of_steps=29)
            self.slider_quality.set(26) # Default Q 5
            self.update_quality_label(self.slider_quality.get())

        elif fmt == "ProRes":
            # Profile ID 0 (Proxy) to 3 (HQ)
            self.slider_quality.configure(from_=0, to=3, number_of_steps=3)
            self.slider_quality.set(2) # Default Standard
            self.update_quality_label(self.slider_quality.get())
            
        elif fmt == "HAP":
            # 0 (Hap) or 1 (Hap Q)
            self.slider_quality.configure(from_=0, to=1, number_of_steps=1)
            self.slider_quality.set(0) # Default Hap
            self.update_quality_label(self.slider_quality.get())

    def update_quality_label(self, value):
        fmt = self.seg_format.get()
        val = int(value)
        
        if fmt == "MP4":
            crf = 35 - val
            self.label_quality_val.configure(text=f"CRF {crf}")
        elif fmt == "MJPEG":
            q = 31 - val
            self.label_quality_val.configure(text=f"Q {q}")
        elif fmt == "ProRes":
            labels = ["Proxy", "LT", "Standard", "HQ"]
            # safety clamp
            idx = max(0, min(3, val))
            self.label_quality_val.configure(text=labels[idx])
        elif fmt == "HAP":
            labels = ["Hap", "Hap Q"]
            idx = max(0, min(1, val))
            self.label_quality_val.configure(text=labels[idx])

    def toggle_crossfade(self):
        if self.check_crossfade.get():
            self.slider_duration.configure(state="normal")
            self.label_crossfade_val.configure(text_color=("black", "white"))
            # Re-check constraints if length is on
            if self.check_length.get():
                self.check_constraints()
        else:
            self.slider_duration.configure(state="disabled")
            self.label_crossfade_val.configure(text_color="gray")

    # Helpers removed (Direct mapping now)

# New Focus Logic
    def set_focused_slider(self, slider):
        self.focused_slider = slider
        
    def on_global_arrow_key(self, direction):
        if self.focused_slider:
             if self.focused_slider._state != "disabled":
                self.nudge_slider(self.focused_slider, direction)

    def nudge_slider(self, slider, direction):
        if slider._state == "disabled":
            return

        current_val = slider.get()
        # For CTkSlider, we can approximate the step. 
        # But since we have defined 'number_of_steps', getting the step size is effectively 1 step unit.
        # However, CTkSlider.get() returns the float value.
        if slider == self.slider_duration:
             # Range 0.1 - 10.0, steps 99 => step 0.1
             step = 0.1
        elif slider == self.slider_start:
             step = 0.1
        elif slider == self.slider_length:
             step = 0.1
        elif slider == self.slider_quality:
             step = 1.0
             
        new_val = current_val + (step * direction)
        
        # Clamp
        if new_val < slider._from_: new_val = slider._from_
        if new_val > slider._to: new_val = slider._to
        
        slider.set(new_val)
        
        # Manually trigger callback
        if slider == self.slider_duration:
            self.update_duration_label(new_val)
        elif slider == self.slider_start:
            self.update_start_label(new_val)
        elif slider == self.slider_length:
            self.update_length_label(new_val)
        elif slider == self.slider_quality:
            self.update_quality_label(new_val)

    def check_constraints(self):
        # Ignore if Crossfade is disabled
        if not self.check_crossfade.get():
            return

        # Enforce Length >= Crossfade + 0.5
        xfade = self.get_effective_crossfade()
        # Use effective length to see current state (respecting custom values)
        current_len = self.get_effective_length()
        
        min_len = xfade + 0.5
        
        if current_len < min_len:
            # We need to increase length.
            new_len = min_len
               
            # If new requirement exceeds slider max, use custom val
            if new_len > 60.0:
                 self.custom_length_val = new_len
                 self.slider_length.set(60.0)
            else:
                 # Fits in slider, so clear custom val to keep it simple (or keep it? No, slider covers it)
                 self.custom_length_val = None
                 self.slider_length.set(new_len)
                 
            self.label_length_val.configure(text=f"{new_len:.1f}s")

    def toggle_start(self):
        if self.check_start.get():
            self.slider_start.configure(state="normal")
            self.label_start_val.configure(text_color=("black", "white"))
        else:
            self.slider_start.configure(state="disabled")
            self.label_start_val.configure(text_color="gray")
            
    def update_start_label(self, value):
        # If slider is moving, we discard any custom value
        self.custom_start_val = None
        self.label_start_val.configure(text=f"{value:.1f}s")

    def edit_start_value(self, event):
        self.close_active_edits()
        if self.check_start.get():
            # Hide label, show entry
            self.label_start_val.grid_remove()
            self.entry_start_val.grid(row=2, column=2, padx=5, pady=4)
            
            # Set current text
            current_text = self.label_start_val.cget("text").replace("s", "")
            self.entry_start_val.delete(0, "end")
            self.entry_start_val.insert(0, current_text)
            
            self.after(50, lambda: self._focus_and_select(self.entry_start_val))

    def submit_start_value(self, event):
        text = self.entry_start_val.get()
        try:
            val = float(text)
            if val < 0: val = 0.0
            
            self.custom_start_val = val
            
            # Update label
            self.label_start_val.configure(text=f"{val:.1f}s")
            
            # Update Slider (Clamp to max)
            if val <= 60.0:
                self.slider_start.set(val)
            else:
                self.slider_start.set(60.0)
                
        except ValueError:
            # Invalid input, ignore
            pass
            
        # Restore UI
        self.entry_start_val.grid_remove()
        self.label_start_val.grid(row=2, column=2, padx=5, pady=4)

    def toggle_length(self):
        if self.check_length.get():
            self.slider_length.configure(state="normal")
            self.label_length_val.configure(text_color=("black", "white"))
            self.check_constraints()
        else:
             self.slider_length.configure(state="disabled")
             self.label_length_val.configure(text_color="gray")

    def update_length_label(self, value):
        # Slider interaction resets custom value
        self.custom_length_val = None
        
        time_val = value
        
        if self.check_crossfade.get():
            if time_val < 0.5:
                time_val = 0.5
                self.slider_length.set(0.5)
                
            xfade = self.get_effective_crossfade()
            min_len = xfade + 0.5
            
            if time_val < min_len:
                # REVERSE CONSTRAINT: Reduce Crossfade
                new_xfade = time_val - 0.5
                if new_xfade < 0:
                    new_xfade = 0.0
                
                # Update Crossfade UI
                self.custom_crossfade_val = new_xfade
                self.label_crossfade_val.configure(text=f"{new_xfade:.1f}s")
                
                if new_xfade <= 59.5:
                    self.slider_duration.set(new_xfade)
                else:
                    self.slider_duration.set(59.5)
                    
        self.label_length_val.configure(text=f"{time_val:.1f}s")
        
    def edit_length_value(self, event):
        self.close_active_edits()
        if self.check_length.get():
            self.label_length_val.grid_remove()
            self.entry_length_val.grid(row=4, column=2, padx=5, pady=4)
            
            current_text = self.label_length_val.cget("text").replace("s", "")
            self.entry_length_val.delete(0, "end")
            self.entry_length_val.insert(0, current_text)
            
            self.after(50, lambda: self._focus_and_select(self.entry_length_val))

    def submit_length_value(self, event):
        text = self.entry_length_val.get()
        try:
            val = float(text)
            
            # Constraint Logic
            if self.check_crossfade.get():
                xfade = self.get_effective_crossfade()
                min_len = xfade + 0.5
                
                if val < min_len:
                    # REVERSE CONSTRAINT: Reduce Crossfade instead of increasing Length
                    new_xfade = val - 0.5
                    
                    if new_xfade < 0:
                        new_xfade = 0.0
                        val = 0.5 # Minimum length if crossfade is enabled (0 + 0.5)
                        
                    # Update Crossfade values
                    self.custom_crossfade_val = new_xfade
                    self.label_crossfade_val.configure(text=f"{new_xfade:.1f}s")
                    
                    if new_xfade <= 59.5:
                        self.slider_duration.set(new_xfade)
                    else:
                         self.slider_duration.set(59.5)
                         
            elif val < 0:
                val = 0.0
            
            self.custom_length_val = val
            self.label_length_val.configure(text=f"{val:.1f}s")
            
            # Update Slider
            if val <= 60.0:
                self.slider_length.set(val)
            else:
                self.slider_length.set(60.0)
                
        except ValueError:
            pass
            
        self.entry_length_val.grid_remove()
        self.label_length_val.grid(row=4, column=2, padx=5, pady=4)

    def toggle_scale(self):
        state = "normal" if self.check_scale.get() else "disabled"
        self.btn_4k.configure(state=state)
        self.btn_1080.configure(state=state)
        self.btn_720.configure(state=state)
        self.entry_width.configure(state=state)
        self.entry_height.configure(state=state)
        if state == "disabled":
            self.entry_width.delete(0, "end")
            self.entry_height.delete(0, "end")
            
    def set_scale(self, w, h):
        if not self.check_scale.get(): return
        self.entry_width.delete(0, "end")
        self.entry_width.insert(0, str(w))
        self.entry_height.delete(0, "end")
        self.entry_height.insert(0, str(h))

    def on_length_release(self, event):
        # Snap back logic removed (Real-time updates handle it)
        self.set_focused_slider(self.slider_length)

    def log(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def start_processing(self):
        # Gather active files
        active_files = [item['path'] for item in self.queue_items if item['var'].get()]
        
        if not active_files:
            self.log("Error: No files selected in queue!")
            return

        duration = self.get_effective_crossfade()
        fmt = self.seg_format.get().lower()
        enable_crossfade = bool(self.check_crossfade.get())
        
        target_length = None
        if self.check_length.get():
            if self.custom_length_val is not None:
                target_length = self.custom_length_val
            else:
                target_length = self.slider_length.get()
            
        start_offset = 0.0
        if self.check_start.get():
            if self.custom_start_val is not None:
                start_offset = self.custom_start_val
            else:
                start_offset = self.slider_start.get()

        # Calculate actual quality param
        raw_q_val = int(self.slider_quality.get())
        quality_val = None
        
        if fmt == "mp4":
            quality_val = 35 - raw_q_val # CRF
        elif fmt == "mjpeg":
            quality_val = 31 - raw_q_val # Q
        elif fmt == "prores":
            quality_val = raw_q_val # Profile ID
        elif fmt == "hap":
            quality_val = "hap" if raw_q_val == 0 else "hap_q"

        
        # Audio mode
        # audio_mode = self.var_audio_mode.get()

        # Scale
        scale_val = None
        if self.check_scale.get():
            try:
                w = int(self.entry_width.get())
                h = int(self.entry_height.get())
                if w > 0 and h > 0:
                    scale_val = (w, h)
                else:
                    self.log("Warning: Invalid scale dimensions ignored.")
            except ValueError:
                self.log("Warning: Invalid scale input (must be integers). Ignored.")

        # Filename options
        name_mode = self.var_name_mode.get()
        name_text = self.entry_name_text.get()

        self.btn_process.configure(state="disabled", text="Processing Code...")
        self.btn_files.configure(state="disabled")
        self.btn_folder.configure(state="disabled")
        self.btn_clear.configure(state="disabled")
        self.is_processing = True
        
        # Run in thread
        threading.Thread(target=self.run_batch, args=(active_files, duration, fmt, target_length, enable_crossfade, start_offset, quality_val, name_mode, name_text, scale_val)).start()

    def run_batch(self, files, duration, fmt, target_length=None, enable_crossfade=True, start_offset=0.0, quality_val=None, name_mode="Append", name_text="_oopl", scale_val=None):
        try:
            total = len(files)
            success_count = 0
            
            # Remove hardcoded global output_dir creation
            if self.custom_output_dir:
                self.log(f"Output mode: Custom -> {self.custom_output_dir}")
            else:
                self.log(f"Output mode: Same as Input File")

            for i, file_path in enumerate(files, 1):
                if not self.is_processing:
                    break
                
                filename = os.path.basename(file_path)
                self.log(f"\n[{i}/{total}] Processing: {filename}...")
                
                try:
                    # Construct Filename
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    ext = "mp4"
                    if fmt in ["hap", "prores", "mjpeg"]: ext = "mov"
                    
                    if name_mode == "Append":
                        out_name = f"{base_name}{name_text}.{ext}"
                    else:
                        out_name = f"{name_text}{base_name}.{ext}"
                        
                    # Determine Output Directory for this file
                    if self.custom_output_dir:
                        file_output_dir = self.custom_output_dir
                    else:
                        file_output_dir = os.path.dirname(file_path)
                        
                    output_path = process_video_crossfade(file_path, duration, fmt, target_output_duration=target_length, output_dir=file_output_dir, enable_crossfade=enable_crossfade, start_offset=start_offset, quality_val=quality_val, output_filename=out_name, target_resolution=scale_val)
                    self.log(f" -> Completed: {os.path.basename(output_path)}")
                    success_count += 1
                except Exception as e:
                    self.log(f" -> ERROR: {str(e)}")
            
            self.log(f"\nBatch Finished! {success_count}/{total} files processed successfully.")
            
        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")

        finally:
            self.is_processing = False
            self.btn_process.configure(state="normal", text="Start Batch")
            self.btn_files.configure(state="normal")
            self.btn_folder.configure(state="normal")
            self.btn_clear.configure(state="normal")
            # Clear queue (optional, but good for workflow)
            # self.file_queue = [] 
            # self.update_status()

if __name__ == "__main__":
    app = App()
    app.mainloop()
