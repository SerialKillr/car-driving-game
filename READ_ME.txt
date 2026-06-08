========================
JOYSTICK MODULE
========================

Joystick VCC  -> ESP32 VIN (5V)
Joystick GND  -> ESP32 GND
Joystick VRX  -> ESP32 GPIO34
Joystick VRY  -> ESP32 GPIO35
Joystick SW   -> ESP32 GPIO32

========================
LED
========================

ESP32 GPIO14  -> 220Ω Resistor
220Ω Resistor -> LED Anode (+)

LED Cathode (-) -> GND

========================
ACTIVE BUZZER
========================

Buzzer VCC    -> ESP32 3V3
Buzzer GND    -> ESP32 GND
Buzzer IN     -> ESP32 GPIO27

========================
USB
========================

ESP32 USB -> Laptop USB
