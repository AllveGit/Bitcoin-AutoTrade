import sys
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtGui import QFont, QFontDatabase
from UIPkg.MainWindow import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Windows 스타일이 아니도록 변경
    app.setStyle(QStyleFactory.create('Fusion'))

    cw = MainWindow()
    cw.show()

    sys.exit(app.exec_())