import flet as ft


def main(page: ft.Page):
    page.window.width = 450
    page.window.height = 600
    #page.window.frameless = True       Add for new design
    page.title = "Quick DNS Changer"
    def open_main(e):
        page.clean()
        settin_button = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            on_click=open_setting)
        page.add(settin_button)
        page.update

    def open_setting(e):
        page.clean()

        back_button = ft.IconButton(
            on_click=open_main,
            icon=ft.Icons.ARROW_BACK
        )
        
        page.add(back_button, ft.Text("Comming soon ..."))
        page.update
    
    open_main(None)

ft.app(main)
