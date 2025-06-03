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
        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white", highlightthickness=0)
        self.canvas.pack()

        # Tamagotchi
        img = Image.open(image_path)
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)
        self.img_width = self.tk_img.width()
        self.img_height = self.tk_img.height()
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.tama_img = self.canvas.create_image(self.center_x, self.center_y, image=self.tk_img)

        # Cibo
        self.food_img = ImageTk.PhotoImage(Image.open("food.png").resize((60, 60)))
        self.food = None
        self.food_pos = None
        self.food_dragging = False

        # Stato
        self.status_labels = {}
        self._create_status_labels()
        self._create_buttons()
        self.update_status()
        self._start_tick_loop()

        # Drag & drop cibo
        self.canvas.bind("<ButtonPress-1>", self.start_drag_food)
        self.canvas.bind("<B1-Motion>", self.drag_food)
        self.canvas.bind("<ButtonRelease-1>", self.drop_food)

        # Movimento Tamagotchi
        self.moving_to_food = False
        self.move_speed = 10

    def _create_status_labels(self):
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

    def _create_buttons(self):
        actions = [
            ("Feed", lambda: self.spawn_food()),
            ("Snack", lambda: self.spawn_food("snack")),
            ("Play", self.tamagotchi.play),
            ("Sleep", self.tamagotchi.sleep),
            ("Clean", self.tamagotchi.clean),
            ("Heal", self.tamagotchi.heal),
            ("Scold", self.tamagotchi.scold),
            ("Tick", self.tamagotchi.tick)
        ]
        self.buttons = []
        btn_y = self.height - 60
        btn_x_start = self.center_x - (len(actions) * 60) // 2
        for i, (text, cmd) in enumerate(actions):
            btn = ttk.Button(self.root, text=text, command=cmd)
            btn.place(x=btn_x_start + i * 80, y=btn_y, width=70, height=35)
            self.buttons.append(btn)

    def _start_tick_loop(self):
        self.tamagotchi.tick()
        self.root.after(1000, self._start_tick_loop)

    # --- Drag & Drop Cibo ---
    def spawn_food(self, food_type="meal"):
        if self.food is not None or self.moving_to_food:
            return
        # Crea il cibo in basso a sinistra
        self.food_type = food_type
        self.food = self.canvas.create_image(60, self.height - 60, image=self.food_img)
        self.food_pos = (60, self.height - 60)
        self.food_dragging = True

    def start_drag_food(self, event):
        if self.food is not None:
            # Inizia drag se clicchi sul cibo
            fx, fy = self.canvas.coords(self.food)
            if abs(event.x - fx) < 40 and abs(event.y - fy) < 40:
                self.food_dragging = True

    def drag_food(self, event):
        if self.food_dragging and self.food is not None:
            self.canvas.coords(self.food, event.x, event.y)
            self.food_pos = (event.x, event.y)

    def drop_food(self, event):
        if self.food_dragging and self.food is not None:
            self.food_dragging = False
            self.food_pos = (event.x, event.y)
            self.moving_to_food = True
            self.move_tamagotchi_to_food()

    def move_tamagotchi_to_food(self):
        if not self.moving_to_food or self.food is None:
            return
        x, y = self.canvas.coords(self.tama_img)
        fx, fy = self.food_pos
        dx = fx - x
        dy = fy - y
        dist = (dx**2 + dy**2) ** 0.5
        if dist < 20:
            # Arrivato: mangia
            self.tamagotchi.feed(self.food_type)
            self.canvas.delete(self.food)
            self.food = None
            self.moving_to_food = False
        else:
            # Muovi verso il cibo
            step = min(self.move_speed, dist)
            nx = x + step * dx / dist
            ny = y + step * dy / dist
            self.canvas.coords(self.tama_img, nx, ny)
            self.root.after(30, self.move_tamagotchi_to_food)

if __name__ == "__main__":
    root = tk.Tk()
    tama = Tamagotchi("Tama")
    overlay = TamagotchiOverlay(root, tama, "tamagochi.png")
    root.mainloop()