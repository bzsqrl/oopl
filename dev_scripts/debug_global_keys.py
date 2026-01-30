import customtkinter as ctk

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        
        self.focused_slider = None
        
        self.slider1 = ctk.CTkSlider(self, from_=0, to=10)
        self.slider1.pack(pady=20)
        self.slider1.bind("<Button-1>", lambda e: self.set_focus(self.slider1))
        
        self.slider2 = ctk.CTkSlider(self, from_=0, to=100)
        self.slider2.pack(pady=20)
        self.slider2.bind("<Button-1>", lambda e: self.set_focus(self.slider2))
        
        self.label = ctk.CTkLabel(self, text="Click a slider then use Arrow Keys")
        self.label.pack()
        
        self.status = ctk.CTkLabel(self, text="Focused: None")
        self.status.pack()
        
        # Global bindings
        self.bind("<Left>", self.on_left)
        self.bind("<Right>", self.on_right)

    def set_focus(self, slider):
        print(f"Setting focus to {slider}")
        self.focused_slider = slider
        self.status.configure(text=f"Focused: {'Slider 1' if slider == self.slider1 else 'Slider 2'}")
        # Important: Don't return 'break' so drag still works

    def on_left(self, event):
        if self.focused_slider:
            print("Left Key -> Decrement")
            self.focused_slider.set(self.focused_slider.get() - 1)
        else:
            print("Left Key -> No Focus")

    def on_right(self, event):
        if self.focused_slider:
            print("Right Key -> Increment")
            self.focused_slider.set(self.focused_slider.get() + 1)
        else:
            print("Right Key -> No Focus")

if __name__ == "__main__":
    app = App()
    app.mainloop()
