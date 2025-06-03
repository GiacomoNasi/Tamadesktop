import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from Tamagochi import Tamagotchi

class TamagotchiOverlay:
    def __init__(self, root, tamagotchi, image_path):
        self.tamagotchi = tamagotchi
        self.root = root

        root.attributes("-fullscreen", True)
        root.wm_attributes("-topmost", True)
        root.wm_attributes("-transparentcolor", "white")
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()

        self.canvas = tk.Canvas(root, width=width, height=height, bg="white", highlightthickness=0)
        self.canvas.pack()

        img = Image.open(image_path)
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)
        self.img_width = self.tk_img.width()
        self.img_height = self.tk_img.height()
        self.center_x = width // 2
        self.center_y = height // 2
        self.tama_img = self.canvas.create_image(self.center_x, self.center_y, image=self.tk_img)

        self.status_labels = {}
        self._create_status_labels(width, height)
        self._create_buttons(width, height)
        self.update_status()
        self._start_tick_loop()  # Avvia il ciclo tick

    def _create_status_labels(self, width, height):
        fields = [
            "hunger", "happiness", "energy", "hygiene", "health",
            "age", "weight", "discipline", "sick", "needs_toilet"
        ]
        x = self.center_x + 150
        y = self.center_y - 70
        for i, field in enumerate(fields):
            label = tk.Label(
                self.root,
                text="",
                anchor="w",
                font=("Arial", 14),
                bg="green",
                fg="black",
                bd=1,
                relief="solid"
            )
            label.place(x=x, y=y + i * 28, width=200, height=24)
            self.status_labels[field] = label

    def update_status(self):
        status = self.tamagotchi.status()
        for field, label in self.status_labels.items():
            value = status[field]
            label.config(text=f"{field.capitalize()}: {value}")
        self.root.after(500, self.update_status)

    def _create_buttons(self, width, height):
        actions = [
            ("Feed", lambda: self.tamagotchi.feed()),
            ("Snack", lambda: self.tamagotchi.feed("snack")),
            ("Play", self.tamagotchi.play),
            ("Sleep", self.tamagotchi.sleep),
            ("Clean", self.tamagotchi.clean),
            ("Heal", self.tamagotchi.heal),
            ("Scold", self.tamagotchi.scold),
            ("Tick", self.tamagotchi.tick)
        ]
        self.buttons = []
        btn_y = height - 60
        btn_x_start = self.center_x - (len(actions) * 60) // 2
        for i, (text, cmd) in enumerate(actions):
            btn = ttk.Button(self.root, text=text, command=cmd)
            btn.place(x=btn_x_start + i * 80, y=btn_y, width=70, height=35)
            self.buttons.append(btn)

    def _start_tick_loop(self):
        self.tamagotchi.tick()
        self.root.after(1000, self._start_tick_loop)

if __name__ == "__main__":
    root = tk.Tk()
    tama = Tamagotchi("Tama")
    overlay = TamagotchiOverlay(root, tama, "tamagochi.png")
    root.mainloop()