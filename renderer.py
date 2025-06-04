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

        self.buttons = []
        self.buttons_visible = False

        self.status_labels = {}
        self.init_status_labels()
        self.update_status()
        self.update_status_labels_position()
        self.tick_timer = QtCore.QTimer(self)
        self.tick_timer.timeout.connect(self.tick)
        self.tick_timer.start(10000)

        self.setMouseTracking(True)

        self.bar_icons = {
            "hunger": QtGui.QPixmap("cookie.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "happiness": QtGui.QPixmap("pngs/happy.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "energy": QtGui.QPixmap("pngs/energy.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "hygiene": QtGui.QPixmap("pngs/hygene.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "health": QtGui.QPixmap("pngs/health.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "weight": QtGui.QPixmap("pngs/weight.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
            "discipline": QtGui.QPixmap("pngs/discipline.png").scaled(24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation),
        }

        self.bar_areas = {}

    def desaturate_pixmap(self, pixmap):
        img = pixmap.toImage().convertToFormat(QtGui.QImage.Format_Grayscale8)
        return QtGui.QPixmap.fromImage(img)

    def init_status_labels(self):
        fields = [
            "age",
            "sick", "needs_toilet"
        ]
        y_offset = 0
        for field in fields:
            label = QtWidgets.QLabel(self)
            label.setText("")
            label.setStyleSheet("background: rgba(255,255,255,0.8); border: 1px solid #bbb; font: 14px Arial;")
            label.setGeometry(0, 0, 200, 24)
            label.show()
            self.status_labels[field] = label
            y_offset += 28

    def update_status_labels_position(self):
        base_x = self.tama_pos.x() - 200 - 20
        base_y = self.tama_pos.y() + 28*3
        for i, label in enumerate(self.status_labels.values()):
            label.move(base_x, base_y + i * 28)

    def update_status(self):
        status = self.tamagotchi.status()
        for field, label in self.status_labels.items():
            value = status[field]
            label.setText(f"{field.capitalize()}: {value}")
        QtCore.QTimer.singleShot(500, self.update_status)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(self.tama_pos, self.tama_img)

        fields = [
            "hunger",
            "happiness",
            "energy", "hygiene", "health",
            "weight", "discipline"
        ]

        base_x = self.tama_pos.x() + self.tama_img.width() + 20
        base_y = self.tama_pos.y()
        icon_size = 48
        col_spacing = 20
        row_spacing = 8
        num_cols = 2

        self.bar_areas.clear()
        for idx, f in enumerate(fields):
            value = self.tamagotchi.status()[f]
            if f == "hunger":
                percent = 1.0 - (value / 100.0)
            else:
                percent = value / 100.0

            icon = self.bar_icons[f]
            icon = icon.scaled(icon_size, icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            col = idx % num_cols
            row = idx // num_cols
            px = base_x + col * (icon_size + col_spacing)
            py = base_y + row * (icon_size + row_spacing)
            self.bar_areas[f] = QtCore.QRect(px, py, icon_size, icon_size)

            painter.save()
            painter.setClipRect(px, py + int((1 - percent) * icon_size), icon_size, int(percent * icon_size))
            painter.setOpacity(1.0)
            painter.drawPixmap(px, py, icon)
            painter.restore()

            painter.save()
            painter.setClipRect(px, py, icon_size, int((1 - percent) * icon_size))
            painter.setOpacity(0.25)
            painter.drawPixmap(px, py, icon)
            painter.restore()

        if self.buttons_visible:
            for btn in self.buttons:
                btn.draw(painter)

    def mousePressEvent(self, event):
        if QtCore.QRect(self.tama_pos, self.tama_img.size()).contains(event.pos()):
            self.toggle_buttons()
        elif self.buttons_visible:
            for btn in self.buttons:
                if btn.contains(event.pos()):
                    btn.cmd()
                    self.update()
                    # NON chiudere il menu qui
                    break
        else:
            self.hide_buttons()

    def mouseMoveEvent(self, event):
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
            if self.buttons_visible:
                action_tooltips = {
                    "🍚": "Dai un pasto",
                    "🍬": "Dai uno snack",
                    "⚽": "Gioca",
                    "💤": "Fai dormire",
                    "🧼": "Pulisci",
                    "💊": "Cura",
                    "😠": "Sgrida"
                }
                for btn in self.buttons:
                    if btn.contains(event.pos()):
                        tip = action_tooltips.get(btn.emoji, "Azione")
                        QtWidgets.QToolTip.showText(
                            self.mapToGlobal(event.pos()),
                            tip,
                            self
                        )
                        break
                else:
                    QtWidgets.QToolTip.hideText()
            else:
                QtWidgets.QToolTip.hideText()

    def mouseReleaseEvent(self, event):
        pass

    def toggle_buttons(self):
        if self.buttons_visible:
            self.hide_buttons()
        else:
            self.show_buttons()

    def show_buttons(self):
        self.buttons = []
        actions = [
            ("🍚", lambda: self.feed_and_update("meal")),
            ("🍬", lambda: self.feed_and_update("snack")),
            ("⚽", self.tamagotchi.play),
            ("💤", self.tamagotchi.sleep),
            ("🧼", self.tamagotchi.clean),
            ("💊", self.tamagotchi.heal),
            ("😠", self.tamagotchi.scold)
        ]
        buttons_per_row = 4
        spacing_x = 50
        spacing_y = 60

        total_width = (buttons_per_row - 1) * spacing_x
        cx = self.tama_pos.x() + self.tama_img.width() // 2
        cy = self.tama_pos.y() + self.tama_img.height() + 40

        for i, (emoji, cmd) in enumerate(actions):
            row = i // buttons_per_row
            col = i % buttons_per_row
            btn_x = cx - total_width // 2 + col * spacing_x
            btn_y = cy + row * spacing_y
            btn = ActionButton(emoji, QtCore.QPoint(btn_x, btn_y), cmd)
            self.buttons.append(btn)
        self.buttons_visible = True
        self.update()

    def hide_buttons(self):
        self.buttons = []
        self.buttons_visible = False
        self.update()

    # Rimuovi o commenta questo metodo per evitare che la finestra si chiuda al doppio click
    # def mouseDoubleClickEvent(self, event):
    #     self.close()

    def feed_and_update(self, food_type):
        self.tamagotchi.feed(food_type)
        self.update()

    def get_tama_pos(self):
        return self._tama_pos

    def set_tama_pos(self, pos):
        self._tama_pos = pos
        self.update_status_labels_position()
        self.update()

    tama_pos = QtCore.pyqtProperty(QtCore.QPoint, fget=get_tama_pos, fset=set_tama_pos)

    def tick(self):
        self.tamagotchi.tick()
        self.update()

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
