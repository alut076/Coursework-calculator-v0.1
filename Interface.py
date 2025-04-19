import PyQt6
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QLabel, QPushButton, QGridLayout, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sys
import matplotlib
import re
import json
import ShuntingPolish as sp

matplotlib.use('QtAgg')
# plt.rcParams['text.usetex'] = True
app = QApplication(sys.argv)




fig, ax = plt.subplots()
ax.axis('off')
text_obj = ax.text(0.5, 0.5, r'$\frac{ab}{cd}$', va='center', ha='center', fontsize=30)

canvas = FigureCanvas(fig)

with open('commands.json') as file:
    myfile = json.load(file)
    maths_funcs = myfile["functions"]
    greeks = myfile["greek"]




window = QWidget()
window.setWindowTitle("Calculator")
window.setGeometry(950, 650, 800, 600)

global textinput
textinput = ""


def generic(val):
    x = textbox.text()
    try:
        a = textbox.cursorPosition()
        x = x[:a] + val + x[a:]
    except:
        x = x + val
    textbox.setText(x)

def button_click(val):
    def button_clicked():
        generic(val)
    return button_clicked

def new_line():
    pass

def on_text_changed():
    #print("changed")
    global textinput
    global text_obj
    tokens = sp.tokenize(textinput)
    print(len(tokens))
    print(type(tokens))
    print(tokens)
    try:
        #print(textbox.cursorPosition())
        raw_input = textbox.text().strip()
        print(textinput)
        ajx = [["/",r"\frac{a}{b}"]]
        for i in ajx:
            raw_input = raw_input.replace(i[0],i[1])
        # If the input is not empty add $ signs
        if raw_input:
            textinput = f"${raw_input}$"
        else:
            textinput = ""


        label.setText(textinput)

        if text_obj:
            text_obj.remove()


        if textinput:
            text_obj = ax.text(0.5, 0.5, textinput, va='center', ha='center', fontsize=30)
        else:
            text_obj = None

        fig.canvas.draw()
    except Exception as e:
        textinput = ""
        label.setText(textinput)
        error_label.setText(str(e))
        textbox.setStyleSheet("color: red")
        error_label.setStyleSheet("color: red")
        text_obj.remove()
        text_obj = ax.text(0.5, 0.5, textinput, va='center', ha='center', fontsize=30)
        fig.canvas.draw()
        print(e)
    else:
        error_label.setText("All good")
        error_label.setStyleSheet("color: black")
        textbox.setStyleSheet("color: black")

# Grid for buttons
calcbuttons = QGridLayout()

# Buttons
buttons = []


# Create a vertical layout
overall_layout = QVBoxLayout()
menus = QHBoxLayout()
main_layout = QVBoxLayout()

overall_layout.addLayout(menus)
overall_layout.addLayout(main_layout)



# Create a QLineEdit widget
textbox = QLineEdit()
main_layout.addWidget(textbox)

# Create a QLabel to display the current text
label = QLabel('Hello World')
error_label = QLabel('')
main_layout.addWidget(label)
main_layout.addWidget(error_label)
main_layout.addWidget(canvas)
main_layout.addLayout(calcbuttons)

expand_menu = QPushButton(text="Menu")
menus.addWidget(expand_menu)

# Adding the maths function buttons and their corresponding on click functions
for index, key in enumerate(maths_funcs.keys()):
    val = str(maths_funcs[key])
    x = QPushButton(key)
    x.setToolTip(val)
    buttons.append(x)
    del x
    buttons[index].clicked.connect(button_click(val))
    nindex = index % 6
    if index < 6:
        calcbuttons.addWidget(buttons[index], 0, nindex)
    elif index >= 6 and index < 12:
        calcbuttons.addWidget(buttons[index], 1, nindex)
    elif index >= 12 and index < 18:
        calcbuttons.addWidget(buttons[index], 2, nindex)


# Connect the textChanged signal to the on_text_changed function
textbox.textChanged.connect(on_text_changed)


# Set the layout for the main window
window.setLayout(overall_layout)

# Show the window
window.show()

# Run the application
sys.exit(app.exec())