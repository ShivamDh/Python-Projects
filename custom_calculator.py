from math import *
from tkinter import *
from tkinter import ttk  # @Reimport


class Calculator:
    def get_superscript_number(self, number):
        if len(number) == 1:
            if number == '1':
                return '\u00B9'
            elif number == '2':
                return '\u00B2'
            elif number == '3':
                return '\u00B3'
            elif number == '4':
                return '\u2074'
            elif number == '5':
                return '\u2075'
            elif number == '6':
                return '\u2076'
            elif number == '7':
                return '\u2077'
            elif number == '8':
                return '\u2078'
            elif number == '9':
                return '\u2079'
            else:
                return '\u2070'
        else:
            return self.get_superscript_number(number[:-1]) + self.get_superscript_number(
                self.number[len(self.number) - 1])

    def calc_new_value(self):
        print("in calc_new_value {0}".format(self.last_operator))
        if self.last_operator == '+':
            self.calc_value += float(self.number)
            self.entry.set(self.calc_value)
        elif self.last_operator == '-':
            self.calc_value -= float(self.number)
            self.entry.set(self.calc_value)
        elif self.last_operator == 'multiply':
            self.calc_value *= float(self.number)
            self.entry.set(self.calc_value)
        elif self.last_operator == 'power':
            self.calc_value = pow(self.calc_value, float(self.number))
            self.entry.set(self.calc_value)
        elif self.last_operator == 'nth root':
            self.calc_value = pow(float(self.number), 1/self.calc_value)
            self.entry.set(self.calc_value)
        elif self.last_operator == 'power 10':
            self.calc_value = pow(10, float(self.number))
            self.entry.set(self.calc_value)
        elif self.last_operator == 'log':
            self.calc_value = log(float(self.number), 10)
            self.entry.set(self.calc_value)
        elif self.last_operator == 'power e':
            self.calc_value = exp(float(self.number))
            self.entry.set(self.calc_value)
        elif self.last_operator == 'ln':
            self.calc_value = log(float(self.number), 10)
            self.entry.set(self.calc_value)
        elif self.last_operator == '/':
            if self.number == '0':
                self.entry.set('Error, division by zero')
            else:
                self.calc_value /= float(self.number)
                self.entry.set(self.calc_value)
        elif self.last_operator == 'sqrt':
            try:
                self.calc_value = sqrt(float(self.number))
                self.entry.set(str(self.calc_value))
            except ValueError:
                self.calc_value = ''
                self.entry.set('Error, cannot square root number < 0')
        elif self.number != '':
            self.calc_value = float(self.number)

    def remove_last_operator(self, operation):
        if operation == '10\u207F':
            return self.entry.get()[:-3]
        elif operation == 'e\u207F' or operation == 'nth root' or operation == '\u207F\u221A':
            return self.entry.get()[:-2]
        else:
            return self.entry.get()[:-1]

    def add_operator(self, operator):
        if operator == 'nth root':
            if self.number == '':
                return self.get_superscript_number('1') + '\u221A'
            else:
                return self.remove_last_number() + self.get_superscript_number(self.number) + '\u221A'
        elif operator == 'sqrt':
            return self.entry.get() + '\u221A'
        elif operator == 'multiply':
            return self.entry.get() + '\u00D7'
        elif operator == 'power':
            return self.entry.get() + '^'
        elif operator == 'power 10':
            return self.entry.get() + '10^'
        elif operator == 'power e':
            return self.entry.get() + 'e^'
        else:
            return self.entry.get() + operator

    def remove_last_number(self):
        return self.entry.get()[:-len(self.number)]

    def number_pressed(self, number):
        entry_output = '' if self.equal_clicked else self.entry.get()
        if number == pi:
            current_text = entry_output
            new_text = current_text[:-len(self.number)]
            self.entry.set(new_text + str(pi))
            self.decimal_number = True
            self.number = str(pi)
        else:
            self.number = self.number + str(number)
            self.entry.set(entry_output + str(number))

        if self.last_clicked == 'operator':
            self.last_clicked = 'number'
        print('{0}'.format(self.number))

    def operator_pressed(self, operation):
        if self.last_clicked == 'operator' and not self.equal_clicked:
            self.entry.set(self.remove_last_operator(self.last_operator) + self.add_operator(operation))
        else:
            self.calc_new_value()
            self.entry.set(self.add_operator(operation))
            self.last_clicked = 'operator'
        self.number = ''
        self.last_operator = operation
        self.equal_clicked = False
        print('Operation Pressed {0}'.format(self.last_operator))

    def clear_pressed(self):
        self.calc_value = 0.0
        self.last_operator = ''
        self.number = ''
        self.decimal_number = False
        self.last_clicked = ''
        self.equal_clicked = False
        self.entry.set('')

    def plus_minus(self):
        print('Plus Minus clicked')
        current_text = self.entry.get()
        new_text = current_text[:-len(self.number)]
        self.number = str(-float(self.number))
        self.entry.set(new_text + self.number)

    def dot_pressed(self):
        if not self.decimal_number:
            self.entry.set(self.entry.get() + '.')
            self.decimal_number = True

    def equal_pressed(self):
        calculation_string = self.entry.get()
        self.calc_new_value()
        self.equal_clicked = True
        calculation_string += ' = ' + self.entry.get()
        self.sidebar_history.add_calculation(calculation_string)

    def back_space(self):
        if self.equal_clicked:
            self.clear_pressed()
        elif len(self.entry.get()) > 0:
            self.entry.set(self.entry.get()[:-1])
            if self.last_clicked == 'number':
                self.number = self.number[:-1]
            else:
                self.last_clicked = 'number'
                self.last_operator = ''

    def keyPressed(self, e):
        print ("pressed key")
        print("${0}".format(e.char))

    def __init__(self, root):
        self.entry = StringVar(root, value='')

        self.clear_pressed()

        root.title('Custom Calculator')
        root.resizable(width=False, height=False)

        style = ttk.Style()

        style.configure('TLabel', font='Serif 11', padding=9)

        frame = Frame(root)
        frame.bind("<Key>", self.keyPressed)

        self.entry_output = ttk.Label(frame, width=41, textvariable=self.entry, anchor=W,
                                      background='white', borderwidth=1, relief=RIDGE)

        self.entry_output.grid(row=0, column=1, columnspan=3)

        style.configure('TButton', font='Times 14', padding=5)

        ttk.Button(frame, text='CE', command=self.clear_pressed).grid(row=0, column=0)
        ttk.Button(frame, text='\u232B', command=self.back_space).grid(row=0, column=4)

        ttk.Button(frame, text='\u03C0', command=lambda: self.number_pressed(pi)).grid(row=1, column=0)
        ttk.Button(frame, text='\u221A', command=lambda: self.operator_pressed('sqrt')).grid(row=1, column=1)
        ttk.Button(frame, text='\u207F\u221A', command=lambda: self.operator_pressed('nth root')).grid(row=1, column=2)
        ttk.Button(frame, text='x\u207F', command=lambda: self.operator_pressed('power')).grid(row=1, column=3)
        ttk.Button(frame, text='/', command=lambda: self.operator_pressed('/')).grid(row=1, column=4)

        ttk.Button(frame, text='10\u207F', command=lambda: self.operator_pressed('power 10')).grid(row=2, column=0)
        ttk.Button(frame, text='7', command=lambda: self.number_pressed(7)).grid(row=2, column=1)
        ttk.Button(frame, text='8', command=lambda: self.number_pressed(8)).grid(row=2, column=2)
        ttk.Button(frame, text='9', command=lambda: self.number_pressed(9)).grid(row=2, column=3)
        ttk.Button(frame, text='\u00D7', command=lambda: self.operator_pressed('multiply')).grid(row=2, column=4)

        ttk.Button(frame, text='log', command=lambda: self.operator_pressed('log')).grid(row=3, column=0)
        ttk.Button(frame, text='4', command=lambda: self.number_pressed(4)).grid(row=3, column=1)
        ttk.Button(frame, text='5', command=lambda: self.number_pressed(5)).grid(row=3, column=2)
        ttk.Button(frame, text='6', command=lambda: self.number_pressed(6)).grid(row=3, column=3)
        ttk.Button(frame, text='-', command=lambda: self.operator_pressed('-')).grid(row=3, column=4)

        ttk.Button(frame, text='e\u207F', command=lambda: self.operator_pressed('power e')).grid(row=4, column=0)
        ttk.Button(frame, text='1', command=lambda: self.number_pressed(1)).grid(row=4, column=1)
        ttk.Button(frame, text='2', command=lambda: self.number_pressed(2)).grid(row=4, column=2)
        ttk.Button(frame, text='3', command=lambda: self.number_pressed(3)).grid(row=4, column=3)
        ttk.Button(frame, text='+', command=lambda: self.operator_pressed('+')).grid(row=4, column=4)

        ttk.Button(frame, text='ln', command=lambda: self.operator_pressed('ln')).grid(row=5, column=0)
        ttk.Button(frame, text='\u00B1', command=self.plus_minus).grid(row=5, column=1)
        ttk.Button(frame, text='0', command=lambda: self.number_pressed(0)).grid(row=5, column=2)
        ttk.Button(frame, text='.', command=self.dot_pressed).grid(row=5, column=3)
        ttk.Button(frame, text='=', command=self.equal_pressed).grid(row=5, column=4)

        frame.grid(row=0, column=0)

        label_frame = LabelFrame(root, text="Past Calculations", padx=1, pady=1)
        label_frame.grid(row=0, column=1, sticky=N)

        self.sidebar_history = PastCalculations(label_frame)

class PastCalculations:

    def add_calculation(self, text):
        last_calculation = Label(self.labelFrame, width=25, text=text, background='white',
                                 borderwidth=1, relief=RIDGE, wraplength=170, anchor=W)
        last_calculation.grid(sticky=N)

    def __init__(self, label_frame):
        self.past_calculations = []
        self.labelFrame = label_frame


def sizeSmall():
    print('Change size to small')


def sizeMedium():
    print('Change size to medium')


def sizeLarge():
    print('Change size to large')


def delete_history():
    print('Deleting history of calculator')


def redo_command():
    print('Redo Command')


def changeToRadians():
    print('Changing mode to radians')


def changeToDegrees():
    print('Changing mode to degrees')


def useScientificNotation():
    print('Using Scientific Notation')


def useDecimalNotation():
    print('Using Decimal Notation')


mainGUI = Tk()

mainFrame = Calculator(mainGUI)

topMenu = Menu(mainGUI)
mainGUI.config(menu=topMenu)

fileMenu = Menu(topMenu)
topMenu.add_cascade(label="File", menu=fileMenu)

fileMenu.add_command(label="Size Small", command=sizeSmall)
fileMenu.add_command(label="Size Medium", command=sizeMedium)
fileMenu.add_command(label="Size Large", command=sizeLarge)

fileMenu.add_separator()
fileMenu.add_command(label="Delete History", command=delete_history)
fileMenu.add_command(label="Quit", command=mainGUI.quit)

editMenu = Menu(topMenu)
topMenu.add_cascade(label="Edit", menu=editMenu)

editMenu.add_command(label="Redo", command=redo_command)
editMenu.add_separator()

editMenu.add_command(label="Radian Mode", command=changeToRadians)
editMenu.add_command(label="Degree Mode", command=changeToDegrees)
editMenu.add_separator()

editMenu.add_command(label="Use Scientific Notation", command=useScientificNotation)
editMenu.add_command(label="Use Decimal Notation", command=useDecimalNotation)

mainGUI.mainloop()

# Will add history functionality to easily recall previously used numbers
# Try and see if multiple calculators can be added on 1 GUI for user to control
