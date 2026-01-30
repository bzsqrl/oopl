import customtkinter as ctk

app = ctk.CTk()
slider = ctk.CTkSlider(app, from_=0, to=10)
print(f"Dir: {dir(slider)}")
try:
    print(f"From: {slider._from_}")
    print(f"To: {slider._to_}")
except Exception as e:
    print(f"Error accessing attributes: {e}")

app.destroy()
