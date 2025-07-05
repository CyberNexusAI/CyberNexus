import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, 
    QPushButton, QTextEdit, QLabel, QHBoxLayout
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QMutex, QWaitCondition
from src.utils.computer import ComputerControl
from src.biz.llm import LLMManager

class CyberNexusWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberNexus · Your AI Automation Assistant")
        self.setGeometry(300, 300, 540, 640)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowOpacity(0.9)

        # Set modern QSS style
        self.setStyleSheet('''
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #f8fafc, stop:1 #e0e7ef);
                font-size: 15px;
            }
            QLabel {
                color: #2d3748;
                font-weight: bold;
                margin-top: 8px;
                margin-bottom: 2px;
            }
            QTextEdit {
                background: #f4f7fa;
                border: 1.5px solid #b6c2d1;
                border-radius: 10px;
                padding: 10px;
                color: #22223b;
                font-size: 15px;
                min-height: 120px;
            }
            QLineEdit {
                background: #f4f7fa;
                border: 1.5px solid #b6c2d1;
                border-radius: 10px;
                padding: 8px 10px;
                color: #22223b;
                font-size: 15px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4f8cff, stop:1 #1e3a8a);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 0;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:pressed {
                background: #1e3a8a;
            }
        ''')
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 22, 28, 22)
        layout.setSpacing(12)

        layout.addWidget(QLabel("🧠 AI Thinking Area:"))
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setPlaceholderText("AI's thoughts and actions will appear here...")
        layout.addWidget(self.output_display)
        
        layout.addWidget(QLabel("💡 Please enter your request:"))
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("E.g.: Organize my desktop files, or describe any task you want the AI to automate...")
        self.input_field.setMinimumHeight(38)
        self.input_field.setStyleSheet("QLineEdit { font-size: 16px; padding: 12px 10px; }")
        layout.addWidget(self.input_field)
        
        self.process_btn = QPushButton("Run Smart Task Now")
        self.process_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.process_btn)

        # pause和resume按钮在一行
        btn_row = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_worker)
        self.pause_btn.setStyleSheet("QPushButton { background: #ffe066; color: #22223b; border-radius: 12px; padding: 10px 0; font-size: 16px; font-weight: bold; margin-top: 10px; } QPushButton:pressed { background: #ffd43b; }")
        btn_row.addWidget(self.pause_btn)

        self.resume_btn = QPushButton("Resume")
        self.resume_btn.setEnabled(False)
        self.resume_btn.clicked.connect(self.resume_worker)
        self.resume_btn.setStyleSheet("QPushButton { background: #51cf66; color: #fff; border-radius: 12px; padding: 10px 0; font-size: 16px; font-weight: bold; margin-top: 10px; } QPushButton:pressed { background: #40c057; }")
        btn_row.addWidget(self.resume_btn)

        layout.addLayout(btn_row)

        self.setLayout(layout)
        
        self.worker_thread = None
    
    def start_processing(self):
        input_data = self.input_field.text().strip()
        if not input_data:
            self.output_display.append("⚠️ Please enter a task description before running.")
            return
        
        self.process_btn.setEnabled(False)
        self.output_display.clear()
        self.output_display.append("🤖 AI is thinking and planning your automation, please wait...")
        
        self.pause_btn.setEnabled(True)
        self.resume_btn.setEnabled(False)

        self.worker_thread = AgentWorker(input_data)
        self.worker_thread.update_output.connect(self.update_output_display)
        self.worker_thread.finished.connect(self.on_worker_finished)
        self.worker_thread.paused.connect(self.on_worker_paused)
        self.worker_thread.resumed.connect(self.on_worker_resumed)
        self.worker_thread.start()
    
    def update_output_display(self, text):
        self.output_display.append(text)
        self.output_display.ensureCursorVisible()
    
    def pause_worker(self):
        if self.worker_thread:
            self.worker_thread.pause()
            self.pause_btn.setEnabled(False)
            self.resume_btn.setEnabled(True)

    def resume_worker(self):
        if self.worker_thread:
            self.worker_thread.resume()
            self.pause_btn.setEnabled(True)
            self.resume_btn.setEnabled(False)

    def on_worker_finished(self):
        self.process_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.resume_btn.setEnabled(False)
        self.worker_thread = None

    def on_worker_paused(self):
        self.update_output_display("⏸️ Paused.")

    def on_worker_resumed(self):
        self.update_output_display("▶️ Resumed.")

class AgentWorker(QThread):
    update_output = pyqtSignal(str)
    finished = pyqtSignal()
    paused = pyqtSignal()
    resumed = pyqtSignal()

    def __init__(self, input_data):
        super().__init__()
        self.input_data = input_data
        self.computer_control = ComputerControl()
        self.llm_manager = LLMManager(api_key=os.environ.get("ARK_API_KEY"))
        self._pause_mutex = QMutex()
        self._pause_cond = QWaitCondition()
        self._is_paused = False

    def pause(self):
        self._pause_mutex.lock()
        self._is_paused = True
        self._pause_mutex.unlock()
        self.paused.emit()

    def resume(self):
        self._pause_mutex.lock()
        self._is_paused = False
        self._pause_cond.wakeAll()
        self._pause_mutex.unlock()
        self.resumed.emit()

    def check_pause(self):
        self._pause_mutex.lock()
        while self._is_paused:
            self._pause_cond.wait(self._pause_mutex)
        self._pause_mutex.unlock()

    def run(self):
        try:
            chat = self.llm_manager.start_chat(self.input_data)
            while True:
                self.check_pause()
                action = chat.next_action(self.computer_control.take_screenshot())
                if action['action'] == 'finished':
                    break
                self.update_output.emit(f"[AI Thought] {action['thought']}")
                self.update_output.emit(f"[AI Action] {action['action_text']}")
                self.update_output.emit('\n')
                self.computer_control.action(action)
            self.update_output.emit("\n✅ All tasks completed. Thank you for using CyberNexus!")
        except Exception as e:
            self.update_output.emit(f"❌ Error: {str(e)}")
        finally:
            self.finished.emit()

class CyberNexusApp:
    def run(self):
        app = QApplication(sys.argv)
        window = CyberNexusWindow()
        window.show()
        sys.exit(app.exec())
