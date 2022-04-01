import aqt.qt

def get_header_label(text):
        header = aqt.qt.QLabel()
        header.setText(text)
        font = aqt.qt.QFont()
        font.setBold(True)
        font.setWeight(75)  
        font.setPointSize(20)
        header.setFont(font)
        return header

def get_medium_label(text):
        label = aqt.qt.QLabel()
        label.setText(text)
        font = aqt.qt.QFont()
        label_font_size = 13
        font.setBold(True)
        font.setPointSize(label_font_size)
        label.setFont(font)
        return label

def get_large_button_font():
        font2 = aqt.qt.QFont()
        font2.setPointSize(14)
        return font2        
