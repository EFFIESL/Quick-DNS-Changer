import flet as ft
import json
import os
import subprocess
import re


SETTINGS_DIR = os.path.join(os.getenv('APPDATA'), 'QuickDNSChanger')
SETTINGS_FILE = os.path.join(SETTINGS_DIR, 'dnsList.json')
os.makedirs(SETTINGS_DIR, exist_ok=True)

def load_data():
    """Load DNS data from JSON file."""
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(data_to_save):
    """Save DNS list to JSON file."""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=4, ensure_ascii=False)


def main(page: ft.Page):
    """Main function of the program"""
    page.title = "Quick DNS Changer"
    page.window.width = 450
    page.window.height = 600
    page.window.resizable = False
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    dns_dropdown = ft.Dropdown(
        expand=True,
        hint_text="Select a DNS profile",
        on_change=lambda e: None
    )

    delete_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Delete Confirmation"),
        content=ft.Text("Are you sure you want to delete this DNS profile?"),
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.controls.append(delete_dialog)

    circle_color = ft.Colors.BLUE
    circle_button = None
    dns_connected = False

    def progress(percent, color=None):
        nonlocal circle_color
        global circle_button
        if color:
            circle_color = color
        elif percent == 100:
            circle_color = ft.Colors.GREEN
        elif percent > 0:
            circle_color = ft.Colors.YELLOW
        else:
            circle_color = ft.Colors.BLUE
        if circle_button:
            circle_button.bgcolor = circle_color
        page.update()

    def turnon(e):
        nonlocal dns_connected
        selected_dns = dns_dropdown.value
        if not selected_dns:
            set_log("Please select a DNS profile!", color=ft.Colors.RED)
            progress(0, ft.Colors.RED)
            dns_connected = False
            return
        dns_list = load_data()
        dns_profile = next((item for item in dns_list if item.get("name") == selected_dns), None)
        if not dns_profile:
            set_log("Please select a DNS profile!", color=ft.Colors.RED)
            progress(0, ft.Colors.RED)
            dns_connected = False
            return
        if dns_connected:
            interface_name = get_active_interface()
            if interface_name:
                set_dns_dynamic(interface_name)
                set_log("DNS reset to automatic (DHCP)!", color=ft.Colors.GREEN)
                progress(0)
                dns_connected = False
            else:
                set_log("Could not detect active network interface!", color=ft.Colors.RED)
                progress(0, ft.Colors.RED)
            return
        progress(50, ft.Colors.YELLOW)
        interface_name = get_active_interface()
        if not interface_name:
            set_log("Could not detect active network interface!", color=ft.Colors.RED)
            progress(0, ft.Colors.RED)
            dns_connected = False
            return
        result = set_dns(interface_name, dns_profile.get("preferred"), dns_profile.get("alternate"))
        if result:
            set_log("DNS servers have been updated!", color=ft.Colors.GREEN)
            progress(100, ft.Colors.GREEN)
            dns_connected = True
        else:
            set_log("Failed to set DNS. Please run as administrator.", color=ft.Colors.RED)
            progress(0, ft.Colors.RED)
            dns_connected = False

    def show_snackbar(message, color=ft.Colors.GREEN):
        """Shows a snackbar to display a message to the user."""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            open=True
        )
        page.update()

    def close_delete_dialog(e):
        """Closes the delete dialog."""
        page.dialog.open = False
        page.update()

    def confirm_delete(e, dns_name_to_delete):
        """Confirms the deletion of the selected DNS."""
        full_list = load_data()
        # Create a new list excluding the item to be deleted
        new_list = [item for item in full_list if item.get("name") != dns_name_to_delete]
        save_data(new_list)
        page.dialog.open = False
        page.update()
        show_snackbar(f"DNS '{dns_name_to_delete}' deleted successfully!", color=ft.Colors.GREEN)
        # Return and refresh the main page
        open_main_view(None)

    def open_delete_dialog(e):
        """Opens the delete confirmation dialog."""
        selected_dns = dns_dropdown.value
        if not selected_dns:
            show_snackbar("Please select a DNS profile to delete!", color=ft.Colors.RED)
            return
        # Update dialog actions to pass the selected DNS name
        delete_dialog.actions = [
            ft.TextButton(
                "Yes, delete", 
                on_click=lambda evt: confirm_delete(evt, selected_dns), 
                style=ft.ButtonStyle(color=ft.Colors.RED)
            ),
            ft.TextButton("No, cancel", on_click=close_delete_dialog),
        ]
        page.dialog = delete_dialog
        page.dialog.open = True
        page.update()

    def save_new_dns(e, name_field, preferred_field, alternate_field):
        """Saves a new DNS entry."""
        dns_name = name_field.value
        preferred_dns = preferred_field.value
        alternate_dns = alternate_field.value

        if not all([dns_name, preferred_dns, alternate_dns]):
            show_snackbar("Please fill in all fields.", color=ft.Colors.RED)
            return
            
        current_list = load_data()
        new_entry = {
            "name": dns_name,
            "preferred": preferred_dns,
            "alternate": alternate_dns
        }
        current_list.append(new_entry)
        save_data(current_list)
        
        show_snackbar(f"DNS '{dns_name}' saved successfully!", color=ft.Colors.GREEN)
        open_main_view(e)

    def open_main_view(e):
        """Displays the main page of the program."""
        page.controls.clear()

        page.controls.append(delete_dialog)
        dns_data_list = load_data()
        dropdown_options = [ft.dropdown.Option(item.get("name")) for item in dns_data_list]
        dns_dropdown.options = dropdown_options

        page.update()
        global circle_button
        circle_button = ft.Container(
            content=ft.Icon(ft.Icons.POWER_SETTINGS_NEW, size=60, color=ft.Colors.WHITE),
            bgcolor=circle_color,
            width=90,
            height=90,
            border_radius=45,
            alignment=ft.alignment.center,
            on_click=turnon,
        )
        page.add(
            ft.Row(
                [
                    ft.IconButton(icon=ft.Icons.SETTINGS, on_click=open_settings_view, tooltip="Settings"),
                    dns_dropdown,
                    ft.IconButton(icon=ft.Icons.ADD, on_click=open_add_dns_view, tooltip="Add new DNS"),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_FOREVER,
                        icon_color=ft.Colors.RED_700,
                        tooltip="Delete selected DNS",
                        on_click=open_delete_dialog
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Container(
                circle_button,
                alignment=ft.alignment.center,
                expand=True
            ),
            ft.Container(
                log_text,
                alignment=ft.alignment.bottom_left,
                padding=ft.padding.only(left=10, bottom=20),
                expand=False
            ),
        )
        page.update()

    def open_add_dns_view(e):
        """Displays the add new DNS page."""
        page.controls.clear()
        
        dns_name_field = ft.TextField(label="DNS Name", expand=True)
        preferred_dns_field = ft.TextField(label="Preferred DNS", expand=True)
        alternate_dns_field = ft.TextField(label="Alternate DNS", expand=True)

        page.add(
            ft.Row([ft.IconButton(on_click=open_main_view, icon=ft.Icons.ARROW_BACK), ft.Text("Add new DNS", size=20)]),
            ft.Row([dns_name_field]),
            ft.Row([preferred_dns_field]),
            ft.Row([alternate_dns_field]),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Save",
                        expand=True,
                        height=50,
                        icon=ft.Icons.SAVE,
                        on_click=lambda evt: save_new_dns(evt, dns_name_field, preferred_dns_field, alternate_dns_field)
                    )
                ]
            )
        )
        page.update()

    def open_settings_view(e):
        """Displays the settings page."""
        page.controls.clear()
        
        page.add(
            ft.Row([ft.IconButton(on_click=open_main_view, icon=ft.Icons.ARROW_BACK), ft.Text("Settings", size=20)]),
            ft.ElevatedButton("erfansalimi1385@gmail.com", icon=ft.Icons.EMAIL),
            ft.ElevatedButton(
                content=ft.Row([ft.Image(src="github-mark.png", width=24, height=24) , ft.Text("Github Page")]), on_click=lambda e:page.launch_url("https://github.com/EFFIESL/Quick-DNS-Changer"))
        )
        page.update()

    # --- Log Output ---
    log_text = ft.Text(value="", size=16, color=ft.Colors.WHITE)

    def set_log(msg, color=ft.Colors.WHITE):
        log_text.value = msg
        log_text.color = color
        page.update()

    def get_network_interfaces():
        try:
            set_log("Searching for active network interfaces...")
            result = subprocess.run(
                ["netsh", "interface", "show", "interface"],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8'
            )
            interfaces = re.findall(r"Connected\s+Dedicated\s+(.+)", result.stdout)
            if not interfaces:
                set_log("No active connected network interfaces found.", color=ft.Colors.RED)
                return []
            set_log(f"Available Network Interface: {interfaces[0].strip()}")
            return [name.strip() for name in interfaces]
        except Exception as e:
            set_log(f"Error: Could not retrieve network interfaces. {e}", color=ft.Colors.RED)
            return []

    def set_dns(interface_name, primary_dns, secondary_dns=None):
        try:
            subprocess.run(f'netsh interface ipv4 set dnsserver name="{interface_name}" static {primary_dns} primary', shell=True, check=True, capture_output=True)
            if secondary_dns:
                subprocess.run(f'netsh interface ipv4 add dnsserver name="{interface_name}" {secondary_dns} index=2', shell=True, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False

    def set_dns_dynamic(interface_name):
        try:
            subprocess.run(f'netsh interface ipv4 set dnsserver name="{interface_name}" source=dhcp', shell=True, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False

    def get_active_interface():
        interfaces = get_network_interfaces()
        return interfaces[0] if interfaces else None

    def on_window_close(e):
        interface_name = get_active_interface()
        if interface_name:
            set_dns_dynamic(interface_name)
        page.window_destroy()

    page.on_window_event = on_window_close

    open_main_view(None)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
