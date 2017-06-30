from tkinter import *

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