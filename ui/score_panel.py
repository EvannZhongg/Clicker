# ui/score_panel.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class ScorePanel(QFrame):
    def __init__(self, referee):
        super().__init__()
        self.referee = referee
        self.init_ui()

        # 【关键修改】添加 Qt.ConnectionType.QueuedConnection
        # 强制将更新任务放入主线程的消息队列，避免后台线程触碰 UI 导致崩溃
        self.referee.score_updated.connect(self.update_score, Qt.ConnectionType.QueuedConnection)

        if self.referee.primary_device:
            self.referee.primary_device.status_changed.connect(self.update_status_primary,
                                                               Qt.ConnectionType.QueuedConnection)
        if self.referee.secondary_device:
            self.referee.secondary_device.status_changed.connect(self.update_status_secondary,
                                                                 Qt.ConnectionType.QueuedConnection)

    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)

        layout = QVBoxLayout()

        # 裁判名称
        self.lbl_name = QLabel(f"裁判: {self.referee.name} ({self.referee.mode}模式)")
        self.lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_name.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # 总分 (大字体)
        self.lbl_score = QLabel("0")
        self.lbl_score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_score.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.lbl_score.setStyleSheet("color: #2c3e50;")

        # 详情 (正分/负分)
        self.lbl_detail = QLabel("正分: 0 | 负分: 0")
        self.lbl_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_detail.setStyleSheet("color: #7f8c8d;")

        # 状态指示
        self.lbl_status = QLabel("等待连接...")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setStyleSheet("color: orange; font-size: 10px;")

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.lbl_score)
        layout.addWidget(self.lbl_detail)
        layout.addWidget(self.lbl_status)
        self.setLayout(layout)

    def update_score(self, total, plus, minus):
        self.lbl_score.setText(str(total))
        self.lbl_detail.setText(f"正分: {plus} | 负分: {minus}")

    def update_status_primary(self, status):
        # 简单处理：如果是双机模式，显示两个设备状态会更复杂，这里简化显示
        self.lbl_status.setText(f"主设备: {status}")
        self._update_status_color(status)

    def update_status_secondary(self, status):
        current_text = self.lbl_status.text()
        self.lbl_status.setText(f"{current_text} | 副设备: {status}")

    def _update_status_color(self, status):
        if "Connected" in status and "Dis" not in status:
            self.lbl_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.lbl_status.setStyleSheet("color: red;")