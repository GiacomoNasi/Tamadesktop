import sys
import tkinter as tk
from PIL import Image, ImageTk
from Tamagochi import Tamagotchi

PLATFORM = 'chrome os' # sys.platform

class TamagotchiOverlay:
    def __init__(self, root, tamagotchi, image_path):
        self.tamagotchi = tamagotchi
        self.root = root

        # Trasparenza multipiattaforma
        if PLATFORM == "darwin":
            root.attributes("-fullscreen", True)
            root.wm_attributes("-topmost", True)
            try:
                root.attributes("-transparent", True)
                bg_color = "systemTransparent"
            except Exception:
                bg_color = "#f0f0f0"
        elif PLATFORM.startswith("win"):
            root.attributes("-fullscreen", True)
            root.wm_attributes("-topmost", True)
            try:
                root.wm_attributes("-transparentcolor", "white")
                bg_color = "white"
            except Exception:
                bg_color = "#f0f0f0"
        else:  # Linux e altri
            root.attributes("-fullscreen", True)
            root.wm_attributes("-topmost", True)
            try:
                root.wm_attributes("-alpha", 0.1)  # Finestra semitrasparente
            except Exception:
                pass
            bg_color = "#f0f0f0"

        self.width = root.winfo_screenwidth()
        self.height = root.winfo_screenheight()
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg=bg_color, highlightthickness=0)
        self.canvas.pack()
        img = Image.open(image_path)
        img = img.resize((150, 150), Image.Resampling.LANCZOS)
        self.tk_img = ImageTk.PhotoImage(img)
        self.img_width = self.tk_img.width()
        self.img_height = self.tk_img.height()
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.tama_img = self.canvas.create_image(self.center_x, self.center_y, image=self.tk_img)

        self.food_img = ImageTk.PhotoImage(Image.open("food.png").resize((60, 60)))
        self.food = None
        self.food_pos = None
        self.food_dragging = False

        self.status_labels = {}
        self._create_status_labels()
        self.update_status()
        self._start_tick_loop()

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.drag_food)
        self.canvas.bind("<ButtonRelease-1>", self.drop_food)

        self.moving_to_food = False
        self.move_speed = 10
        self.buttons_offset_y = 120
        self.buttons_visible = False
        self.button_items = []

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
                bg="white",
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

    def show_buttons(self, x, y):
        if self.buttons_visible:
            return
        self.button_items = []
        btn_y = y + self.buttons_offset_y
        btn_x_start = x - (8 * 44) // 2
        actions = [
            ("🍚", lambda: self.spawn_food()),         # Feed
            ("🍬", lambda: self.spawn_food("snack")),  # Snack
            ("⚽", self.tamagotchi.play),              # Play
            ("💤", self.tamagotchi.sleep),             # Sleep
            ("🧼", self.tamagotchi.clean),             # Clean
            ("💊", self.tamagotchi.heal),              # Heal
            ("😠", self.tamagotchi.scold),             # Scold
            ("⏰", self.tamagotchi.tick)               # Tick
        ]
        for i, (emoji, cmd) in enumerate(actions):
            cx = btn_x_start + i * 48 + 20
            cy = btn_y + 20
            oval = self.canvas.create_oval(
                cx - 20, cy - 20, cx + 20, cy + 20,
                fill="#fff", outline="#bbb", width=2, tags=("action_btn", f"btn_{i}")
            )
            text = self.canvas.create_text(
                cx, cy, text=emoji, font=("Arial", 20), tags=("action_btn", f"btn_{i}")
            )
            self.button_items.append((oval, text, cmd))
        self.canvas.tag_bind("action_btn", "<Button-1>", self.on_button_click)
        self.buttons_visible = True

    def hide_buttons(self):
        for oval, text, _ in self.button_items:
            self.canvas.delete(oval)
            self.canvas.delete(text)
        self.button_items = []
        self.buttons_visible = False

    def toggle_buttons(self, x, y):
        if self.buttons_visible:
            self.hide_buttons()
        else:
            self.show_buttons(x, y)

    def _start_tick_loop(self):
        self.tamagotchi.tick()
        self.root.after(1000, self._start_tick_loop)

    def spawn_food(self, food_type="meal"):
        if self.food is not None or self.moving_to_food:
            return
        self.food_type = food_type
        self.food = self.canvas.create_image(60, self.height - 60, image=self.food_img)
        self.food_pos = (60, self.height - 60)
        self.food_dragging = True

    def start_drag_food(self, event):
        if self.food is not None:
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
            self.tamagotchi.feed(self.food_type)
            self.canvas.delete(self.food)
            self.food = None
            self.moving_to_food = False
        else:
            step = min(self.move_speed, dist)
            nx = x + step * dx / dist
            ny = y + step * dy / dist
            self.canvas.coords(self.tama_img, nx, ny)
            if self.buttons_visible:
                self.hide_buttons()
                self.show_buttons(nx, ny)
            self.root.after(30, self.move_tamagotchi_to_food)

    def on_button_click(self, event):
        item = self.canvas.find_withtag("current")
        for oval, text, cmd in self.button_items:
            if item and (item[0] == oval or item[0] == text):
                self.hide_buttons()
                cmd()
                break

    def on_canvas_click(self, event):
        if self.food is not None:
            fx, fy = self.canvas.coords(self.food)
            if abs(event.x - fx) < 40 and abs(event.y - fy) < 40:
                self.start_drag_food(event)
                return
        tx, ty = self.canvas.coords(self.tama_img)
        half_w = self.img_width // 2
        half_h = self.img_height // 2
        if (tx - half_w <= event.x <= tx + half_w) and (ty - half_h <= event.y <= ty + half_h):
            self.toggle_buttons(tx, ty)
        else:
            self.hide_buttons()

if __name__ == "__main__":
    root = tk.Tk()
    tama = Tamagotchi("Tama")
    overlay = TamagotchiOverlay(root, tama, "tamagochi.png")
    root.mainloop()