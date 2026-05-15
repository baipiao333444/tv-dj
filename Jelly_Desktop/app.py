import sys
import os
import ctypes
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage

# --- 【黑科技：强制刷新 Windows 任务栏图标】 ---
# Python 默认会显示那个丑陋的蛇形图标，这行代码告诉 Windows：我们是一个独立的新软件！
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("jelly.quant.terminal.1")
except:
    pass


# --- 【极客画笔：纯代码生成 . - 极简图标】 ---
# --- 【极客画笔：纯代码生成 . - 极简图标并保存】 ---
def create_minimalist_icon():
    # 创建一张 64x64 的全透明画布
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing) # 开启抗锯齿，边缘极其平滑

    # 蘸取“深海冰蓝”颜料
    pen = QPen(QColor("#5caaf6"))
    pen.setWidth(8)
    pen.setCapStyle(Qt.RoundCap)
    painter.setPen(pen)

    # 画图
    painter.drawPoint(16, 24)
    painter.drawLine(36, 24, 52, 24)
    painter.drawPoint(16, 44)
    painter.drawLine(28, 44, 48, 44)
    painter.end()

    # 【新增黑科技】：检查当前目录有没有 icon.ico，如果没有，就把画好的直接存硬盘！
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, 'icon.ico')
    if not os.path.exists(icon_path):
        pixmap.save(icon_path, "ICO") # 保存为标准的 Windows 图标格式

    return QIcon(pixmap)


# --- 拦截 JS 命令 ---
class JellyWebPage(QWebEnginePage):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        if msg == "CMD_CLOSE":
            self.main_window.close()
        elif msg == "CMD_MIN":
            self.main_window.showMinimized()
        elif msg == "CMD_DRAG":
            if self.main_window.windowHandle():
                self.main_window.windowHandle().startSystemMove()


class JellyDesktopApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Jelly Quant')
        self.resize(380, 700)

        # 【核心：应用我们自己画的极简图标】
        self.setWindowIcon(create_minimalist_icon())

        # 无边框 + 透明支持
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.browser = QWebEngineView()
        self.page = JellyWebPage(self)
        self.browser.setPage(self.page)
        self.browser.page().setBackgroundColor(Qt.transparent)

        # 接管网页下载，调用系统原生的“另存为”对话框
        self.browser.page().profile().downloadRequested.connect(self.handle_download)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        html_path = os.path.join(current_dir, 'index.html')
        self.browser.setUrl(QUrl.fromLocalFile(html_path))

        self.setCentralWidget(self.browser)
        self.browser.titleChanged.connect(self.handle_title_change)

    # 处理导出的保存对话框
    def handle_download(self, download_item):
        path, _ = QFileDialog.getSaveFileName(self, "保存 Jelly 备份", download_item.suggestedFileName(),
                                              "JSON Files (*.json)")
        if path:
            download_item.setPath(path)
            download_item.accept()

    def handle_title_change(self, title):
        if title == "PIN_ON":
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.show()
        elif title == "PIN_OFF":
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JellyDesktopApp()
    window.show()
    sys.exit(app.exec_())