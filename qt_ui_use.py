from PyQt5 import QtWidgets
from qt import Ui_Form
from main_zhilian import *
import sys, os

class myWindow(QtWidgets.QMainWindow, Ui_Form):
    def __init__(self):
        super(myWindow, self).__init__()
        self.setupUi(self)
        self.lineEdit.setText("python")
        self.lineEdit_2.setText("2")
        self.lineEdit_3.setText(os.getcwd())
        self.pushButton.clicked.connect(self.get_input)

    def get_input(self):
        self.setEnabled(False)
        self.filename = self.lineEdit.text()
        self.max_page = int(self.lineEdit_2.text())
        self.save_path = self.lineEdit_3.text()
        self.search_url = self.lineEdit_4.text()
        self.b, self.w = create_browser()
        html = search_key(self.filename, self.b, self.w, self.search_url)
        csv_name = os.path.join(self.save_path, self.filename + '.csv')
        headers = ['职位链接', '职位', '薪资', '基本要求', '职责描述', '公司', '公司规模', '公司链接']
        csv_write(csv_name, headers, html)
        while True:
            time.sleep(1)
            html = next_page(self.b, self.w, self.max_page)
            if not html:
                break
            else:
                csv_write(csv_name, headers, html, False)
        self.b.quit()
        self.setEnabled(True)

app = QtWidgets.QApplication(sys.argv)
myshow = myWindow()
myshow.show()
sys.exit(app.exec_())