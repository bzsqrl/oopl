from PIL import Image

def convert_to_ico(input_path, output_path):
    img = Image.open(input_path)
    # Save as ICO with multiple sizes
    img.save(output_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Converted {input_path} to {output_path}")

if __name__ == "__main__":
    convert_to_ico('c:/Users/beatf/Documents/Antigravity/Oopl/assets/icon.png', 
                   'c:/Users/beatf/Documents/Antigravity/Oopl/assets/icon.ico')
