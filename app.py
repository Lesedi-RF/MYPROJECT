from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Store data from ESP32 and user control commands
esp_data = {
    "analog_input": 0,
    "button": False,
    "temperature": 0.0,
    "fan_pot": 0
}

control_commands = {
    "led": False,
    "analog_output": 0,
    "fan": False,
    "fan_speed": 0
}

# === Updated HTML Template ===
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ESP32 Smart System</title>
  <style>
    body {
      background: #1e1e2f;
      color: #ffffff;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      padding: 20px;
    }
    h2 {
      color: #a3ff5a;
      border-bottom: 2px solid #333;
      padding-bottom: 5px;
    }
    ul {
      list-style: none;
      padding: 0;
    }
    li {
      background: #2c2c3e;
      margin-bottom: 8px;
      padding: 12px;
      border-radius: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    fieldset {
      border: 1px solid #333;
      border-radius: 12px;
      padding: 15px;
      margin-bottom: 20px;
      background: #2c2c3e;
    }
    legend {
      color: #a3ff5a;
      font-weight: bold;
      padding: 0 8px;
    }
    label {
      display: block;
      margin-bottom: 12px;
    }
    input[type="number"] {
      width: 100%;
      padding: 6px;
      margin-top: 4px;
      background: #1e1e2f;
      color: white;
      border: 1px solid #555;
      border-radius: 8px;
    }
    input[type="submit"] {
      background-color: #a3ff5a;
      color: #1e1e2f;
      border: none;
      padding: 12px 20px;
      border-radius: 12px;
      cursor: pointer;
      font-weight: bold;
      transition: background-color 0.3s;
    }
    input[type="submit"]:hover {
      background-color: #89e94f;
    }
    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 26px;
    }
    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0;
      right: 0; bottom: 0;
      background-color: #444;
      transition: .4s;
      border-radius: 34px;
    }
    .slider:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
    .toggle-switch input:checked + .slider {
      background-color: #a3ff5a;
    }
    .toggle-switch input:checked + .slider:before {
      transform: translateX(24px);
    }
    .section-title {
      margin-bottom: 10px;
      font-size: 1.2rem;
    }
  </style>
</head>
<body>

<h2>ESP32 Sensor Data</h2>
<ul>
  <li><span>Temperature</span> <span>{{ data.temperature }} °C</span></li>
  <li><span>Brightness Level</span> <span>{{ data.analog_input }}</span></li>
  <li><span>Motion Detected</span> <span>{{ 'Yes' if data.button else 'No' }}</span></li>
  <li><span>Potentiometer Fan Speed</span> <span>{{ data.fan_pot }}</span></li>
  <li><span><strong>LED Status</strong></span> <span>{{ 'ON' if commands.led else 'OFF' }}</span></li>
  <li><span><strong>Fan Status</strong></span> <span>{{ 'ON' if commands.fan else 'OFF' }}</span></li>
</ul>

<h2>Control Panel</h2>
<form action="/control" method="post">

  <fieldset>
    <legend>LED Control</legend>
    <label>LED Power:
      <div class="toggle-switch">
        <input type="checkbox" name="led" {% if commands.led %}checked{% endif %}>
        <span class="slider"></span>
      </div>
    </label>
    <label>LED Brightness (0-255):
      <input type="number" name="analog_output" min="0" max="255" value="{{ commands.analog_output }}">
    </label>
  </fieldset>

  <fieldset>
    <legend>Fan Control</legend>
    <label>Fan Power:
      <div class="toggle-switch">
        <input type="checkbox" name="fan" {% if commands.fan %}checked{% endif %}>
        <span class="slider"></span>
      </div>
    </label>
    <label>Fan Speed (0-255):
      <input type="number" name="fan_speed" min="0" max="255" value="{{ commands.fan_speed }}">
    </label>
  </fieldset>

  <input type="submit" value="Update Controls">

</form>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, data=esp_data, commands=control_commands)

@app.route('/control', methods=['POST'])
def update_controls():
    control_commands['led'] = 'led' in request.form
    control_commands['analog_output'] = int(request.form.get('analog_output', 0))
    control_commands['fan'] = 'fan' in request.form
    control_commands['fan_speed'] = int(request.form.get('fan_speed', 0))
    return render_template_string(HTML_TEMPLATE, data=esp_data, commands=control_commands)

@app.route('/esp/update', methods=['POST'])
def esp_update():
    data = request.get_json()
    if data:
        esp_data.update({
            "analog_input": data.get("analog_input", 0),
            "button": data.get("button", False),
            "temperature": data.get("temperature", 0.0),
            "fan_pot": data.get("fan_pot", 0)
        })
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/esp/control', methods=['GET'])
def esp_control():
    return jsonify(control_commands)

@app.route('/esp/control', methods=['POST'])
def esp_control_update():
    data = request.get_json()
    if data:
        control_commands['led'] = bool(data.get('led', False))
        control_commands['analog_output'] = int(data.get('analog_output', 0))
        control_commands['fan'] = bool(data.get('fan', False))
        control_commands['fan_speed'] = int(data.get('fan_speed', 0))
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Invalid data"}), 400

@app.route('/esp/data', methods=['GET'])
def get_esp_data():
    return jsonify(esp_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

