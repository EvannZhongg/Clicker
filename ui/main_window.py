# ui/main_window.py
import asyncio
from PyQt6.QtWidgets import QMainWindow, QWidget, QGridLayout, QStackedWidget
from ui.setup_wizard import SetupWizard
from ui.score_panel import ScorePanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("电子计分系统 PC端")
        self.resize(800, 600)

        # 【关键修改】使用堆叠窗口部件 (页面切换)
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # 页面1：配置向导
        self.wizard_page = SetupWizard()
        self.wizard_page.setup_finished.connect(self.on_setup_finished)
        self.stack.addWidget(self.wizard_page)

        # 页面2：计分面板容器 (初始为空)
        self.dashboard_page = QWidget()
        self.dashboard_layout = QGridLayout(self.dashboard_page)
        self.stack.addWidget(self.dashboard_page)

        # 默认显示配置页
        self.stack.setCurrentIndex(0)

        self.referees = []

    def on_setup_finished(self, referees):
        """配置完成的回调"""
        self.referees = referees

        # 1. 初始化计分界面
        self.setup_dashboard()

        # 2. 切换到计分页面
        self.stack.setCurrentIndex(1)

        # 3. 开始连接设备
        self.connect_devices()

    def setup_dashboard(self):
        # 清理旧布局（如果有）
        # ...略 (简单版暂不考虑清理，因为只运行一次)

        row, col = 0, 0
        max_cols = 2

        for ref in self.referees:
            panel = ScorePanel(ref)
            self.dashboard_layout.addWidget(panel, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def connect_devices(self):
        # 异步连接
        for ref in self.referees:
            if ref.primary_device:
                asyncio.create_task(ref.primary_device.connect())
            if ref.secondary_device:
                asyncio.create_task(ref.secondary_device.connect())