# ui/setup_wizard.py
import asyncio
from bleak import BleakScanner
# 【修改】继承 QWidget
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox,
                             QPushButton, QFormLayout)
from PyQt6.QtCore import pyqtSignal  # 【新增】
from logic.referee import Referee
from core.device_node import DeviceNode
from config import DEVICE_NAME_PREFIX


class SetupWizard(QWidget):  # 【修改】继承 QWidget
    # 定义信号：配置完成时发送裁判列表
    setup_finished = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.referees = []
        self.scanned_devices = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 标题
        title = QLabel("步骤 1/2: 配置裁判设备")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # 1. 扫描按钮
        self.btn_scan = QPushButton("扫描蓝牙设备")
        self.btn_scan.clicked.connect(self.start_scan)
        layout.addWidget(self.btn_scan)

        self.lbl_status = QLabel("点击上方按钮开始扫描...")
        layout.addWidget(self.lbl_status)

        # 2. 简单配置区域
        form = QFormLayout()
        self.combo_device = QComboBox()
        form.addRow("选择计分器:", self.combo_device)
        layout.addLayout(form)

        layout.addStretch()

        # 3. 完成按钮
        self.btn_ok = QPushButton("开始计分")
        self.btn_ok.clicked.connect(self.on_finish)
        self.btn_ok.setEnabled(False)
        self.btn_ok.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        layout.addWidget(self.btn_ok)

        self.setLayout(layout)

    def start_scan(self):
        self.lbl_status.setText("正在扫描 BLE 设备 (5秒)...")
        self.btn_scan.setEnabled(False)
        asyncio.create_task(self.run_ble_scan())

    async def run_ble_scan(self):
        try:
            # 扫描5秒
            devices = await BleakScanner.discover(timeout=5.0)
            # 过滤名称
            self.scanned_devices = [d for d in devices if d.name and DEVICE_NAME_PREFIX in d.name]

            self.combo_device.clear()
            if not self.scanned_devices:
                self.lbl_status.setText("未找到 Counter 设备，请确保设备已开机")
            else:
                for d in self.scanned_devices:
                    self.combo_device.addItem(f"{d.name} ({d.address})", d)
                self.lbl_status.setText(f"扫描完成，找到 {len(self.scanned_devices)} 个设备")
                self.btn_ok.setEnabled(True)
        except Exception as e:
            self.lbl_status.setText(f"扫描出错: {str(e)}")
        finally:
            self.btn_scan.setEnabled(True)

    def on_finish(self):
        idx = self.combo_device.currentIndex()
        if idx < 0:
            return

        selected_ble_device = self.combo_device.itemData(idx)

        # 创建 Referee 对象
        referee = Referee(name="裁判A", mode="SINGLE")
        node = DeviceNode(selected_ble_device)
        referee.set_devices(primary=node)

        self.referees.append(referee)

        # 【关键修改】发射信号，而不是 accept()
        self.setup_finished.emit(self.referees)