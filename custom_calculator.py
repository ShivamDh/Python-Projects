from tkinter import *
from tkinter import ttk  # @Reimport
from math import *

class Calculator:
    
    def calc_new_value(self):
        pass
    
    def remove_last_operator(self, operation):
        if operation == '10\u207F':
            return self.entry.get()[:-3]
        elif operation == 'e\u207F' or operation == 'x\u207F' or operation == '\u207F\u221A':
            return self.entry.get()[:-2]
        else:
            return self.entry.get()[:-1]
            
    
    def number_pressed(self, number):
        if number == pi:
            currentText = self.entry.get()
            newText = currentText[:-float(len(self.number))]
            self.entry.set(newText + str(pi))
            self.decimal_number = True
            self.number = str(pi)
        else:
            self.number = self.number + str(number)
            self.entry.set(self.entry.get() + str(number))
        
        if self.last_clicked == 'operator':
            self.last_clicked = 'number'
            self.last_operator= ''
        print('{0}'.format(self.number))
        
    def operator_pressed(self, operation):
        self.number = ''
        self.last_operator = operation
        if self.last_clicked == 'operator':
            self.entry.set(self.remove_last_operator(operation) + operation)
        else:
            self.calc_new_value()
            self.entry.set(self.entry.get() + operation)
            self.last_clicked = 'operator'
#         print('Operation Pressed {0}'.format(str(operation)))
        
    def clear_pressed(self):
        self.entry.set('')
        self.decimal_number = False
        
    def plus_minus(self):
        print('Plus Minus clicked')
        currentText = self.entry.get()
        newText = currentText[:-len(self.number)]
        self.number = str(-float(self.number))
        self.entry.set(newText + self.number)
    
    def dotPressed(self):
        if not self.decimal_number:
            self.entry.set(self.entry.get() + '.')
            self.decimal_number = True
            
    def equal_pressed(self):
        print('Equal Pressed')
    
    def back_space(self):
        if len(self.entry.get()) > 0:
            self.entry.set(self.entry.get()[:-1])
    
    def __init__(self, root):
        self.entry = StringVar(root, value='')
        
        self.calc_value: 0.0
        self.last_operator = ''
        self.number = ''
        self.decimal_number = False
        self.last_clicked=''
        
        root.title('Custom Calculator')
        root.resizable(width=False, height=False)
        
        style=ttk.Style()
        
        style.configure('TLabel', font='Serif 11', padding=9)
        
        self.entry_output = ttk.Label(root, width=41, textvariable=self.entry, anchor=W,
                                      background='white',borderwidth=1, relief=RIDGE)
        
        self.entry_output.grid(row=0, column=1, columnspan=3)
        
        style.configure('TButton', font='Times 14', padding=5)
        
        ttk.Button(root, text='\u232B', command=self.back_space).grid(row=0, column=4)
        ttk.Button(root, text='CE', command=self.clear_pressed).grid(row=0, column=0)

        ttk.Button(root, text='\u03C0', command=lambda: self.number_pressed(pi)).grid(row=1, column=0)
        ttk.Button(root, text='\u221A', command=lambda: self.operator_pressed('\u221A')).grid(row=1, column=1)
        ttk.Button(root, text='\u207F\u221A', command=lambda: self.operator_pressed('\u207F\u221A')).grid(row=1, column=2)
        ttk.Button(root, text='x\u207F', command=lambda: self.operator_pressed('x\u207F')).grid(row=1, column=3)
        ttk.Button(root, text='/', command=lambda: self.operator_pressed('/')).grid(row=1, column=4)
        
        ttk.Button(root, text='10\u207F', command=lambda: self.operator_pressed('10\u207F')).grid(row=2, column=0)
        ttk.Button(root, text='7', command=lambda: self.number_pressed(7)).grid(row=2, column=1)
        ttk.Button(root, text='8', command=lambda: self.number_pressed(8)).grid(row=2, column=2)
        ttk.Button(root, text='9', command=lambda: self.number_pressed(9)).grid(row=2, column=3)
        ttk.Button(root, text='\u00D7', command=lambda: self.operator_pressed('\u00D7')).grid(row=2, column=4)
        
        ttk.Button(root, text='\u33D2', command=lambda: self.operator_pressed('\u33D2')).grid(row=3, column=0)
        ttk.Button(root, text='4', command=lambda: self.number_pressed(4)).grid(row=3, column=1)
        ttk.Button(root, text='5', command=lambda: self.number_pressed(5)).grid(row=3, column=2)
        ttk.Button(root, text='6', command=lambda: self.number_pressed(6)).grid(row=3, column=3)
        ttk.Button(root, text='-', command=lambda: self.operator_pressed('-')).grid(row=3, column=4)
        
        ttk.Button(root, text='e\u207F', command=lambda: self.operator_pressed('e\u207F')).grid(row=4, column=0)
        ttk.Button(root, text='1', command=lambda: self.number_pressed(1)).grid(row=4, column=1)
        ttk.Button(root, text='2', command=lambda: self.number_pressed(2)).grid(row=4, column=2)
        ttk.Button(root, text='3', command=lambda: self.number_pressed(3)).grid(row=4, column=3)
        ttk.Button(root, text='+', command=lambda: self.operator_pressed('+')).grid(row=4, column=4)
        
        ttk.Button(root, text='\u33D1', command=lambda: self.operator_pressed('\u33D1')).grid(row=5, column=0)
        ttk.Button(root, text='\u00B1', command=self.plus_minus).grid(row=5, column=1)
        ttk.Button(root, text='0', command=lambda: self.number_pressed(0)).grid(row=5, column=2)
        ttk.Button(root, text='.', command=self.dotPressed).grid(row=5, column=3)
        ttk.Button(root, text='=', command=self.equal_pressed).grid(row=5, column=4)
        
        

def sizeSmall():
    print('Change size to small')

def sizeMedium():
    print('Change size to medium')
    
def sizeLarge():
    print('Change size to large')
    
def deleteHistory():
    print('Deleting history of calculator')

def editSomething():
    print('Redo Command')
    
def changeToRadians():
    print('Changing mode to radians')
    
def changeToDegrees():
    print('Changing mode to degrees')
    
def useScientificNotation():
    print('Using Scientific Notation')
    
def useDecimalNotation():
    print('Using Decimal Notation')
        
        

root = Tk()

mainFrame = Calculator(root)


topMenu = Menu(root)
root.config(menu = topMenu)

fileMenu = Menu(topMenu)
topMenu.add_cascade(label="File", menu=fileMenu)

fileMenu.add_command(label="Size Small", command=sizeSmall)
fileMenu.add_command(label="Size Medium", command=sizeMedium)
fileMenu.add_command(label="Size Large", command=sizeLarge)

fileMenu.add_separator()
fileMenu.add_command(label="Delete History", command=deleteHistory)
fileMenu.add_command(label="Quit", command=root.quit)

editMenu = Menu(topMenu)
topMenu.add_cascade(label="Edit", menu=editMenu)

editMenu.add_command(label="Redo", command=editSomething)
editMenu.add_separator()

editMenu.add_command(label="Radian Mode", command=changeToRadians)
editMenu.add_command(label="Degree Mode", command=changeToDegrees)
editMenu.add_separator()

editMenu.add_command(label="Use Scientific Notation", command=useScientificNotation)
editMenu.add_command(label="Use Decimal Notation", command=useDecimalNotation)

root.mainloop()

#Will add history functionality to easily recall previously used numbers
#Will add functionality to grow calculator size according to USER
#Try and see if multiple calculators can be added on 1 GUI for user to control
