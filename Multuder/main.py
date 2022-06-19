import pygame
from pygame.locals import *
from Multuder.body import *
from Multuder.constants import *
import PySimpleGUI as sg

pygame.init()
layout = [[sg.MLine("Enter you code here: (Delete text first)")], [sg.Button("OK")]]



window = sg.Window("Demo", layout)
responce = None


while True:
    event, values = window.read()

    if event == "OK" or event == sg.WIN_CLOSED:
        responce = int(values[0])
        break



window.close()

if responce == 29827:
    win = Window()
    win.play()

if responce == 90828:
    win = Shooter()
    win.play()

if responce == 98096:
    win = ThirdGame()
    win.play()
