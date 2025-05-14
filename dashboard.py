# dashboard.py
import flet as ft
import requests

# === Server details ===
SERVER_URL = "http://192.168.43.131:5000"  # <- Set your PC's IP address here

def main(page: ft.Page):
    page.title = "ESP32 Smart System Dashboard"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.theme_mode = "dark"
    page.bgcolor = "#1E1E2F"
    page.padding = 20

    neon_green = "#A3FF5A"
    card_bg = "#2C2C3E"
    text_color = "#FFFFFF"

    # === Styled reusable containers ===
    def card(title, content):
        return ft.Container(
            content=ft.Column([ft.Text(title, size=16, weight="bold", color=neon_green)] + content, spacing=12),
            padding=15,
            border_radius=15,
            bgcolor=card_bg,
            width=320
        )

    def styled_checkbox(label, value=False):
        return ft.Switch(
            label=label,
            value=value,
            active_color=neon_green,
            inactive_thumb_color="#888",
            inactive_track_color="#444",
            thumb_color=text_color,
            scale=1.2,
        )

    def styled_slider(min_val, max_val, value):
        return ft.Slider(
            min=min_val,
            max=max_val,
            divisions=(max_val - min_val),
            value=value,
            active_color=neon_green,
            inactive_color="#444",
            thumb_color=neon_green,
            width=280,
        )

    def styled_button(label, on_click):
        return ft.ElevatedButton(
            text=label,
            on_click=on_click,
            style=ft.ButtonStyle(
                bgcolor=neon_green,
                color="#1E1E2F",
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.Padding(15, 12, 15, 12),
            )
        )

    # === UI Elements ===
    led_checkbox = styled_checkbox("LED Power")
    led_brightness_slider = styled_slider(0, 255, 0)
    fan_checkbox = styled_checkbox("Fan Power")
    fan_speed_slider = styled_slider(0, 255, 0)

    flet_status_text = ft.Text(value="Flet data not updated yet", color=text_color)
    esp_status_text = ft.Text(value="ESP data not updated yet", color=text_color)

    # === Functions ===
    def update_flet_data(e=None):
        data = {
            "led": led_checkbox.value,
            "analog_output": int(led_brightness_slider.value),
            "fan": fan_checkbox.value,
            "fan_speed": int(fan_speed_slider.value)
        }
        try:
            response = requests.post(f"{SERVER_URL}/esp/control", json=data)
            if response.status_code == 200:
                flet_status_text.value = "Flet control commands sent successfully"
            else:
                flet_status_text.value = f"Error sending control data: {response.status_code}"
        except Exception as ex:
            flet_status_text.value = f"Exception: {str(ex)}"
        page.update()

    def refresh_status(e=None):
        try:
            response_esp = requests.get(f"{SERVER_URL}/esp/data")
            esp_data = response_esp.json() if response_esp.status_code == 200 else {}

            response_ctrl = requests.get(f"{SERVER_URL}/esp/control")
            ctrl_data = response_ctrl.json() if response_ctrl.status_code == 200 else {}

            esp_status_text.value = (
                f"ESP Data\n"
                f"-----------------------------\n"
                f"Temperature: {esp_data.get('temperature', 0.0)} °C\n"
                f"Brightness Level: {esp_data.get('analog_input', 0)}\n"
                f"Motion Detected: {'Yes' if esp_data.get('button', False) else 'No'}\n"
                f"Potentiometer Fan Speed: {esp_data.get('fan_pot', 0)}"
            )

            led_checkbox.value = ctrl_data.get('led', False)
            led_brightness_slider.value = ctrl_data.get('analog_output', 0)
            fan_checkbox.value = ctrl_data.get('fan', False)
            fan_speed_slider.value = ctrl_data.get('fan_speed', 0)

            flet_status_text.value = "Data refreshed successfully"
        except Exception as ex:
            flet_status_text.value = f"Exception: {str(ex)}"
        page.update()

    # === Layout ===
    refresh_button = styled_button("Refresh Now", refresh_status)
    update_button = styled_button("Update Controls", update_flet_data)

    page.add(
        ft.Column([
            ft.Text("ESP32 Smart Dashboard", size=22, weight="bold", color=neon_green),
            card("LED Control", [led_checkbox, led_brightness_slider]),
            card("Fan Control", [fan_checkbox, fan_speed_slider]),
            ft.Row([refresh_button, update_button], alignment="center", spacing=20),
            ft.Container(content=flet_status_text, padding=10),
            ft.Container(content=esp_status_text, padding=10),
        ],
        spacing=25,
        alignment="center",
        horizontal_alignment="center")
    )

# Launch the app
if __name__ == "__main__":
    ft.app(target=main, view=ft.FLET_APP_HIDDEN)
