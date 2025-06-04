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
        self.setGeometry(100, 100, 1000, 1000)

        self.tama_img = QtGui.QPixmap(image_path).scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self._tama_pos = QtCore.QPoint(self.width() // 2 - 75, self.height() // 2 - 75)

        self.food_pos = None
        self.food_type = None
        self.food_emoji = None

        self.placing_food = False
        self.food_mouse_pos = QtCore.QPoint(0, 0)

        self.buttons = []
        self.buttons_visible = False

        self.status_labels = {}
        self.init_status_labels()
        self.update_status()
        self.update_status_labels_position()  # <-- aggiorna subito la posizione
        self.tick_timer = QtCore.QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(1000)

        self.setMouseTracking(True)

        # Carica le PNG per ogni statistica che va da 0 a 100
        self.bar_icons = {
            "hunger": QtGui.QPixmap("cookie.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "happiness": QtGui.QPixmap("pngs/happy.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "energy": QtGui.QPixmap("pngs/energy.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "hygiene": QtGui.QPixmap("pngs/hygene.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "health": QtGui.QPixmap("pngs/health.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "weight": QtGui.QPixmap("pngs/weight.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "discipline": QtGui.QPixmap("pngs/discipline.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
        }

        self.bar_areas = {}  # Mappa: nome_statistica -> QRect area barra

    def desaturate_pixmap(self, pixmap):
        # Converte un QPixmap a scala di grigi
        img = pixmap.toImage().convertToFormat(QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap.fromImage(img)

    def init_status_labels(self):
        fields = [
            # "hunger",  # <-- RIMUOVI la label per la fame
            # "happiness",
            # "energy", "hygiene", "health",
            "age",
            # "weight", "discipline",
            "sick", "needs_toilet"
        ]
        y_offset = 0
        for field in fields:
            label = QtWidgets.QLabel(self)
            label.setText("")
            label.setStyleSheet("background: rgba(255,255,255,0.8); border: 1px solid #bbb; font: 14px Arial;")
            label.setGeometry(0, 0, 200, 24)  # la posizione verrà aggiornata dopo
            label.show()
            self.status_labels[field] = label
            y_offset += 28

    def update_status_labels_position(self):
        # Posiziona le label a sinistra del Tamagotchi
        base_x = self.tama_pos.x() - 200 - 20  # 200 = larghezza label, 20 = margine
        base_y = self.tama_pos.y() + 28*3
        for i, label in enumerate(self.status_labels.values()):
            label.move(base_x, base_y + i * 28)

    def update_status(self):
        status = self.tamagotchi.status()
        for field, label in self.status_labels.items():
            # if field == "hunger":
            #     label.setText("")  # Non serve più
            # else:
            value = status[field]
            label.setText(f"{field.capitalize()}: {value}")
        QtCore.QTimer.singleShot(500, self.update_status)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(self.tama_pos, self.tama_img)
        # Disegna i biscotti per la fame
        hunger = self.tamagotchi.status()["hunger"]
        full_cookies = (100 - hunger) // 10
        empty_cookies = 10 - full_cookies
        # Calcola la posizione dove sarebbero state le label (sopra la prima label)
        base_x = self.tama_pos.x() + self.tama_img.width() + 20
        base_y = self.tama_pos.y()
        x = base_x
        y = base_y

        fields = [
            "hunger",
            "happiness",
            "energy", "hygiene", "health",
            "weight", "discipline"
        ]

        delta_y = 0
        self.bar_areas.clear()
        for f in fields:
            metric = 100 - self.tamagotchi.status()[f] if f == "hunger" else self.tamagotchi.status()[f]
            bar_rect = QtCore.QRect(x, y + delta_y, 26 * 10, 24)
            self.bar_areas[f] = bar_rect
            for i in range(metric // 10):
                painter.drawPixmap(x + i * 26, y + delta_y, self.bar_icons[f])
            delta_y = delta_y + 28

        # Disegna l'emoji del cibo se presente
        if self.food_pos and self.food_emoji:
            font = QtGui.QFont("Arial", 40)
            painter.setFont(font)
            painter.drawText(
                QtCore.QRect(self.food_pos.x(), self.food_pos.y(), 60, 60),
                QtCore.Qt.AlignCenter, self.food_emoji
            )
        # Disegna l'emoji mentre si sta posizionando il cibo
        if self.placing_food and self.food_emoji:
            font = QtGui.QFont("Arial", 40)
            painter.setFont(font)
            pos = self.food_mouse_pos - QtCore.QPoint(30, 30)
            painter.drawText(
                QtCore.QRect(pos.x(), pos.y(), 60, 60),
                QtCore.Qt.AlignCenter, self.food_emoji
            )
        if self.buttons_visible:
            for btn in self.buttons:
                btn.draw(painter)

    def mousePressEvent(self, event):
        if self.placing_food:
            # Posa il cibo dove hai cliccato
            self.food_pos = event.pos() - QtCore.QPoint(30, 30)
            self.placing_food = False
            self.update()  # Richiede il repaint
            # Avvia l’animazione solo dopo che il cibo è stato disegnato
            QtCore.QTimer.singleShot(0, self.move_tamagotchi_to_food)
            return
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

    def mouseMoveEvent(self, event):
        if self.placing_food:
            self.food_mouse_pos = event.pos()
            self.update()
            return

        # Tooltip per le barre delle statistiche
        for stat, rect in self.bar_areas.items():
            if rect.contains(event.pos()):
                value = self.tamagotchi.status()[stat]
                QtWidgets.QToolTip.showText(
                    self.mapToGlobal(event.pos()),
                    f"{stat.capitalize()}: {value}",
                    self,
                    rect
                )
                break
        else:
            QtWidgets.QToolTip.hideText()

    def mouseReleaseEvent(self, event):
        pass  # Non serve più per il cibo

    def toggle_buttons(self):
        if self.buttons_visible:
            self.hide_buttons()
        else:
            self.show_buttons()

    def show_buttons(self):
        self.buttons = []
        actions = [
            ("🍚", lambda: self.start_placing_food("meal")),
            ("🍬", lambda: self.start_placing_food("snack")),
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
        self.close()

    def start_placing_food(self, food_type="meal"):
        if self.food_pos or self.placing_food:
            return
        self.food_type = food_type
        self.food_emoji = "🍚" if food_type == "meal" else "🍬"
        self.placing_food = True
        self.food_mouse_pos = QtGui.QCursor.pos() - self.mapToGlobal(QtCore.QPoint(0, 0))
        self.hide_buttons()
        self.update()

    def move_tamagotchi_to_food(self):
        if not self.food_pos:
            return
        self.anim = QtCore.QPropertyAnimation(self, b"tama_pos")
        self.anim.setDuration(1000)
        self.anim.setStartValue(self.tama_pos)
        self.anim.setEndValue(self.food_pos)
        self.anim.finished.connect(self.eat_food)
        self.anim.start()

    def get_tama_pos(self):
        return self._tama_pos

    def set_tama_pos(self, pos):
        self._tama_pos = pos
        self.update_status_labels_position()  # <-- aggiorna la posizione delle label
        self.update()

    tama_pos = QtCore.pyqtProperty(QtCore.QPoint, fget=get_tama_pos, fset=set_tama_pos)

    def eat_food(self):
        self.tamagotchi.feed(self.food_type)
        self.food_pos = None
        self.food_emoji = None
        self.update()

    def tick(self):
        self.tamagotchi.tick()
        self.update()  # Aggiorna la finestra per ridisegnare le barre

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
