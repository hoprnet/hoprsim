import PySimpleGUI as sg

layout = [
    [sg.Text("HOPRsim")],
    [sg.Button("Generate stake matrix")]
]

window = sg.Window(
    title="Hello World",
    layout=layout,
    margins=(100, 50),
    location=(0,0)
)

while True:
    event, values = window.read()
    # End program if user closes window or
    # presses the OK button
    if event == "OK" or event == sg.WIN_CLOSED:
        break

window.close()


