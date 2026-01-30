import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        
        self.slider = ctk.CTkSlider(self, from_=0, to=10)
        self.slider.pack(pady=20)
        
        # Original attempt
        self.slider.bind("<Left>", lambda e: print("Left key pressed"))
        self.slider.bind("<Right>", lambda e: print("Right key pressed"))
        
        # Hypotheris: Needs explicit focus
        self.slider.bind("<Button-1>", lambda e: self.on_click(e))
        
        self.label = ctk.CTkLabel(self, text="Click slider then use arrows")
        self.label.pack()

    def on_click(self, event):
        print("Slider clicked, setting focus...")
        self.slider.focus_set()

if __name__ == "__main__":
    app = App()
    app.mainloop()
