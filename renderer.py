import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from Tamagochi import Tamagotchi

class TamagotchiOverlay(QtWidgets.QWidget):
    def __init__(self, tamagotchi, image_path):
        super().__init__()
        self.tamagotchi = tamagotchi
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 600, 400)

        self.tama_img = QtGui.QPixmap(image_path).scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.tama_pos = QtCore.QPoint(self.width() // 2 - 75, self.height() // 2 - 75)

        self.food_img = QtGui.QPixmap("food.png").scaled(60, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.food_pos = None
        self.food_dragging = False
        self.food_type = "meal"

        self.buttons = []
        self.buttons_visible = False

        self.status_labels = {}
        self.init_status_labels()
        self.update_status()
        self.tick_timer = QtCore.QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(1000)

        self.setMouseTracking(True)

    def init_status_labels(self):
        fields = [
            "hunger", "happiness", "energy", "hygiene", "health",
            "age", "weight", "discipline", "sick", "needs_toilet"
        ]
        y = 20
        for field in fields:
            label = QtWidgets.QLabel(self)
            label.setText("")
            label.setStyleSheet("background: rgba(255,255,255,0.8); border: 1px solid #bbb; font: 14px Arial;")
            label.setGeometry(self.width() - 220, y, 200, 24)
            label.show()
            self.status_labels[field] = label
            y += 28

    def update_status(self):
        status = self.tamagotchi.status()
        for field, label in self.status_labels.items():
            value = status[field]
            label.setText(f"{field.capitalize()}: {value}")
        QtCore.QTimer.singleShot(500, self.update_status)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Disegna Tamagotchi
        painter.drawPixmap(self.tama_pos, self.tama_img)
        # Disegna cibo se presente
        if self.food_pos:
            painter.drawPixmap(self.food_pos, self.food_img)
        # Disegna bottoni se visibili
        if self.buttons_visible:
            for btn in self.buttons:
                btn.draw(painter)

    def mousePressEvent(self, event):
        if self.food_pos and (QtCore.QRect(self.food_pos, self.food_img.size()).contains(event.pos())):
            self.food_dragging = True
        elif QtCore.QRect(self.tama_pos, self.tama_img.size()).contains(event.pos()):
            self.toggle_buttons()
        else:
            self.hide_buttons()

    def mouseMoveEvent(self, event):
        if self.food_dragging and self.food_pos:
            self.food_pos = event.pos() - QtCore.QPoint(self.food_img.width() // 2, self.food_img.height() // 2)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.food_dragging:
            self.food_dragging = False
            self.move_tamagotchi_to_food()

    def toggle_buttons(self):
        if self.buttons_visible:
            self.hide_buttons()
        else:
            self.show_buttons()

    def show_buttons(self):
        self.buttons = []
        actions = [
            ("🍚", lambda: self.spawn_food("meal")),
            ("🍬", lambda: self.spawn_food("snack")),
            ("⚽", self.tamagotchi.play),
            ("💤", self.tamagotchi.sleep),
            ("🧼", self.tamagotchi.clean),
            ("💊", self.tamagotchi.heal),
            ("😠", self.tamagotchi.scold),
            ("⏰", self.tamagotchi.tick)
        ]
        cx = self.tama_pos.x() + self.tama_img.width() // 2
        cy = self.tama_pos.y() + self.tama_img.height() + 40
        for i, (emoji, cmd) in enumerate(actions):
            btn = ActionButton(emoji, QtCore.QPoint(cx - 180 + i * 50, cy), cmd)
            self.buttons.append(btn)
        self.buttons_visible = True
        self.update()

    def hide_buttons(self):
        self.buttons = []
        self.buttons_visible = False
        self.update()

    def mouseDoubleClickEvent(self, event):
        # Per test: doppio click chiude la finestra
        self.close()

    def mousePressEvent(self, event):
        if self.food_pos and (QtCore.QRect(self.food_pos, self.food_img.size()).contains(event.pos())):
            self.food_dragging = True
        elif QtCore.QRect(self.tama_pos, self.tama_img.size()).contains(event.pos()):
            self.toggle_buttons()
        elif self.buttons_visible:
            for btn in self.buttons:
                if btn.contains(event.pos()):
                    btn.cmd()
                    self.hide_buttons()
                    break
        else:
            self.hide_buttons()

    def spawn_food(self, food_type="meal"):
        if self.food_pos:
            return
        self.food_type = food_type
        self.food_pos = QtCore.QPoint(60, self.height() - 80)
        self.food_dragging = True
        self.update()

    def move_tamagotchi_to_food(self):
        if not self.food_pos:
            return
        # Movimento animato verso il cibo
        self.anim = QtCore.QPropertyAnimation(self, b"tama_pos")
        self.anim.setDuration(600)
        self.anim.setStartValue(self.tama_pos)
        self.anim.setEndValue(self.food_pos)
        self.anim.finished.connect(self.eat_food)
        self.anim.start()

    def get_tama_pos(self):
        return self.tama_pos

    def set_tama_pos(self, pos):
        self.tama_pos = pos
        self.update()

    tama_pos_prop = QtCore.pyqtProperty(QtCore.QPoint, fget=get_tama_pos, fset=set_tama_pos)

    def eat_food(self):
        self.tamagotchi.feed(self.food_type)
        self.food_pos = None
        self.update()

    def tick(self):
        self.tamagotchi.tick()

class ActionButton:
    def __init__(self, emoji, pos, cmd):
        self.emoji = emoji
        self.pos = pos
        self.cmd = cmd
        self.radius = 22

    def draw(self, painter):
        painter.setBrush(QtGui.QColor(255, 255, 255, 230))
        painter.setPen(QtGui.QPen(QtGui.QColor(180, 180, 180), 2))
        painter.drawEllipse(self.pos, self.radius, self.radius)
        font = QtGui.QFont("Arial", 20)
        painter.setFont(font)
        painter.setPen(QtGui.QColor(0, 0, 0))
        painter.drawText(
            QtCore.QRect(self.pos.x() - self.radius, self.pos.y() - self.radius, self.radius * 2, self.radius * 2),
            QtCore.Qt.AlignCenter, self.emoji
        )

    def contains(self, point):
        return (self.pos - point).manhattanLength() < self.radius + 4

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    tama = Tamagotchi("Tama")
    overlay = TamagotchiOverlay(tama, "tamagochi.png")
    overlay.show()
    sys.exit(app.exec_())