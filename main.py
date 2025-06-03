import tkinter as tk
from PIL import Image, ImageTk

root = tk.Tk()
root.attributes("-fullscreen", True)
root.wm_attributes("-topmost", True)
root.wm_attributes("-transparentcolor", "white")

width = root.winfo_screenwidth()
height = root.winfo_screenheight()

canvas = tk.Canvas(root, width=width, height=height, bg="white", highlightthickness=0)
canvas.pack()

# Carica l'immagine originale e crea la versione ribaltata
img_orig = Image.open("tamagochi.png")
img_orig = img_orig.resize(
    (img_orig.width // 5, img_orig.height // 5),
    Image.Resampling.LANCZOS
)
img_flip = img_orig.transpose(Image.FLIP_LEFT_RIGHT)

tamagochi_img_dx = ImageTk.PhotoImage(img_orig)
tamagochi_img_sx = ImageTk.PhotoImage(img_flip)

img_width = tamagochi_img_dx.width()
img_height = tamagochi_img_dx.height()

x, y = width // 2, height // 2
dx, dy = 5, 3
current_img = tamagochi_img_dx

tamagochi = canvas.create_image(x, y, image=current_img)

def move_tamagochi():
    global x, y, dx, dy, current_img
    x += dx
    y += dy

    # Cambia immagine in base alla direzione
    if dx < 0:
        current_img = tamagochi_img_sx
    else:
        current_img = tamagochi_img_dx
    canvas.itemconfig(tamagochi, image=current_img)

    if x - img_width // 2 <= 0 or x + img_width // 2 >= width:
        dx = -dx
    if y - img_height // 2 <= 0 or y + img_height // 2 >= height:
        dy = -dy

    canvas.coords(tamagochi, x, y)
    root.after(16, move_tamagochi)

move_tamagochi()
root.mainloop()