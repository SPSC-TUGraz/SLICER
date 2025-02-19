import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog

mydir = {}
mydir['A'] = 1
mydir['B'] = 2
print(mydir)
for index in mydir:
    print(index)


nsamples = 10
a = np.ones((nsamples,1))
print(a)
a = np.multiply(a,np.flip(np.arange(0,nsamples)/np.size(a)))
print(a)
print(np.arange(0,-1))

workspace_path = filedialog.asksaveasfilename(defaultextension='.pkl')
if workspace_path:
    print('done')
else:
    print('none chosen')