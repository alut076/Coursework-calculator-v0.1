import PyQt6
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QGridLayout, QHBoxLayout
from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QDrag
from MyMainWindow import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import matplotlib
import re
import json
import ShuntingPolish as sp


matplotlib.use('QtAgg')
# plt.rcParams['text.usetex'] = True

class MyCustomButton(QPushButton):
    def mouseMoveEvent(self, a0):
        if a0.buttons() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.MoveAction)
        return super().mouseMoveEvent(a0)



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setupUi(self)
        
        self.textinput = ""

        matplotlib.use('QtAgg')
        self.fig, self.ax = plt.subplots()
        self.ax.axis('off')
        self.text_obj = self.ax.text(0.5, 0.5, r'$\frac{ab}{cd}$', va='center', ha='center', fontsize=30)
        self.canvas = FigureCanvas(self.fig)
        self.my_verticalLayout.insertWidget(3,self.canvas)

        
        with open('commands.json') as file:
            myfile = json.load(file)
            self.maths_funcs = myfile["functions"]
            self.greeks = myfile["greek"]

        # Buttons
        self.buttons = []

        for index, key in enumerate(self.maths_funcs.keys()):
            val = str(self.maths_funcs[key])
            x = MyCustomButton(key)
            x.setToolTip(val)
            self.buttons.append(x)
            del x
            self.buttons[index].clicked.connect(self.button_click(val))
            nindex = index % 6
            if index < 6:
                self.calcbuttons.addWidget(self.buttons[index], 0, nindex)
            elif index >= 6 and index < 12:
                self.calcbuttons.addWidget(self.buttons[index], 1, nindex)
            elif index >= 12 and index < 18:
                self.calcbuttons.addWidget(self.buttons[index], 2, nindex)

        self.textbox.textChanged.connect(self.on_text_changed)
        self.actionEnable_editing.triggered.connect(self.enable_editing)

    def enable_editing(self):
        ...

    def dragEnterEvent(self, a0):
        a0.accept()

    def dropEvent(self, a0):
        cur_position = a0.position()
        selected_widget = a0.source()
        self.calcbuttons.removeWidget(selected_widget)

        for row in range(self.calcbuttons.rowCount()):
            for col in range(self.calcbuttons.columnCount()):
                on_widget = self.calcbuttons.itemAtPosition(row,col).widget()
                if cur_position.x() < on_widget.x() + on_widget.size().width() // 2:
                    break
            else:
                col += 1
            if cur_position.y() < on_widget.y():
                break
        else:
            row += 1

        self.calcbuttons.addWidget(selected_widget,row=row,column=col)
    
    def generic(self,val):
        x = self.textbox.text()
        try:
            a = self.textbox.cursorPosition()
            x = x[:a] + val + x[a:]
        except:
            x = x + val
        self.textbox.setText(x)

    def button_click(self,val):
        def button_clicked():
            self.generic(val)
        return button_clicked
    
    def on_text_changed(self):
        #print("changed")
        global text_obj
        tokens = sp.tokenize(self.textinput)
        print(len(tokens))
        print(type(tokens))
        print(tokens)
        try:
            #print(textbox.cursorPosition())
            raw_input = self.textbox.text().strip()
            print(self.textinput)
            ajx = [["/",r"\frac{a}{b}"]]
            for i in ajx:
                raw_input = raw_input.replace(i[0],i[1])
            # If the input is not empty add $ signs
            if raw_input:
                self.textinput = f"${raw_input}$"
            else:
                self.textinput = ""


            self.my_label.setText(self.textinput)

            if self.text_obj:
                self.text_obj.remove()


            if self.textinput:
                self.text_obj = self.ax.text(0.5, 0.5, self.textinput, va='center', ha='center', fontsize=30)
            else:
                text_obj = None

            self.fig.canvas.draw()
        except Exception as e:
            self.textinput = ""
            self.my_label.setText(self.textinput)
            self.error_label.setText(str(e))
            self.textbox.setStyleSheet("color: red")
            self.error_label.setStyleSheet("color: red")
            self.text_obj.remove()
            self.text_obj = self.ax.text(0.5, 0.5, self.textinput, va='center', ha='center', fontsize=30)
            self.fig.canvas.draw()
            print(e)
        else:
            self.error_label.setText("All good")
            self.error_label.setStyleSheet("color: black")
            self.textbox.setStyleSheet("color: black")

        
app = QApplication(sys.argv)
mainwindow = MainWindow()

mainwindow.show()
app.exec()