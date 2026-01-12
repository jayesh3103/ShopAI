import json
import os

def create_mock_data():
    products = [
        {
            "id": "p001",
            "name": "Wireless Noise-Canceling Headphones",
            "price": 299.99,
            "description": "Premium over-ear headphones with active noise cancellation, 30-hour battery life, and plush ear cushions for all-day comfort.",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80",
            "manual_text": "Power On/Off: Press and hold the power button for 3 seconds. \nBluetooth Pairing: Enable Bluetooth on your device, search for 'AudioMax Pro', and select to pair. \nCharging: Connect the USB-C cable to the charging port. LED turns green when fully charged. \nNoise Cancellation: Toggle the ANC switch on the left earcup."
        },
        {
            "id": "p002",
            "name": "Smart Fitness Watch",
            "price": 149.50,
            "description": "Advanced fitness tracker with heart rate monitoring, GPS, sleep tracking, and water resistance up to 50 meters.",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80",
            "manual_text": "Setup: Download the 'FitTrack' app on your smartphone. Follow on-screen instructions to pair via Bluetooth. \nHeart Rate: Navigate to the Heart Rate widget to measure instantly. \nWater Lock: Enable Water Lock mode before swimming to prevent accidental touches. \nReset: Hold the side button for 10 seconds to reboot."
        },
        {
            "id": "p003",
            "name": "Portable Bluetooth Speaker",
            "price": 89.99,
            "description": "Compact speaker delivering powerful 360-degree sound. Waterproof design, perfect for outdoor adventures.",
            "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=500&q=80",
            "manual_text": "Pairing: Press the Bluetooth button until the light flashes blue. Select 'SoundBlast Mini' on your device. \nStereo Mode: Pair two speakers by holding the Link button on both simultaneously. \nBattery: Red light indicates low battery. Charge using the included micro-USB cable. \nCleaning: Wipe with a damp cloth. Do not submerge while charging."
        },
        {
            "id": "p004",
            "name": "4K Action Camera",
            "price": 349.00,
            "description": "Capture life's moments in stunning 4K resolution. Waterproof case included, enabling underwater filming.",
            "image_url": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500&q=80",
            "manual_text": "Insert SD Card: Use a Class 10 microSD card (up to 128GB). Format before first use. \nRecord Video: Press the top shutter button to start/stop recording. \nWiFi connection: Enable WiFi in settings to transfer files to the mobile app. \nMounting: Use the included adhesive mounts for helmets or dashes."
        },
        {
            "id": "p005",
            "name": "Ergonomic Mechanical Keyboard",
            "price": 129.99,
            "description": "High-performance mechanical keyboard with customizable RGB lighting and tactile switches for a responsive typing experience.",
            "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b91a45e?w=500&q=80",
            "manual_text": "RGB Modes: Press FN + Insert to cycle through lighting effects. \nMacros: Download the driver software to record custom macros. \nKeycap Removal: Use the included puller to gently remove keycaps for cleaning. \nConnection: Plug the USB cable into a USB 3.0 port for best performance."
        }
    ]

    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, "products.json")
    with open(file_path, "w") as f:
        json.dump(products, f, indent=4)
    
    print(f"Successfully created {file_path} with {len(products)} products (now with prices).")

if __name__ == "__main__":
    create_mock_data()
