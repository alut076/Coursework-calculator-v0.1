import PyQt6
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QGridLayout, QHBoxLayout
from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QSizePolicy
from MyMainWindow import Ui_MainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import matplotlib
import re
import json
import HandlingViewWindow as hvw
import ShuntingPolish as sp


# plt.rcParams['text.usetex'] = True

matplotlib.use('QtAgg')


class LatexLine(FigureCanvas):
    def __init__(self, text = r'$\frac{ab}{cd}$', Halignment='center', text_pos = 0.5):
        self.text = text
        self.mode = 'regular'

        plt.close('all')

        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.ax.axis('off')
        self.text_obj = self.ax.text(text_pos, 0.5, self.text, va='center', ha=Halignment, fontsize=10)

        self.setFixedHeight(40)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))

        



        self.draw()

    def update_drawing(self, Halignment='center', text_pos=0.5):
        self.ax.clear()
        self.ax.axis('off')
        self.text_obj = self.ax.text(text_pos,0.5, self.text, va='center', ha=Halignment, fontsize=10)
        
        self.draw()



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.viewWindow = None
        

        self.scrollAreaWidgetContents.setLayout(self.completedLines)
        self.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.scrollAreaWidgetContents.setMaximumHeight(500)

        

        print("Hi")
        self.currentCanvas = LatexLine()
        self.currentCanvas.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding))
        self.currentCanvas.text = ""

        print("Hi world")


        self.my_verticalLayout.insertWidget(4,self.currentCanvas)
        self.my_verticalLayout.setStretchFactor(self.currentCanvas, 1)
        self.my_verticalLayout.setStretchFactor(self.scrollArea, 4)
        print("hello world")
        self.currentCanvas.draw()
        self.currentCanvas.show()
        



        
        with open('commands.json') as file:
            myfile = json.load(file)
            self.maths_funcs = myfile["functions"]
            self.greeks = myfile["greek"]

        # Buttons
        self.buttons = []
        self.my_lines = []

        for index, key in enumerate(self.maths_funcs.keys()):
            val = str(self.maths_funcs[key])
            x = QPushButton(key)
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
        self.actionView_Data.triggered.connect(self.show_view_window)



    def show_view_window(self):
        if self.viewWindow is None:
            self.viewWindow = hvw.MyViewWindow()
        self.viewWindow.show()

    def enable_editing(self):
        if self.actionEnable_editing.isChecked():
            self.mode = 'edit'
        else:
            self.mode = 'regular'
        print(self.mode)


    def keyPressEvent(self, a0):
        if a0.key() == Qt.Key.Key_Return:
            self.new_line()
        else:
            super().keyPressEvent(a0)


    def new_line(self):
        
        self.my_lines.append(self.currentCanvas.text)
        print(self.my_lines)
        self.my_verticalLayout.removeWidget(self.currentCanvas)
        self.currentCanvas.setParent(None)

        self.currentCanvas = LatexLine(text="")
        self.currentCanvas.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred))

        # self.my_verticalLayout.setParent(None)
        self.my_verticalLayout.insertWidget(4,self.currentCanvas)
        self.my_verticalLayout.setStretchFactor(self.currentCanvas, 1)
        self.my_verticalLayout.setStretchFactor(self.scrollArea, 4)




        for i in reversed(range(self.completedLines.count())):
            item = self.completedLines.itemAt(i)
            correspond_widg = item.widget()
            if correspond_widg is not None:
                self.completedLines.removeWidget(correspond_widg)
                correspond_widg.close()
                correspond_widg.deleteLater()
            elif item.spacerItem():
                self.completedLines.removeItem(item)

        for each in self.my_lines:
            temp_figcan = LatexLine(Halignment='left', text_pos=0)
            temp_figcan.text = each

            temp_figcan.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
            temp_figcan.setFixedHeight(40)
            
            self.completedLines.addWidget(temp_figcan)
            temp_figcan.update_drawing(Halignment='left', text_pos=0)
        
        
        self.completedLines.insertStretch(0)
        self.textbox.setText("")

        
        
        print("hello")
        #self.adjustSize()
        # print(self.scrollArea.verticalScrollBar().maximum())

        # Force a UI update as even though the scrollbar maximum is changing the UI is not updating
        self.scrollAreaWidgetContents.updateGeometry()
        self.scrollAreaWidgetContents.adjustSize()
        QApplication.processEvents()

        x = self.scrollArea.verticalScrollBar().maximum()
        self.scrollArea.verticalScrollBar().setValue(x)

    def rollback_line(self):
        if len(self.my_lines) == 0 or self.completedLines.count() <= 0:
            return
    
        new_canvas_text = self.my_lines.pop()
        
        print(self.my_lines)

        self.currentCanvas.text = new_canvas_text
        self.currentCanvas.update_drawing()


        for i in reversed(range(self.completedLines.count())):
            item = self.completedLines.itemAt(i)
            correspond_widg = item.widget()
            if correspond_widg is not None:
                self.completedLines.removeWidget(correspond_widg)
                correspond_widg.close()
                correspond_widg.deleteLater()
            elif item.spacerItem():
                self.completedLines.removeItem(item)

        for each in self.my_lines:
            temp_figcan = LatexLine(Halignment='left', text_pos=0)
            temp_figcan.text = each

            temp_figcan.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
            temp_figcan.setFixedHeight(40)
            
            self.completedLines.addWidget(temp_figcan)
            temp_figcan.update_drawing(Halignment='left', text_pos=0)
        
        
        self.completedLines.insertStretch(0)
        self.textbox.setText(new_canvas_text[1:-1])

        
        
        print("hello2")
        #self.adjustSize()
        # print(self.scrollArea.verticalScrollBar().maximum())

        # Force a UI update as even though the scrollbar maximum is changing the UI is not updating
        self.scrollAreaWidgetContents.updateGeometry()
        self.scrollAreaWidgetContents.adjustSize()
        QApplication.processEvents()

        x = self.scrollArea.verticalScrollBar().maximum()
        self.scrollArea.verticalScrollBar().setValue(x)        

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
        #global text_obj
        tokens = sp.tokenize(self.currentCanvas.text)
        print(len(tokens))
        print(type(tokens))
        print(tokens)
        try:
            #print(textbox.cursorPosition())
            raw_input = self.textbox.text().strip()
            print(self.currentCanvas.text)
            ajx = [["/",r"\frac{a}{b}"]]
            for i in ajx:
                raw_input = raw_input.replace(i[0],i[1])
            # If the input is not empty add $ signs
            if raw_input:
                self.currentCanvas.text = f"${raw_input}$"
            else:
                self.currentCanvas.text = ""


            self.my_label.setText(self.currentCanvas.text)

            if self.currentCanvas.text_obj:
                try:
                    self.currentCanvas.text_obj.remove()
                except ValueError:
                    print("XYZ")
                    pass #Add code to get rid of this line and rollback previous line



            if self.currentCanvas.text:
                self.currentCanvas.text_obj = self.currentCanvas.ax.text(0.5, 0.5, self.currentCanvas.text, va='center', ha='center', fontsize=10)
            else:
                print("DEF")
                #self.currentCanvas.text_obj = None
                self.rollback_line()

            self.currentCanvas.update_drawing()
        except Exception as e:
            self.currentCanvas.text = ""
            self.my_label.setText(self.currentCanvas.text)
            self.error_label.setText(str(e))
            self.textbox.setStyleSheet("color: red")
            self.error_label.setStyleSheet("color: red")
            if self.currentCanvas.text_obj is not None:
                try:
                    self.currentCanvas.text_obj.remove()
                except ValueError:
                    print("ABC")
                    #Add code to get rid of this line and rollback previous line
                    self.rollback_line()
            
            self.currentCanvas.text_obj = self.currentCanvas.ax.text(0.5, 0.5, self.currentCanvas.text, va='center', ha='center', fontsize=10)
            self.currentCanvas.update_drawing()
            print(e)
        else:
            self.error_label.setText("All good")
            self.error_label.setStyleSheet("color: black")
            self.textbox.setStyleSheet("color: black")

        
app = QApplication(sys.argv)
mainwindow = MainWindow()

mainwindow.show()
app.exec()
