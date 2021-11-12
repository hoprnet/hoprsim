import numpy
from decimal import *
import networkx as nx
import matplotlib.pyplot as plt
import hoprsim

import PySimpleGUI as sg

def renderWindow(layout):
    window = sg.Window(
        title="HOPRsim",
        layout=layout,
        margins=(100, 50),
        location=(0,0)
    )
    return window


def drawUI():
    layout = [
        [sg.Text("HOPRsim")],
        [sg.Button("Generate stake matrix")]
    ]
    window = renderWindow(layout)

    while True:
        event, values = window.read()
        # End program if user closes window or
        # presses the OK button
        if event == "Generate stake matrix":
            print("got event")
            stake = hoprsim.setupStake()
            layout = [[sg.Text("{:3.0f}".format(cell)) for cell in row] for row in stake]
            window.close()
            window = renderWindow(layout)

        if event == sg.WIN_CLOSED:
            break

    window.close()

# drawUI()

stake = [
   [0, 2, 0, 0, 0, 0, 8, 0, 12, 0],
   [0, 0, 1, 0, 0, 0, 0, 7, 0, 0],
   [0, 11, 0, 1, 0, 0, 8, 0, 0, 0],
   [0, 2, 0, 0, 0, 0, 8, 0, 0, 0],
   [0, 0, 2, 0, 0, 0, 0, 13, 0, 0],
   [0, 0, 0, 14, 9, 0, 0, 5, 0, 0],
   [0, 0, 0, 23, 6, 0, 0, 0, 9, 0],
   [0, 2, 0, 11, 0, 0, 3, 0, 0, 20],
   [0, 0, 0, 0, 10, 0, 5, 0, 0, 0],
   [0, 3, 5, 0, 0, 7, 0, 1, 9, 0
]

#'''
stake = [
    [ 0, 80,  0,  1],
    [ 0,  0, 40,  1],
    [ 0, 20,  0,  1],
    [ 1,  1,  1,  1]
]
#'''

# stake = hoprsim.setupStake(20, 3, 20, 10, 100000, 0.1)
importance = hoprsim.calcImportance(stake)
# print("importance ", importance)
sortedPrioList = [i[0] for i in sorted(enumerate(importance), key=lambda x:x[1], reverse=True)]
print("sortedPrioList", sortedPrioList)



balancePerCtChannel = 5
hops = 3

#ctChannelBalances, ctNodeBalance = hoprsim.openInitialCtChannels(ctNodeBalance, balancePerCtChannel, importance)
#print("channel balances", ctChannelBalances)
numTests = 10
ctNodeBalance = 50
payoutPerHop = 1




totalPayout, ctPaths = hoprsim.runCT(stake, 10)

print("stake:")
hoprsim.printArray2d(stake, 0)

print("importance:")
hoprsim.printArray1d(importance)

print("paths:")
hoprsim.printArray2d(ctPaths, 0)

print("payout:")
hoprsim.printArray1d(totalPayout, 0)

totalStake = numpy.sum(stake, axis=1)
print("total stake:")
hoprsim.printArray1d(totalStake, 0)

'''
print("importance", importance)
# exp node 2 has been chosen 20 times for example
#table = [['total CT Nodes', 'total Payout'], [totalpathIndices, totalPayout]]
#print("table", table)
#accuracyAverage = [0.51,0.52,0.64,0.57,0.7,0.63,0.59,0.66,0.64]

hoprsim.drawGraph(stake)
plt.figure(2)

minMarkerSize = 2
maxMarkerSize = 20
normalizedImportance = [0] * len(importance)
minImportance = min(importance)
maxImportance = max(importance)
for x in range(len(importance)):
    normalizedImportance[x] = float((importance[x] - minImportance) / (maxImportance - minImportance) * (maxMarkerSize - minMarkerSize) + minMarkerSize)
print("normalizedImportance", normalizedImportance)

for x, y, size, text in zip(totalStake, totalPayout, normalizedImportance, range(len(stake))):
    plt.plot(x, y, ms=size, marker='o', color='r', linestyle='None')
    plt.text(x, y, text)
plt.title('Stake vs payout')
plt.xlabel('Stake')
plt.ylabel('Payout')
plt.yscale('log')
plt.xscale('log')
plt.show()
'''
