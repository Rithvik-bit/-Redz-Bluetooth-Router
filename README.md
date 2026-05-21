<div align="center">
  <h1>🔴 Redz Bluetooth Audio Router</h1>
  <p><b>Simultaneously route any Windows system audio to dual Bluetooth earbuds with zero-latency sync.</b></p>
</div>

---

## 🎧 The Problem
Windows does not natively support outputting system audio (Spotify, YouTube, Games) to two separate Bluetooth headphones at the same time. If you connect two pairs of earbuds, you can only listen to one at a time. 

Even if you use third-party virtual audio cables, different brands of Bluetooth earbuds have different internal processing delays. This causes a terrible "echo" effect where one earbud plays sound slightly ahead of the other.

## 🚀 The Solution: Redz
**Redz** is a standalone Python application that intercepts your Windows Master Audio stream in real-time and duplicates it directly into two separate Bluetooth endpoints. 

It features **Live Sync Delay Ring-Buffers** that allow you to perfectly align the audio of two mismatched earbuds by delaying the faster pair in milliseconds!

### Features
- **Dual-Device Routing**: Play music to Earbuds A and Earbuds B simultaneously.
- **Independent Volume Control**: Built-in mathematical array multiplication allows you to boost the volume of one earbud up to 200% without affecting the other.
- **Sync Delay Sliders**: Dynamically hold the audio in a memory buffer (0-500ms) for one device, instantly removing Bluetooth echo.
- **RMS Visualizers**: Live-animated bars that bounce to the true waveform of your audio.
- **Custom UI**: Built with `customtkinter` for a sleek, hardware-accelerated dark mode interface.

---

## 📥 Installation & Usage (For Users)

1. Go to the [Releases](../../releases) tab on this GitHub repository.
2. Download `Redz.exe`.
3. Open Windows Sound Settings and set your Default Playback Device to **Laptop Speakers** (and mute them if you don't want to hear them out loud). 
   > *Note: If your earbuds are the default Windows device, the audio stream will feed back into itself!*
4. Run `Redz.exe`.
5. Select your two pairs of earbuds from the dropdown menus.
6. Click **Start Routing**. Adjust the volume and delay sliders until the audio perfectly syncs in your ears!

---

## 🛠️ Developer Setup (For Contributors)

If you want to run the python source code or contribute to the UI:

1. Clone this repository.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python redzbt.py
   ```

To compile your own executable, use PyInstaller:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --icon=custom_icon.ico --name="Redz" redzbt.py
```

---

## 🗺️ Roadmap & Help Wanted

We are actively looking for C++ / C# Windows developers to help automate one critical step!

Currently, users must manually set their Windows Default Audio device to their laptop speakers to avoid a feedback loop. Changing the default audio endpoint programmatically requires hooking into the undocumented Windows Kernel `IPolicyConfig` COM interface. 

If you are familiar with `pycaw` or writing C++ wrappers for `IPolicyConfig`, please submit a Pull Request to help us automate the default audio switching when the app launches!
