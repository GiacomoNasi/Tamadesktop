from PyQt5 import QtGui, QtCore

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
