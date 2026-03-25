from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import QTimer, Qt
import psutil
import torch
import os
from app.utils.ui_helpers import COLORS, STYLES


class SystemMonitorWidget(QWidget):
    """Widget to display CPU, RAM, and GPU usage for this process."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = psutil.Process(os.getpid())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        self.setStyleSheet(
            """
            QWidget {
                background-color: #2a2a2a;
                border: 1px solid #444444;
                border-radius: 6px;
            }
            QLabel {
                color: #d1d5db;
                font-size: 11px;
                font-weight: 600;
                border: none;
                background: transparent;
            }
            QProgressBar {
                border: 1px solid #333333;
                border-radius: 3px;
                background-color: #1a1a1a;
                text-align: center;
                color: white;
                font-size: 10px;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 2px;
            }
        """
        )

        # CPU Monitor
        self.cpu_label = QLabel("APP CPU: 0.0 Cores (0%)")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)

        # RAM Monitor
        self.ram_label = QLabel("APP RAM: 0 MB (0%)")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)

        # GPU Monitor (Optional based on torch.cuda availability)
        self.gpu_available = torch.cuda.is_available()
        if self.gpu_available:
            self.gpu_label = QLabel("GPU MEMORY: 0 MB")
            self.gpu_bar = QProgressBar()
            self.gpu_bar.setRange(0, 100)
            self.gpu_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #10b981; }"
            )
        else:
            self.gpu_label = QLabel("GPU: NOT DETECTED")
            self.gpu_label.setStyleSheet("color: #6b7280;")

        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)
        layout.addSpacing(2)
        layout.addWidget(self.ram_label)
        layout.addWidget(self.ram_bar)

        if self.gpu_available:
            layout.addSpacing(2)
            layout.addWidget(self.gpu_label)
            layout.addWidget(self.gpu_bar)
        else:
            layout.addWidget(self.gpu_label)

        # Update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_stats)
        self.timer.start(2000)  # Update every 2 seconds

    def _update_stats(self):
        try:
            # Update CPU for this process specifically
            # Returns total % used across all cores (e.g. 200% = 2 cores used)
            cpu_usage_total = self.process.cpu_percent(interval=None)
            cpu_cores = cpu_usage_total / 100.0
            cpu_percent_normalized = cpu_usage_total / psutil.cpu_count()

            self.cpu_label.setText(
                f"APP CPU: {cpu_cores:.2f} Cores ({cpu_percent_normalized:.1f}%)"
            )
            self.cpu_bar.setValue(min(100, int(cpu_percent_normalized)))

            # Update RAM for this process (RSS = Resident Set Size)
            ram_info = self.process.memory_info()
            ram_mb = ram_info.rss / (1024 * 1024)
            # Calculate % based on total system memory for context
            total_mem = psutil.virtual_memory().total / (1024 * 1024)
            ram_percent = (ram_mb / total_mem) * 100

            self.ram_label.setText(f"APP RAM: {int(ram_mb)} MB ({ram_percent:.1f}%)")
            # Update bar to show real process usage relative to system total
            self.ram_bar.setFormat("%p%")
            self.ram_bar.setValue(int(ram_percent))
            self.ram_bar.setMaximum(100)

            # Update GPU if available (PyTorch tracks its own allocation)
            if self.gpu_available:
                gpu_mem_used = torch.cuda.memory_allocated() / (1024 * 1024)
                gpu_mem_max = torch.cuda.get_device_properties(0).total_memory / (
                    1024 * 1024
                )

                self.gpu_label.setText(f"GPU MEMORY: {int(gpu_mem_used)} MB")
                self.gpu_bar.setMaximum(int(gpu_mem_max))
                self.gpu_bar.setValue(int(gpu_mem_used))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
