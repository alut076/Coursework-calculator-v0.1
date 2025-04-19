import PyQt6
import PyQt6.QtCore
import PyQt6.QtGui
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
import TermClass as tc
import TreeHandling as th


# plt.rcParams['text.usetex'] = True

#Allows the matplotlib to connect to PyQt
matplotlib.use('QtAgg')


def latexify(expr: str) -> str:
    # wrap any sequence of two or more digits (or letters) after ^ in braces
    return re.sub(
        r'\^([0-9]+)',
        lambda m: '^{%s}' % m.group(1),
        expr
    )


class LatexLine(FigureCanvas):
    """
    A Class for the FigureCanvas instance specifically for displaying text in a LaTeX format
    """
    def __init__(self, text = r'$\frac{ab}{cd}$', Halignment='center', text_pos=0.5, border_thickness=0,border_color='white', textcol='black'):
        #Set up attributes for the FigureCanvas
        self.text = text
        self.border_thickness = border_thickness
        self.border_color = border_color
        self.textcol = textcol
        self.mode = 'regular'

        plt.close('all')

        #Makes a plot
        self.fig, self.ax = plt.subplots()
        
        #Inherits from FigureCanvas class
        super().__init__(self.fig)

        #Sets the border of the FigureCanvas
        self.fig.set_edgecolor(border_color)
        self.fig.set_linewidth(border_thickness)
        
        #Sets the attributes for the text object and turns axis off
        self.ax.axis('off')
        self.text_obj = self.ax.text(text_pos, 0.5, self.text, va='center', ha=Halignment, fontsize=10, color=self.textcol)

        #Sets size
        self.setFixedHeight(40)

        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))

        



        self.draw()

    def update_drawing(self, Halignment='center', text_pos=0.5):
        #Updates drawing in the case that any attributes have been changed
        self.ax.clear()
        self.ax.axis('off')
        self.text_obj = self.ax.text(text_pos,0.5, self.text, va='center', ha=Halignment, fontsize=10, color=self.textcol)
        self.fig.set_edgecolor(self.border_color)
        self.fig.set_linewidth(self.border_thickness)
        
        self.draw()







class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        #Sets up UI
        super().__init__()
        self.setupUi(self)


        self.viewWindow = None
        self.newLineJustCreated = False
        #Ensures that the error label does not increase size of screen unnecessarily
        self.error_label.setWordWrap(True)

        #Sets current item, widget and flag
        self.currentItemIndex = None
        self.widgBeingEdited = None
        self.widgBeingEditedText = None
        self.CompletedLinesBeingEdited = False

        # Temporary store for variables initialised by the user in the user interface
        self.variables = {}

        self.textbox.installEventFilter(self)

        
        #Sets layout and size of the scroll area
        self.scrollAreaWidgetContents.setLayout(self.horizontalLayout_2)
        self.scrollAreaWidgetContents.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.scrollAreaWidgetContents.setMaximumHeight(500)

        

        # Initialises the line at bottom separate of the completedLines layout
        self.mainCanvas = LatexLine(border_thickness=1,border_color='darkslategray')
        self.mainCanvas.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding))
        self.mainCanvas.text = ""


        # Sets up initial user interface and updates the current canvas
        self.my_verticalLayout.insertWidget(4,self.mainCanvas)
        self.my_verticalLayout.setStretchFactor(self.mainCanvas, 1)
        self.my_verticalLayout.setStretchFactor(self.scrollArea, 4)
        print("Program Initialised")
        self.currentCanvas = self.mainCanvas
        self.currentCanvas.draw()
        self.currentCanvas.show()
        



        # Gets latex values from JSON dictionary
        with open('commands.json') as file:
            myfile = json.load(file)
            self.maths_funcs = myfile["functions"]
            self.greeks = myfile["greek"]

        # Buttons for grid
        self.buttons = []
        self.my_lines = [] #list for user text in the completedlines layout
        self.ans_lines = [] # list for answer text in the answerLines layout

        #Sets up grid of buttons
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

        #Adds the Clear Line and Clear All buttons 
        self.clearLineBtn = QPushButton(text="Clear Line")
        self.calcbuttons.addWidget(self.clearLineBtn,3,0)

        self.clearAllBtn = QPushButton(text="Clear All")
        self.calcbuttons.addWidget(self.clearAllBtn,3,1)
        

        #Adds the signals for relevant key and button presses
        self.textbox.textChanged.connect(self.on_text_changed)
        self.actionEnable_editing.triggered.connect(self.enable_editing)
        self.actionView_Data.triggered.connect(self.show_view_window)
        
        self.clearLineBtn.clicked.connect(self.clear_line)
        self.clearAllBtn.clicked.connect(self.clearAll)

    # Overrides backspace functionality
    def eventFilter(self, a0, a1):
        if a0 == self.textbox and a1.type() == PyQt6.QtCore.QEvent.Type.KeyPress:
            if a1.key() == Qt.Key.Key_Backspace and self.textbox.text() == "":
                #print("This works")
                self.rollback_line()
                return True

        return super().eventFilter(a0, a1)
    
    def clear_line(self):
        '''
        Clears the current line
        '''
        self.textbox.setText("")


    def clearAll(self):
        """
        Clears all of the LatexLine instances in the completedLines and answerLines
        """
        if self.completedLines.count() != 0:
            for i in reversed(range(self.completedLines.count())):
                #Clears the completedLines
                item = self.completedLines.itemAt(i)
                correspond_widg = item.widget()
                if correspond_widg is not None:
                    self.completedLines.removeWidget(correspond_widg)
                    correspond_widg.close()
                    correspond_widg.deleteLater()
                elif item.spacerItem():
                    self.completedLines.removeItem(item)

                #Clears answer lines
                ansitem = self.answerLines.itemAt(i)
                ans_widg = ansitem.widget()

                if ans_widg is not None:
                    self.answerLines.removeWidget(ans_widg)
                    ans_widg.close()
                    ans_widg.deleteLater()
                elif ansitem.spacerItem():
                    self.answerLines.removeItem(ansitem)

            self.my_lines.clear()
            self.ans_lines.clear()


    def show_view_window(self):
        """
        Sets up the view window and shows it
        """
        if self.viewWindow is None:
            self.viewWindow = hvw.MyViewWindow()
        self.viewWindow.show()

    def enable_editing(self):
        """
        Base function for enabling editing, this was never implemented
        """
        if self.actionEnable_editing.isChecked():
            self.mode = 'edit'
        else:
            self.mode = 'regular'
        print(self.mode)




    def keyPressEvent(self, a0):
        # Assigns the functions to relevant key presses
        if a0.key() == Qt.Key.Key_Return:
            self.new_line()
        elif a0.key() == Qt.Key.Key_Up:
            self.move_up()
        elif a0.key() == Qt.Key.Key_Down:
            self.move_down()
        else:
            super().keyPressEvent(a0)


    def move_up(self):
        """
        Moves to line above
        """
        if self.currentItemIndex is None:
            self.currentItemIndex = len(self.my_lines) - 1
        elif self.currentItemIndex > 0:
            self.currentItemIndex -= 1
        else:
            return  # Already at the top
        if self.currentItemIndex >= 0:
            # print(f"currentItemIndex:{self.currentItemIndex}")
            #print(f"completedLines count: {self.completedLines.count()}")
            if self.currentItemIndex == self.completedLines.count()-1: #The -1 is needed to account for 0 based index
                self.new_line()
                self.currentItemIndex -= 1

            self.moving_lines()

    def move_down(self):
        """
        Moves to line below
        """
        if self.currentItemIndex is None:
            self.currentItemIndex = 0
        elif self.currentItemIndex < len(self.my_lines) - 1:
            self.currentItemIndex += 1
        elif self.currentItemIndex == len(self.my_lines)-1:
            self.reset_editing_state()
            return
        else:
            return  # Already at the bottom
        if self.currentItemIndex < self.completedLines.count()-1:
            # print(f"currentItemIndex:{self.currentItemIndex}")
            #print(f"completedLines count: {self.completedLines.count()}")

            self.moving_lines()
        
            
            

    def moving_lines(self):
        """
        General function for ensuring the current line is highlighted
        And for updating which is the current item etc.
        """
        self.widgBeingEdited = self.completedLines.itemAt(self.currentItemIndex+1).widget()
        self.CompletedLinesBeingEdited = True
        self.currentCanvas = self.widgBeingEdited

        currentItemTXT = self.my_lines[self.currentItemIndex]
        self.widgBeingEditedText = currentItemTXT

        self.textbox.setText(currentItemTXT[1:-1])
        for i in range(self.completedLines.count()):
            item = self.completedLines.itemAt(i)
            correspond_widg = item.widget()
            if correspond_widg is not None:
                if i == self.currentItemIndex+1:
                    correspond_widg.border_thickness = 1
                    correspond_widg.border_color = 'darkslategray'
                else:
                    correspond_widg.border_thickness = 0
                    correspond_widg.border_color = 'white'
                correspond_widg.update_drawing(Halignment='left', text_pos=0)

    def reset_editing_state(self):
        self.newLineJustCreated = True
        self.widgBeingEdited = None
        self.widgBeingEditedText = None
        self.CompletedLinesBeingEdited = False
        self.textbox.setText("")
        self.currentItemIndex = len(self.my_lines)

        self.mainCanvas.text = ""
        self.currentCanvas = self.mainCanvas
        
        self.reRenderCompletedLines()

            

    def reRenderCompletedLines(self):
        """
        Deletes and redraws the LatexLine instances within the completedLines and answerLines
        """
        print(f"my_lines: {self.my_lines}")
        #Empties the answer lines so they can be recalculated
        self.ans_lines = []

        # Re calculates the answer lines
        for each in self.my_lines:
            try:
                my_ans = th.build_and_simplify(each[1:-1])
                my_ans = latexify(my_ans)
                my_ans = f"${my_ans}$"
            except Exception as e:
                # If there is an error, error is put as the answer text
                print(f"Error: {e}")
                my_ans = f"Error"
            self.ans_lines.append(my_ans)

        print(f"ans_lines: {self.ans_lines}")

        #Deletes the canvases in the completedLines and answerLines layouts
        for i in reversed(range(self.completedLines.count())):
            # Deletes canvases in completedLines
            item = self.completedLines.itemAt(i)
            correspond_widg = item.widget()

            if correspond_widg is not None:
                self.completedLines.removeWidget(correspond_widg)
                correspond_widg.close()
                correspond_widg.deleteLater()
            elif item.spacerItem():
                self.completedLines.removeItem(item)


            # Deletes the canvases in the answerLines layout
            ansitem = self.answerLines.itemAt(i)
            ans_widg = ansitem.widget()

            if ans_widg is not None:
                self.answerLines.removeWidget(ans_widg)
                ans_widg.close()
                ans_widg.deleteLater()
            elif ansitem.spacerItem():
                self.answerLines.removeItem(ansitem)


        # Re-instantiates and draws the canvases based off the mylines and answerlines lists
        # This is so that everything can be updated successfully
        for i, each in enumerate(self.my_lines):
            temp_figcan = LatexLine(Halignment='left', text_pos=0)
            temp_figcan.text = each

            ans_figcan = LatexLine(Halignment='right', text_pos=1, textcol='darkgreen')
            ans_figcan.text = self.ans_lines[i]

            temp_figcan.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
            temp_figcan.setFixedHeight(40)
            
            ans_figcan.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed))
            ans_figcan.setFixedHeight(40)
            
            self.completedLines.addWidget(temp_figcan)
            self.answerLines.addWidget(ans_figcan)

            temp_figcan.update_drawing(Halignment='left', text_pos=0)
            ans_figcan.update_drawing(Halignment='right', text_pos=1)

            
        # Re inserts spacing widget
        self.answerLines.insertStretch(0)        
        self.completedLines.insertStretch(0)

    def change_line(self):
        pass

    def new_line(self):
        """
        Instantiates a new line in the completedLines canvas
        """

        # Checks if one of the completedLines was being edited
        # If so, the editing state is reset and the user is brought back down to the main canvas
        if self.CompletedLinesBeingEdited == True:
            self.reset_editing_state()
            return
        
        self.my_lines.append(self.currentCanvas.text)
        print(f"self.my_lines: {self.my_lines}")

        self.currentItemIndex = len(self.my_lines)

        self.mainCanvas.text = ""
        self.currentCanvas = self.mainCanvas

        self.reRenderCompletedLines()
        self.textbox.setText("")


        # Force a UI update as even though the scrollbar maximum is changing the UI is not updating
        self.scrollAreaWidgetContents.updateGeometry()
        self.scrollAreaWidgetContents.adjustSize()
        QApplication.processEvents()

        x = self.scrollArea.verticalScrollBar().maximum()
        self.scrollArea.verticalScrollBar().setValue(x)



    def rollback_line(self):
        """
        In the case that the line the user is editing in the completedLines layout is empty
        this function deletes the current line in the completedLines layout
        """
        #Ensures the function doesn't work 
        # if the user is either on the bottom canvas 
        # or there are no lines in the completedLines layout
        if len(self.my_lines) == 0 or self.completedLines.count() <= 0:
            return
        
        # Ensures that the function only works if the CompletedLines are being edited
        # Deletes the current line and resets if the user is on the last line in the completedLines layout
        if self.CompletedLinesBeingEdited == True:
            print("deleting while editing")
            self.my_lines.pop(self.currentItemIndex)
            self.reRenderCompletedLines()
            print(f"when crashing currentItemIndex: {self.currentItemIndex}")
            print(f"when crashing completedLines count: {self.completedLines.count()}")
            if self.currentItemIndex < self.completedLines.count() - 1:
                self.moving_lines()
            else:
                self.reset_editing_state()
                return
            return
    
        # Updates and re renders

        new_canvas_text = self.my_lines.pop()
        
        print(f"self.my_lines:{self.my_lines}")

        self.currentCanvas.text = new_canvas_text
        self.currentCanvas.update_drawing()


        self.reRenderCompletedLines()
        self.textbox.setText(new_canvas_text[1:-1])

        
        
        #print("hello2")
        #self.adjustSize()
        # print(self.scrollArea.verticalScrollBar().maximum())

        # Force a UI update as even though the scrollbar maximum is changing the UI is not updating
        self.scrollAreaWidgetContents.updateGeometry()
        self.scrollAreaWidgetContents.adjustSize()
        QApplication.processEvents()

        x = self.scrollArea.verticalScrollBar().maximum()
        self.scrollArea.verticalScrollBar().setValue(x)        


    def generic(self,val):
        # Based on parameters passed in
        # updates text in textbox on the position the user's cursor is at
        x = self.textbox.text()
        try:
            a = self.textbox.cursorPosition()
            x = x[:a] + val + x[a:]
        except:
            x = x + val
        self.textbox.setText(x)


    def button_click(self,val):
        # Generates a corresponding function to map to each button
        def button_clicked():
            self.generic(val)
        return button_clicked


    def on_text_changed(self):
        """
        Carries out all processing for updating everything in real time
        Mainly updates the relevant figure canvas depending on the text inside the textbox
        By converting the text inside the textbox to its LaTeX formatted equivalent
        """

        try:

            raw_input = self.textbox.text().strip()

            #This following commented code could be used to implement typesetting
            # Although will be made to be more complicated especially for fractions
            # ajx = [["/",r"\frac{a}{b}"]]
            # for i in ajx:
            #     raw_input = raw_input.replace(i[0],i[1])


            # If the input is not empty add $ signs
            if raw_input:
                self.currentCanvas.text = f"${raw_input}$"
            else:
                self.currentCanvas.text = ""


            self.my_label.setText(self.currentCanvas.text)

            # This part is for the working on lines in the completedLines layout
            # and to have them update in real time when working on them
            if self.CompletedLinesBeingEdited == True:
                self.my_lines[self.currentItemIndex] = self.currentCanvas.text


            if self.currentCanvas.text_obj:
                try:
                    self.currentCanvas.text_obj.remove()
                except ValueError:
                    pass #Add code to get rid of this line and rollback previous line



            if self.currentCanvas.text:
                self.currentCanvas.text_obj = self.currentCanvas.ax.text(0.5, 0.5, self.currentCanvas.text, va='center', ha='center', fontsize=10)
            else:
                pass

            self.currentCanvas.update_drawing()
        except Exception as e:
            # In case there is an error the error is caught and displayed in the label
            self.currentCanvas.text = ""
            self.my_label.setText(self.currentCanvas.text)
            self.error_label.setText(str(e))
            self.textbox.setStyleSheet("color: red") # For any error the text in the textbox is made red
            self.error_label.setStyleSheet("color: red") # For any error the text in the error label is made red
            
            if self.currentCanvas.text_obj is not None:
                try:
                    self.currentCanvas.text_obj.remove()
                except ValueError:
                    pass

            # Renders the text in its latex format in the currentCanvas
            self.currentCanvas.text_obj = self.currentCanvas.ax.text(0.5, 0.5, self.currentCanvas.text, va='center', ha='center', fontsize=10)
            self.currentCanvas.update_drawing()
            print(e)
        else:
            # If there is no issue the text in the error label is black and says All good
            self.error_label.setText("All good")
            self.error_label.setStyleSheet("color: black")
            self.textbox.setStyleSheet("color: black")

        if self.newLineJustCreated == True:
            self.newLineJustCreated = False
        print(f"my_lines: {self.my_lines}")



# Starts up the program
app = QApplication(sys.argv)
mainwindow = MainWindow()

mainwindow.show()
app.exec()
