import PyQt6
import matplotlib.pyplot as plt
from PyQt6 import QtCore
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QGridLayout, QHBoxLayout, QTableWidgetItem, QTableWidget, QDialog, QDialogButtonBox
from PyQt6.QtCore import QMimeData, Qt
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QSizePolicy
from MyViewWindow import Ui_ViewWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import matplotlib
import re
import json
import ShuntingPolish as sp


class MyDialog(QDialog):
    """
    Custom dialog box when user tries to close the window
    """
    def __init__(self):
        super().__init__()

        # Specifies the buttons
        op_buttons = QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Discard | QDialogButtonBox.StandardButton.Cancel

        self.buttonBox = QDialogButtonBox(op_buttons)

        # Handles any clicks
        self.buttonBox.clicked.connect(self.onClickFunction)


        my_layout = QVBoxLayout()
        message = QLabel("Do you want to save changes?")
        my_layout.addWidget(message)
        my_layout.addWidget(self.buttonBox)
        self.setLayout(my_layout)

    
    def onClickFunction(self,button):
        print("Response returned from user")

        buttonpressed = self.buttonBox.standardButton(button)

        # Based on what button was pressed, different numbers are returned
        # 1 for Save, 2 for Discard, 3 for Cancel
        if buttonpressed == QDialogButtonBox.StandardButton.Save:
            self.done(1)
        elif buttonpressed == QDialogButtonBox.StandardButton.Discard:
            self.done(2)
        elif buttonpressed == QDialogButtonBox.StandardButton.Cancel:
            self.done(3)




class MyViewWindow(QMainWindow, Ui_ViewWindow):
    """
    Window for viewing and editing table data from a JSON file
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        with open('commands2.json', encoding='utf-8') as file:
            self.myfile = json.load(file)
            self.TableNamesComboBox.addItems(self.myfile.keys())

        self.update_table()

        # Connects functions to the relevant signals
        self.TableNamesComboBox.currentTextChanged.connect(self.update_table)
        self.addRowpushButton.clicked.connect(self.add_row)
        self.deleteRowpushButton.clicked.connect(self.remove_row)
        self.SavepushButton.clicked.connect(self.save_table_data)




    def update_table(self):
        """
        Update the table widget to display data for the currently selected table
        """
        # print("Hello World")
        self.numCols = 2
        self.numRows = len(self.myfile[self.TableNamesComboBox.currentText()])
        #print(self.numRows)

        # Hides buttons if the table is not defined_vars
        if self.TableNamesComboBox.currentText() == "defined_vars":
            self.addRowpushButton.setHidden(False)
            self.deleteRowpushButton.setHidden(False)
            self.SavepushButton.setHidden(False)
        else:
            self.addRowpushButton.setHidden(True)
            self.deleteRowpushButton.setHidden(True)
            self.SavepushButton.setHidden(True)


        # Gets the data from the JSON file into the table
        self.tableWidget.setRowCount(self.numRows)
        self.tableWidget.setColumnCount(self.numCols)
        self.numRows = 0
        for i, (each_key, each_value) in enumerate(self.myfile[self.TableNamesComboBox.currentText()].items()):
            x = each_value
            #print(f"each_key is {each_key}")
            #print(each_key)
            if type(x) is dict:
                # For the defined vars table uses headers
                self.numCols = 4
                self.tableWidget.setColumnCount(self.numCols)
                self.tableWidget.setHorizontalHeaderLabels(["Name", "Symbol", "Value", "Unit"])
                
                self.tableWidget.setRowCount(self.numRows + 1)
                #print(f"x is {x}")

                for each_name, eachs_details in x.items():
                    #print(f"each_name is {each_name}")
                    #print(f"eachs_details is {eachs_details}")
                    self.tableWidget.setRowCount(self.numRows + 1)
                    #print(f"Name:{each_name} \n{eachs_details}")

                    a = QTableWidgetItem(each_name)
                    b = QTableWidgetItem(eachs_details['symbol'])
                    c = QTableWidgetItem(eachs_details['value'])
                    d = QTableWidgetItem(eachs_details['unit'])
                    
                    if each_key == "user_defined_consts":
                        #print("Not editable")
                        pass
                    else:
                        a.setFlags(a.flags() ^ Qt.ItemFlag.ItemIsEditable)
                        b.setFlags(b.flags() ^ Qt.ItemFlag.ItemIsEditable)
                        c.setFlags(c.flags() ^ Qt.ItemFlag.ItemIsEditable)
                        d.setFlags(d.flags() ^ Qt.ItemFlag.ItemIsEditable)

                    self.tableWidget.setItem(self.numRows, 0, a)
                    self.tableWidget.setItem(self.numRows, 1, b)
                    self.tableWidget.setItem(self.numRows, 2, c)
                    self.tableWidget.setItem(self.numRows, 3, d)
                    self.numRows += 1

            else:
                # For simple key value pairs
                if self.numRows == 0:
                    self.numRows = len(self.myfile[self.TableNamesComboBox.currentText()])
                item_key = QTableWidgetItem(each_key)
                item_val = QTableWidgetItem(x)
                
                item_key.setFlags(item_key.flags() ^ Qt.ItemFlag.ItemIsEditable)
                item_val.setFlags(item_val.flags() ^ Qt.ItemFlag.ItemIsEditable)

                self.tableWidget.setItem(i, 0, item_key)
                self.tableWidget.setItem(i, 1, item_val)




    def add_row(self):
        """
        Adds a new row in the table which the user can edit
        """
        self.tableWidget.setRowCount(self.numRows+1)
        a = QTableWidgetItem("")
        b = QTableWidgetItem("")
        c = QTableWidgetItem("")
        d = QTableWidgetItem("")
        self.tableWidget.setItem(self.numRows, 0, a)
        self.tableWidget.setItem(self.numRows, 1, b)
        self.tableWidget.setItem(self.numRows, 2, c)
        self.tableWidget.setItem(self.numRows, 3, d)
        self.numRows += 1
        self.tableWidget.scrollToBottom()

    def remove_row(self):
        """
        Removes last editable row from table
        """
        x = self.tableWidget.item(self.numRows-1,0)
        if Qt.ItemFlag.ItemIsEditable in x.flags():
            self.tableWidget.removeRow(self.numRows-1)
            self.numRows -= 1
        self.tableWidget.scrollToBottom()

    def save_table_data(self):
        """
        Saves the data in the editable section to the JSON file
        """
        user_consts = {}
        for i in range(self.numRows):
            x = self.tableWidget.item(i,0)
            if Qt.ItemFlag.ItemIsEditable in x.flags():
                const_name = self.tableWidget.item(i,0).text()
                const_symbol = self.tableWidget.item(i,1).text()
                const_value = self.tableWidget.item(i,2).text()
                const_unit = self.tableWidget.item(i,3).text()
                user_consts[const_name] = {"symbol": const_symbol, "value": const_value, "unit": const_unit}

        with open('commands2.json', 'r', encoding='utf-8') as file:
            my_data = json.load(file)
        
        with open('commands2.json', 'w', encoding='utf-8') as file:
            my_data["defined_vars"]["user_defined_consts"] = user_consts
            json.dump(my_data, file, indent=4)

    def closeEvent(self, a0):
        """
        Prompts user to save/discard/cancel when closing the window if editing variables
        """
        if self.TableNamesComboBox.currentText() == "defined_vars":
            self.DiaCheckSave = MyDialog()
            buttonPressed = self.DiaCheckSave.exec()

            if buttonPressed == 1: # 1 is save
                self.save_table_data()
                a0.accept()
            elif buttonPressed == 2: # 2 is discard
                a0.accept()
            elif buttonPressed == 3: # 3 is cancel
                a0.ignore()

        else:
            return super().closeEvent(a0)

    def checkSave(self):
        pass




    







if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewwindow = MyViewWindow()

    viewwindow.show()
    app.exec()



