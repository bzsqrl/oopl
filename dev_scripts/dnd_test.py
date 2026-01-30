import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES

class App(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)
        
        self.geometry("400x300")
        self.title("DND Test")
        
        self.label = ctk.CTkLabel(self, text="Drop files here")
        self.label.pack(expand=True)
        
        # Register for DND
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_event)
        
    def drop_event(self, event):
        print(f"Dropped: {event.data}")
        self.label.configure(text=f"Dropped: {event.data}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
