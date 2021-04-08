import PyQt5

def get_header_label(text):
        header = PyQt5.QtWidgets.QLabel()
        header.setText(text)
        font = PyQt5.QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)  
        font.setPointSize(20)
        header.setFont(font)
        return header

def get_medium_label(text):
        label = PyQt5.QtWidgets.QLabel()
        label.setText(text)
        font = PyQt5.QtGui.QFont()
        label_font_size = 13
        font.setBold(True)
        font.setPointSize(label_font_size)
        label.setFont(font)
        return label