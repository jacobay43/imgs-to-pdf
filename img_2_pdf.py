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
    doc_width = 8.27 * dpi 
    doc_height = 11.67 * dpi 

    def __init__(self):
        super().__init__(readOnly=True)
        self.setFixedSize(qtc.QSize(self.doc_width,self.doc_height))

    def set_page_size(self, qrect: qtc.QRect):
        self.doc_width = qrect.width()
        self.doc_height = qrect.height()
        self.setFixedSize(qtc.QSize(self.doc_width,self.doc_height))
        self.document().setPageSize(qtc.QSizeF(self.doc_width,self.doc_height))

    def scale_down_image(self, img_path: str):
        image = qtg.QImage(img_path)
        scaled_image = image.scaled(300,400,qtc.Qt.KeepAspectRatio, qtc.Qt.SmoothTransformation) 
        buffer = qtc.QBuffer()
        buffer.open(qtc.QBuffer.ReadWrite)
        scaled_image.save(buffer, "PNG")
        data = buffer.data()

        return data

    def build_pdf(self, images: list):
        document = qtg.QTextDocument()
        self.setDocument(document)
        document.setPageSize(qtc.QSizeF(self.doc_width, self.doc_height))

        cursor = qtg.QTextCursor(document)
        root = document.rootFrame()
        cursor.setPosition(root.lastPosition())

        block_fmt = qtg.QTextBlockFormat()
        block_fmt.setAlignment(qtg.Qt.AlignCenter)
        cursor.setBlockFormat(block_fmt)

        table_fmt = qtg.QTextTableFormat()
        table_fmt.setAlignment(qtg.Qt.AlignCenter)
        table_fmt.setTopMargin(4)
        table_fmt.setBottomMargin(4)
        table_fmt.setLeftMargin(4)
        table_fmt.setRightMargin(4)
        table_fmt.setCellPadding(5)
        table_fmt.setCellSpacing(2)
        #table_fmt.setBorderBrush(qtg.QColor('white'))
        table_fmt.setBorderCollapse(True)
        table_fmt.setBorder(0)
        table = cursor.insertTable(len(images), 2, table_fmt)
        image_format_fmt = qtg.QTextImageFormat()
        image_format_fmt.setHeight(self.doc_height * 0.45)    
        image_format_fmt.setWidth(self.doc_width * 0.525) 

        for row in range(0,len(images),4):
            if (row >= table.rows()):
                break

            try:                
                data = self.scale_down_image(images[row])
                image_format_fmt.setName("data:image/png;base64," + data.toBase64().data().decode())        
                cursor = table.cellAt(row,0).firstCursorPosition()
                cursor.setBlockFormat(block_fmt)
                cursor.insertImage(image_format_fmt)
            except (IndexError, TypeError):
                break

            try:
                data = self.scale_down_image(images[row+1])
                image_format_fmt.setName("data:image/png;base64," + data.toBase64().data().decode())   
                cursor = table.cellAt(row,1).firstCursorPosition()
                cursor.setBlockFormat(block_fmt)
                cursor.insertImage(image_format_fmt)
            except (IndexError, TypeError):
                break

            if ((row+1) >= table.rows()):
                break
            try:
                data = self.scale_down_image(images[row+2])
                image_format_fmt.setName("data:image/png;base64," + data.toBase64().data().decode())   
                cursor = table.cellAt(row+1,0).firstCursorPosition()
                cursor.setBlockFormat(block_fmt)
                cursor.insertImage(image_format_fmt)
            except (IndexError, KeyError):
                break
            
            try:
                data = self.scale_down_image(images[row+3])
                image_format_fmt.setName("data:image/png;base64," + data.toBase64().data().decode())   
                cursor = table.cellAt(row+1,1).firstCursorPosition()
                cursor.setBlockFormat(block_fmt)
                cursor.insertImage(image_format_fmt)
            except (IndexError, TypeError):
                break


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('img2pdf')

        self.open_folder_btn = qtw.QPushButton('Open Image Folder')
        self.open_folder_btn.clicked.connect(self.select_folder)

         
        self.date = qtw.QDateEdit(date=qtc.QDate.currentDate(),calendarPopup=True,displayFormat='MM/dd/yyyy')
        self.pdf_view = PDFView()
        layout = qtw.QVBoxLayout()
        self.images = []
        self.status_label = qtw.QLabel(f'{len(self.images)} images found. Begin conversion? ')
        self.begin_btn = qtw.QPushButton(text='Begin',clicked=self.convert_to_pdf)
        layout.addWidget(self.open_folder_btn)
        layout.addWidget(self.status_label)
        #layout.addWidget(self.date)
        layout.addWidget(self.begin_btn)

        mw = qtw.QWidget()
        mw.setLayout(layout)
        self.setCentralWidget(mw)

        # Printing
        #print_tb = self.addToolBar('Printing')
        #print_tb.addAction('Configure Printer', self.printer_config)
        #print_tb.addAction('Print Preview', self.print_preview)
        #print_tb.addAction('Print dialog', self.print_dialog)
        #print_tb.addAction('Export PDF', self.export_pdf)

        self.printer = qtps.QPrinter()
        # Configure defaults:
        self.printer.setPageLayout(qtg.QPageLayout(qtg.QPageSize.A4, qtg.QPageLayout.Portrait,qtc.QMarginsF()))
        self.printer.setPageSize(qtg.QPageSize(qtg.QPageSize.Letter))
        #self._update_preview_size()

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

    def select_folder(self):
        folder = qtw.QFileDialog.getExistingDirectory(
            self, "Images Folder", qtc.QDir.homePath(), qtw.QFileDialog.ShowDirsOnly)        
        if folder:
            self.images = list(set([os.path.join(folder,p) for p in os.listdir(folder) if (p.lower().endswith('.png') or p.lower().endswith('.jpeg') or p.lower().endswith('.jpg'))]))
            self.status_label.setText(f'{len(self.images)} images found. Begin conversion? ')

    def export_pdf(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(
            self, "Save to PDF", qtc.QDir.homePath(), "PDF Files (*.pdf)")
        if filename:
            self.printer.setOutputFileName(filename)
            self.printer.setOutputFormat(qtps.QPrinter.PdfFormat)
            self._print_document()

    def convert_to_pdf(self):
        self.setEnabled(False)
        self.pdf_view.build_pdf(self.images)
        self.export_pdf()
        self.setEnabled(True)

if __name__ == '__main__':
    #print(pic_names)
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    app.setStyle('Fusion')
    app.setPalette(make_dark_palette())
    mw.show()
    sys.exit(app.exec())