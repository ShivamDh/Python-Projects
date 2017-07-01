from tkinter import *
from tkinter import ttk  # @Reimport
from math import *
import tkinter

class Calculator:
    
    def numberPressed(self, number):
        print('Number Pressed {0}'.format(str(number)))
        self.entry.set(self.entry.get() + str(number))
        
    def operatorPressed(self, operation):
        print('Operation Pressed {0}'.format(operation))
        
    def clearPressed(self):
        print('Clear Pressed')
        
    def plus_minus(self):
        print('Plus Minus clicked')
    
    def dotPressed(self):
        print('Dot clicked')
    
    def __init__(self, root):
        self.entry = StringVar(root, value='')
        
        self.calc_value: 0.0
        self.math_button_pressed = ''
        self.number_button_pressed = ''
        
        root.title('Custom Calculator')
        root.resizable(width=False, height=False)
        
        style=ttk.Style()
        
        style.configure('TLabel', font='Serif 11', padding=9)
        
        self.entry_output = ttk.Label(root, width=41, textvariable=self.entry, anchor=W, background='white',borderwidth=1, relief=RIDGE)
        
        self.entry_output.grid(row=0, column=1, columnspan=3)
        
        style.configure('TButton', font='Times 14', padding=5)
        
        ttk.Button(root, text='\u232B', command=lambda: self.operatorPressed('back space')).grid(row=0, column=4)
        ttk.Button(root, text='CE', command=self.clearPressed).grid(row=0, column=0)

        ttk.Button(root, text='\u03C0', command=lambda: self.numberPressed(pi)).grid(row=1, column=0)
        ttk.Button(root, text='\u221A', command=lambda: self.operatorPressed('square root')).grid(row=1, column=1)
        ttk.Button(root, text='\u207F\u221A', command=lambda: self.operatorPressed('nth root')).grid(row=1, column=2)
        ttk.Button(root, text='x\u207F', command=lambda: self.operatorPressed('power')).grid(row=1, column=3)
        ttk.Button(root, text='/', command=lambda: self.operatorPressed('divide')).grid(row=1, column=4)
        
        ttk.Button(root, text='10\u207F', command=lambda: self.operatorPressed('power of 10')).grid(row=2, column=0)
        ttk.Button(root, text='7', command=lambda: self.numberPressed(7)).grid(row=2, column=1)
        ttk.Button(root, text='8', command=lambda: self.numberPressed(8)).grid(row=2, column=2)
        ttk.Button(root, text='9', command=lambda: self.numberPressed(9)).grid(row=2, column=3)
        ttk.Button(root, text='\u00D7', command=lambda: self.operatorPressed('multiply')).grid(row=2, column=4)
        
        ttk.Button(root, text='\u33D2', command=lambda: self.operatorPressed('log')).grid(row=3, column=0)
        ttk.Button(root, text='4', command=lambda: self.numberPressed(4)).grid(row=3, column=1)
        ttk.Button(root, text='5', command=lambda: self.numberPressed(5)).grid(row=3, column=2)
        ttk.Button(root, text='6', command=lambda: self.numberPressed(6)).grid(row=3, column=3)
        ttk.Button(root, text='-', command=lambda: self.operatorPressed('subtract')).grid(row=3, column=4)
        
        ttk.Button(root, text='e\u207F', command=lambda: self.operatorPressed('power of e')).grid(row=4, column=0)
        ttk.Button(root, text='1', command=lambda: self.numberPressed(1)).grid(row=4, column=1)
        ttk.Button(root, text='2', command=lambda: self.numberPressed(2)).grid(row=4, column=2)
        ttk.Button(root, text='3', command=lambda: self.numberPressed(3)).grid(row=4, column=3)
        ttk.Button(root, text='+', command=lambda: self.operatorPressed('add')).grid(row=4, column=4)
        
        ttk.Button(root, text='\u33D1', command=lambda: self.operatorPressed('ln')).grid(row=5, column=0)
        ttk.Button(root, text='\u00B1', command=self.plus_minus).grid(row=5, column=1)
        ttk.Button(root, text='0', command=lambda: self.numberPressed(0)).grid(row=5, column=2)
        ttk.Button(root, text='.', command=self.dotPressed).grid(row=5, column=3)
        ttk.Button(root, text='=', command=lambda: self.operatorPressed('equal')).grid(row=5, column=4)
        
        

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