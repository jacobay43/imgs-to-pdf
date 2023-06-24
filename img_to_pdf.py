import sys
import os 
import PySide6.QtWidgets as qtw
import PySide6.QtGui as qtg
import PySide6.QtCore as qtc
import PySide6.QtPrintSupport as qtps

def make_dark_palette():
    darkPalette = qtg.QPalette()
    darkPalette.setColor(qtg.QPalette.Window, qtg.QColor(53, 53, 53))
    darkPalette.setColor(qtg.QPalette.WindowText, qtc.Qt.white)
    darkPalette.setColor(qtg.QPalette.Disabled, qtg.QPalette.WindowText, qtg.QColor    (127, 127, 127))
    darkPalette.setColor(qtg.QPalette.Base, qtg.QColor(42, 42, 42))
    darkPalette.setColor(qtg.QPalette.AlternateBase, qtg.QColor(66, 66, 66))
    darkPalette.setColor(qtg.QPalette.ToolTipBase, qtc.Qt.white)
    darkPalette.setColor(qtg.QPalette.ToolTipText, qtc.Qt.white)
    darkPalette.setColor(qtg.QPalette.Text, qtc.Qt.white)
    darkPalette.setColor(qtg.QPalette.Disabled, qtg.QPalette.Text, qtg.QColor(127, 127, 127))
    darkPalette.setColor(qtg.QPalette.Dark, qtg.QColor(35, 35, 35))
    darkPalette.setColor(qtg.QPalette.Shadow, qtg.QColor(20, 20, 20))
    darkPalette.setColor(qtg.QPalette.Button, qtg.QColor(53, 53, 53))
    darkPalette.setColor(qtg.QPalette.ButtonText, qtc.Qt.white)
    darkPalette.setColor(qtg.QPalette.Disabled, qtg.QPalette.ButtonText, qtg.QColor(127, 127, 127))
    darkPalette.setColor(qtg.QPalette.BrightText, qtc.Qt.red)
    darkPalette.setColor(qtg.QPalette.Link, qtg.QColor(42, 130, 218))
    darkPalette.setColor(qtg.QPalette.Highlight, qtg.QColor(42, 130, 218))
    darkPalette.setColor(qtg.QPalette.Disabled, qtg.QPalette.Highlight, qtg.QColor(80, 80, 80))
    darkPalette.setColor(qtg.QPalette.HighlightedText, qtc.Qt.white)
    darkPalette.setColor(qtg.QPalette.Disabled, qtg.QPalette.HighlightedText, qtg.QColor(127, 127, 127))
    return darkPalette

class PDFView(qtw.QTextEdit):
    dpi = 72
    doc_width = 8.5 * dpi 
    doc_height = 11 * dpi 

    def __init__(self):
        super().__init__(readOnly=True)
        self.setFixedSize(qtc.QSize(self.doc_width,self.doc_height))

    def set_page_size(self, qrect: qtc.QRect):
        self.doc_width = qrect.width()
        self.doc_height = qrect.height()
        self.setFixedSize(qtc.QSize(self.doc_width,self.doc_height))
        self.document().setPageSize(qtc.QSizeF(self.doc_width,self.doc_height))

    def build_pdf(self, date: qtc.QDate, images: list):
        document = qtg.QTextDocument()
        self.setDocument(document)
        document.setPageSize(qtc.QSizeF(self.doc_width, self.doc_height))

        cursor = qtg.QTextCursor(document)
        root = document.rootFrame()
        cursor.setPosition(root.lastPosition())

        date_format = qtg.QTextBlockFormat()
        date_format.setAlignment(qtc.Qt.AlignRight)
        date_format.setRightMargin(25)

        date_format = cursor.insertBlock(date_format)
        cursor.insertText(f"{date.month():02d}/{date.day():02d}/{date.year():04d}")

        cursor.setPosition(root.lastPosition())

        for index,image in enumerate(images):            
            image_frame_fmt = qtg.QTextBlockFormat()
            image_frame_fmt.setAlignment(qtc.Qt.AlignHCenter)
            if index % 2 == 0:
                image_frame_fmt.setBottomMargin(50)
            cursor.insertBlock(image_frame_fmt)
            
            image_format_fmt = qtg.QTextImageFormat()
            image_format_fmt.setName(image)
            image_format_fmt.setHeight(self.doc_height / 2.5)
            cursor.insertImage(image_format_fmt)
            
            if index % 2 == 1:
                cursor.movePosition(qtg.QTextCursor.End)
                date_format = qtg.QTextBlockFormat()
                date_format.setAlignment(qtc.Qt.AlignRight)

                date_format.setTopMargin(75)
                date_format.setRightMargin(25)
                date_format = cursor.insertBlock(date_format)
                cursor.insertText(f"{date.month():02d}/{date.day():02d}/{date.year():04d}")
                cursor.movePosition(qtg.QTextCursor.End)
            else:
                cursor.movePosition(qtg.QTextCursor.End)

class MainWindow(qtw.QMainWindow):
    def __init__(self, images: list):
        super().__init__()

        self.setWindowTitle('img2pdf')

        self.images = images
        self.date = qtw.QDateEdit(date=qtc.QDate.currentDate(),calendarPopup=True,displayFormat='MM/dd/yyyy')
        self.pdf_view = PDFView()
        layout = qtw.QVBoxLayout()
        layout.addWidget(qtw.QLabel(f'{len(images)} images found. Begin conversion? '))
        layout.addWidget(self.date)
        layout.addWidget(qtw.QPushButton(text='Begin',clicked=self.convert_to_pdf))

        mw = qtw.QWidget()
        mw.setLayout(layout)
        self.setCentralWidget(mw)

        # Printing
        print_tb = self.addToolBar('Printing')
        print_tb.addAction('Configure Printer', self.printer_config)
        print_tb.addAction('Print Preview', self.print_preview)
        print_tb.addAction('Print dialog', self.print_dialog)
        print_tb.addAction('Export PDF', self.export_pdf)

        self.printer = qtps.QPrinter()
        # Configure defaults:
        self.printer.setPageLayout(qtg.QPageLayout(qtg.QPageSize.A4, qtg.QPageLayout.Portrait,qtc.QMarginsF()))
        self.printer.setPageSize(qtg.QPageSize(qtg.QPageSize.Letter))
        self._update_preview_size()

    def _update_preview_size(self):
        self.pdf_view.set_page_size(
            self.printer.pageRect(qtps.QPrinter.Point))

    def printer_config(self):
        dialog = qtps.QPageSetupDialog(self.printer, self)
        dialog.exec()
        self._update_preview_size()

    def _print_document(self):
        self.pdf_view.document().print_(self.printer)
        #self.printer.newPage()

    def print_dialog(self):
        self._print_document()
        dialog = qtps.QPrintDialog(self.printer, self)
        dialog.exec()
        self._update_preview_size()

    def print_preview(self):
        dialog = qtps.QPrintPreviewDialog(self.printer, self)
        dialog.paintRequested.connect(self._print_document)
        dialog.exec()
        self._update_preview_size()

    def export_pdf(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(
            self, "Save to PDF", qtc.QDir.homePath(), "PDF Files (*.pdf)")
        if filename:
            self.printer.setOutputFileName(filename)
            self.printer.setOutputFormat(qtps.QPrinter.PdfFormat)
            self._print_document()

    def convert_to_pdf(self):
        self.pdf_view.build_pdf(self.date.date(),self.images)
        self.printer_config()

if __name__ == '__main__':
    pic_names = ([p for p in os.listdir(os.curdir) if (p.endswith('.png') or p.endswith('.jpeg') or p.endswith('.jpg'))])

    app = qtw.QApplication(sys.argv)
    mw = MainWindow(pic_names)
    app.setStyle('Fusion')
    app.setPalette(make_dark_palette())
    mw.show()
    sys.exit(app.exec())