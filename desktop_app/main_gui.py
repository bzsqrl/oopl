import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES
import os
import threading
import sys
import webbrowser
import glob
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
        self.geometry("550x680")
        self.minsize(500, 550)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1) # Log area expands

        self.queue_items = [] # List of dicts: {'path': str, 'var': BooleanVar, 'widget': CheckBox}
        self.is_processing = False
        self.focused_slider = None
        
        # Global Key Bindings
        self.bind("<Left>", lambda e: self.on_global_arrow_key(-1))
        self.bind("<Right>", lambda e: self.on_global_arrow_key(1))

        # Title
        self.label_title = ctk.CTkLabel(self, text="Oopl", font=("Arial", 18, "bold"))
        self.label_title.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")

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
        self.label_format.grid(row=0, column=0, padx=10, pady=10)

        self.seg_format = ctk.CTkSegmentedButton(self.frame_settings, values=["MP4", "HAP", "ProRes", "MJPEG"], command=self.update_quality_config)
        self.seg_format.set("MP4")
        self.seg_format.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Row 1: Quality Slider
        self.label_quality = ctk.CTkLabel(self.frame_settings, text="Quality:")
        self.label_quality.grid(row=1, column=0, padx=10, pady=10)
        
        # Initial config for MP4 (0-17 mapping to CRF 35-18)
        self.slider_quality = ctk.CTkSlider(self.frame_settings, from_=0, to=17, number_of_steps=17, command=self.update_quality_label)
        self.slider_quality.set(12) # Default around CRF 23 (35 - 12 = 23)
        self.slider_quality.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        
        self.label_quality_val = ctk.CTkLabel(self.frame_settings, text="CRF 23", width=80)
        self.label_quality_val.grid(row=1, column=2, padx=5, pady=10)

        # Row 2: Crossfade Control
        self.check_crossfade = ctk.CTkCheckBox(self.frame_settings, text="Crossfade", command=self.toggle_crossfade)
        self.check_crossfade.select() # Default ON
        self.check_crossfade.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.slider_duration = ctk.CTkSlider(self.frame_settings, from_=0.1, to=10.0, number_of_steps=99, command=self.update_duration_label)
        self.slider_duration.set(1.0)
        self.slider_duration.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        
        self.label_crossfade_val = ctk.CTkLabel(self.frame_settings, text="1.0s", width=60)
        self.label_crossfade_val.grid(row=2, column=2, padx=5, pady=10)

        # Row 3: Set Start
        self.check_start = ctk.CTkCheckBox(self.frame_settings, text="Set Start", command=self.toggle_start)
        self.check_start.grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        self.slider_start = ctk.CTkSlider(self.frame_settings, from_=0, to=10.0, number_of_steps=100, command=self.update_start_label, state="disabled")
        self.slider_start.set(0.0)
        self.slider_start.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        self.label_start_val = ctk.CTkLabel(self.frame_settings, text="0.0s", width=60)
        self.label_start_val.grid(row=3, column=2, padx=5, pady=10)
        self.label_start_val.configure(text_color="gray")

        # Row 4: Set Length
        self.check_length = ctk.CTkCheckBox(self.frame_settings, text="Set Length", command=self.toggle_length)
        self.check_length.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        
        self.slider_length = ctk.CTkSlider(self.frame_settings, from_=0, to=140, number_of_steps=140, command=self.update_length_label, state="disabled")
        self.slider_length.set(self.time_to_slider(10.0))
        self.slider_length.grid(row=4, column=1, padx=10, pady=10, sticky="ew")
        
        self.label_length_val = ctk.CTkLabel(self.frame_settings, text="10.0s", width=60)
        self.label_length_val.grid(row=4, column=2, padx=5, pady=10)
        self.label_length_val.configure(text_color="gray")

        # Row 5: Filename configuration
        self.label_filename = ctk.CTkLabel(self.frame_settings, text="Filename:")
        self.label_filename.grid(row=5, column=0, padx=10, pady=10)
        
        # Frame for controls
        self.frame_filename = ctk.CTkFrame(self.frame_settings, fg_color="transparent")
        self.frame_filename.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        
        self.var_name_mode = ctk.StringVar(value="Append")
        self.radio_prepend = ctk.CTkRadioButton(self.frame_filename, text="Prepend", variable=self.var_name_mode, value="Prepend")
        self.radio_prepend.pack(side="left", padx=(0, 10))
        
        self.radio_append = ctk.CTkRadioButton(self.frame_filename, text="Append", variable=self.var_name_mode, value="Append")
        self.radio_append.pack(side="left", padx=(0, 10))
        
        self.entry_name_text = ctk.CTkEntry(self.frame_filename, width=100)
        self.entry_name_text.pack(side="left")
        self.entry_name_text.insert(0, " loop")

        # Keyboard bindings
        # Keyboard bindings
        self.slider_quality.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_quality))
        self.slider_duration.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_duration))
        self.slider_start.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_start))
        self.slider_length.bind("<Button-1>", lambda e: self.set_focused_slider(self.slider_length))

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
        
        self.btn_clear = ctk.CTkButton(self.frame_queue, text="Clear", command=self.clear_queue, width=60, fg_color="firebrick")
        self.btn_clear.grid(row=0, column=3, padx=10, pady=5, sticky="e")
        self.frame_queue.grid_columnconfigure(3, weight=1) # Clear button pushes right? No, weight keeps it flexible. 
        # Actually to push Clear right, we can put a spacer or use weight on an empty column.
        # Let's just grid them tightly left-to-right for now, it's compact.
        
        # Row 1: Status Label (Integrated)
        self.label_status = ctk.CTkLabel(self.frame_queue, text="No files selected", text_color="gray", font=("Arial", 12))
        self.label_status.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 5), sticky="w")
        
        # Row 2: Queue List (Scrollable)
        # Using a wrapper frame to enforce height limit
        self.frame_queue_container = ctk.CTkFrame(self.frame_queue, height=160, fg_color="transparent")
        self.frame_queue_container.grid(row=2, column=0, columnspan=4, padx=10, pady=5, sticky="ew")
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
        self.label_crossfade_val.configure(text=f"{value:.1f}s")
        if self.check_length.get():
             self.check_constraints()

    def update_quality_config(self, value=None):
        fmt = self.seg_format.get()
        if fmt == "MP4":
            # CRF 18 (Best) to 35 (Worst)
            # Slider 0 (Worst) to 17 (Best) -> CRF = 35 - val
            self.slider_quality.configure(from_=0, to=17, number_of_steps=17)
            self.slider_quality.set(12) # Default CRF 23
        elif fmt == "MJPEG":
            # Q 2 (Best) to 31 (Worst)
            # Slider 0 (Worst) to 29 (Best) -> Q = 31 - val
            self.slider_quality.configure(from_=0, to=29, number_of_steps=29)
            self.slider_quality.set(26) # Default Q 5 (31 - 26 = 5)
        elif fmt == "ProRes":
            # 0:Proxy, 1:LT, 2:Std, 3:HQ
            self.slider_quality.configure(from_=0, to=3, number_of_steps=3)
            self.slider_quality.set(2) # Default Standard
        elif fmt == "HAP":
            # 0:Hap, 1:Hap Q
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

    def slider_to_time(self, value):
        if value <= 90:
            # 0-90 maps to 1.0 - 10.0 (0.1s per step)
            return 1.0 + (value * 0.1)
        else:
            # 91-140 maps to 11.0 - 60.0 (1.0s per step)
            return 10.0 + (value - 90)

    def time_to_slider(self, time_val):
        if time_val <= 10.0:
            return (time_val - 1.0) * 10
        else:
            return 90 + (time_val - 10.0)

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
        # For slider_duration: range 0.1-5.0, steps 49 => step = 0.1
        # For slider_trim: range 0-140, steps 140 => step = 1.0
        
        step = 1.0 # Default step size in value units
        
        if slider == self.slider_duration:
             # Range 0.1 - 10.0, steps 99 => step 0.1
             step = 0.1
        elif slider == self.slider_start:
             step = 0.1
        elif slider == self.slider_length:
             step = 1.0
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
        xfade = self.slider_duration.get()
        length_slider_val = self.slider_length.get()
        length_time = self.slider_to_time(length_slider_val)
        
        min_len = xfade + 0.5
        
        if length_time < min_len:
            # We need to increase length.
            # If min_len > 10.0, we must snap to the next integer
            if min_len > 10.0:
               import math
               length_time = math.ceil(min_len)
            else:
               length_time = min_len
               
            # Update slider position (reverse map)
            new_slider_val = self.time_to_slider(length_time)
            
            # Additional clamp
            if new_slider_val > 140:
                 new_slider_val = 140
                 length_time = 60.0 
                 
            self.slider_length.set(new_slider_val)
            self.label_length_val.configure(text=f"{length_time:.1f}s")

    def toggle_start(self):
        if self.check_start.get():
            self.slider_start.configure(state="normal")
            self.label_start_val.configure(text_color=("black", "white"))
        else:
            self.slider_start.configure(state="disabled")
            self.label_start_val.configure(text_color="gray")
            
    def update_start_label(self, value):
        self.label_start_val.configure(text=f"{value:.1f}s")

    def toggle_length(self):
        if self.check_length.get():
            self.slider_length.configure(state="normal")
            self.label_length_val.configure(text_color=("black", "white"))
            self.check_constraints()
        else:
             self.slider_length.configure(state="disabled")
             self.label_length_val.configure(text_color="gray")

    def update_length_label(self, value):
        time_val = self.slider_to_time(value)
        # Check constraints immediately during drag if crossfade enabled
        if self.check_crossfade.get():
            xfade = self.slider_duration.get()
            min_len = xfade + 0.5
            
            if time_val < min_len:
                time_val = min_len
                # Snap slider back
                self.slider_length.set(self.time_to_slider(time_val))
            
        self.label_length_val.configure(text=f"{time_val:.1f}s")

    def log(self, message):
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")

    def start_processing(self):
        # Gather active files
        active_files = [item['path'] for item in self.queue_items if item['var'].get()]
        
        if not active_files:
            self.log("Error: No files selected in queue!")
            return

        duration = self.slider_duration.get()
        fmt = self.seg_format.get().lower()
        enable_crossfade = bool(self.check_crossfade.get())
        
        target_length = None
        if self.check_length.get():
            target_length = self.slider_to_time(self.slider_length.get())
            
        start_offset = 0.0
        if self.check_start.get():
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

        # Filename options
        name_mode = self.var_name_mode.get()
        name_text = self.entry_name_text.get()

        self.btn_process.configure(state="disabled", text="Processing Code...")
        self.btn_files.configure(state="disabled")
        self.btn_folder.configure(state="disabled")
        self.btn_clear.configure(state="disabled")
        self.is_processing = True
        
        # Run in thread
        threading.Thread(target=self.run_batch, args=(active_files, duration, fmt, target_length, enable_crossfade, start_offset, quality_val, name_mode, name_text)).start()

    def run_batch(self, files, duration, fmt, target_length=None, enable_crossfade=True, start_offset=0.0, quality_val=None, name_mode="Append", name_text=" loop"):
        try:
            total = len(files)
            success_count = 0
            
            # Ensure output dir exists
            output_dir = os.path.join(os.getcwd(), "outputs")
            os.makedirs(output_dir, exist_ok=True)
            self.log(f"Output directory: {output_dir}")

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
                        
                    output_path = process_video_crossfade(file_path, duration, fmt, target_output_duration=target_length, output_dir=output_dir, enable_crossfade=enable_crossfade, start_offset=start_offset, quality_val=quality_val, output_filename=out_name)
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
