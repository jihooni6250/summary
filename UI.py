import sys
import asyncio
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QTextEdit, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
from extractor import extract_pdf_content
from text_processing import clean_text, analyze_key_sections
from summarizer import generate_summary

class PDFProcessorThread(QThread):
    finished = pyqtSignal(str, str)
    error = pyqtSignal(str)

    def __init__(self, pdf_path, emphasis=None, exclude=None):
        super().__init__()
        self.pdf_path = pdf_path
        self.emphasis = emphasis
        self.exclude = exclude

    def run(self):
        try:
            # PDF 데이터 추출
            text, title, ocr_text = extract_pdf_content(self.pdf_path)

            # 텍스트 처리 및 키워드 분석
            cleaned_text = clean_text(text + " " + ocr_text)
            keywords = analyze_key_sections(cleaned_text)

            # 요약 생성
            summary = asyncio.run(generate_summary(
                cleaned_text, title, ocr_text, keywords,
                emphasis=self.emphasis, exclude=self.exclude
            ))

            self.finished.emit(title, summary)
        except Exception as e:
            self.error.emit(str(e))


# class PDFProcessorThread(QThread):
#     finished = pyqtSignal(str, str)  # 제목과 요약 결과를 반환
#     error = pyqtSignal(str)          # 오류 메시지를 반환
#
#     def __init__(self, pdf_path):
#         super().__init__()
#         self.pdf_path = pdf_path
#
#     def run(self):
#         try:
#             # PDF 데이터 추출
#             text, title, ocr_text = extract_pdf_content(self.pdf_path)
#
#             # 텍스트 처리 및 키워드 분석
#             cleaned_text = clean_text(text + " " + ocr_text)
#             keywords = analyze_key_sections(cleaned_text)
#
#             # 요약 생성 (비동기 호출)
#             summary = asyncio.run(generate_summary(cleaned_text, title, ocr_text, keywords))
#
#             # 결과 반환
#             self.finished.emit(title, summary)
#         except Exception as e:
#             self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PDF Processor and Summary Viewer")
        self.setGeometry(200, 200, 900, 700)

        # Layout 설정
        layout = QVBoxLayout()

        # 텍스트 요약 표시 영역
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlaceholderText("PDF 요약 결과가 여기에 표시됩니다.")
        layout.addWidget(self.summary_text)

        # 버튼: PDF 파일 로드
        self.load_button = QPushButton("Load PDF")
        self.load_button.clicked.connect(self.load_pdf)
        layout.addWidget(self.load_button)

        # Main Layout 설정
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_pdf(self):
        """PDF 파일을 선택하고 처리"""
        options = QFileDialog.Options()
        pdf_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf);;All Files (*)",
                                                  options=options)

        if pdf_path:
            self.process_pdf(pdf_path)

    def process_pdf(self, pdf_path):
        """PDF를 처리하고 요약 결과를 UI에 표시"""
        self.summary_text.clear()

        # 사용자 입력을 통해 강조/제외 주제를 설정
        emphasis = ["도핑 농도"]
        exclude = ["실험 방법"]

        # 스레드 생성 및 연결
        self.thread = PDFProcessorThread(pdf_path, emphasis=emphasis, exclude=exclude)
        self.thread.finished.connect(self.display_summary)
        self.thread.error.connect(self.display_error)
        self.thread.start()

    # def process_pdf(self, pdf_path):
    #     """PDF를 처리하고 요약 결과를 UI에 표시"""
    #     self.summary_text.clear()
    #
    #     # 스레드 생성 및 연결
    #     self.thread = PDFProcessorThread(pdf_path)
    #     self.thread.finished.connect(self.display_summary)
    #     self.thread.error.connect(self.display_error)
    #     self.thread.start()

    def display_summary(self, title, summary):
        """요약 결과를 UI에 표시"""
        self.summary_text.setPlainText(f"Title: {title}\n\nSummary:\n{summary}")

    def display_error(self, error_message):
        """오류 메시지를 UI에 표시"""
        self.summary_text.setPlainText(f"Error processing PDF: {error_message}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
