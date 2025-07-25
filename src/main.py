import flet as ft


def main(page: ft.Page):
    page.window.width = 450
    page.window.height = 600
    #page.window.frameless = True       Add for new design
    page.title = "Quick DNS Changer"


ft.app(main)
