import pyaudiowpatch as pyaudio
import customtkinter as ctk
import threading
import queue
import time
import numpy as np
import collections

class RedzbtApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#080808")
        
        # --- UI Window Setup ---
        self.title("REDZ BT")
        self.geometry("560x780")
        self.resizable(False, False)
        
        # --- Audio Engine Setup ---
        self.p = pyaudio.PyAudio()
        self.is_routing = False
        
        self.in_stream = None
        self.out_stream_a = None
        self.out_stream_b = None
        
        # Thread-safe queues for decoupling output timing
        self.queue_a = queue.Queue(maxsize=30)
        self.queue_b = queue.Queue(maxsize=30)
        
        self.create_icon()
        self.build_ui()
        self.load_devices()

    def create_icon(self):
        import os
        
        # If you place a file named "custom_icon.ico" in the folder, it will use that instead!
        if os.path.exists("custom_icon.ico"):
            try:
                self.iconbitmap("custom_icon.ico")
                return
            except Exception:
                pass
                
        icon_path = "redz_icon.ico"
        if not os.path.exists(icon_path):
            try:
                from PIL import Image, ImageDraw
                img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                # Draw dark background with red outline
                draw.rounded_rectangle([0, 0, 64, 64], radius=16, fill="#080808", outline="#ff0000", width=3)
                # Trace the Bluetooth Rune
                path = [
                    (20, 44), (32, 32), (44, 20), (32, 10), 
                    (32, 54), (44, 44), (32, 32), (20, 20)
                ]
                draw.line(path, fill="#ff0000", width=6, joint="curve")
                img.save(icon_path, format="ICO", sizes=[(64, 64)])
            except Exception as e:
                pass
                
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def load_devices(self):
        try:
            self.wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
            self.default_loopback = self.p.get_default_wasapi_loopback()
            self.loopback_label.configure(text=f"System Audio: {self.default_loopback['name']}")

            self.output_devices = []
            for i in range(self.p.get_device_count()):
                dev = self.p.get_device_info_by_index(i)
                if dev["hostApi"] == self.wasapi_info["index"] and dev["maxOutputChannels"] > 0 and not dev["isLoopbackDevice"]:
                    self.output_devices.append(dev)

            device_names = [d["name"] for d in self.output_devices]
            
            self.combo_a.configure(values=device_names)
            self.combo_b.configure(values=device_names)
            
            if len(device_names) > 0:
                self.combo_a.set(device_names[0])
                if len(device_names) > 1:
                    self.combo_b.set(device_names[1])
                else:
                    self.combo_b.set(device_names[0])
        except Exception as e:
            self.loopback_label.configure(text="Failed to initialize WASAPI.", text_color="#E50914")
            print("Error loading devices:", e)

    def update_val_labels(self, *args):
        try:
            if hasattr(self, 'vol_val_a'):
                self.vol_val_a.configure(text=f"{int(self.vol_a.get() * 100)}%")
            if hasattr(self, 'delay_val_a'):
                self.delay_val_a.configure(text=f"{int(self.delay_a.get())} ms")
            if hasattr(self, 'vol_val_b'):
                self.vol_val_b.configure(text=f"{int(self.vol_b.get() * 100)}%")
            if hasattr(self, 'delay_val_b'):
                self.delay_val_b.configure(text=f"{int(self.delay_b.get())} ms")
        except Exception:
            pass

    def build_ui(self):
        # Title Frame for Cinematic Branding
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=(28, 0))
        
        red_label = ctk.CTkLabel(title_frame, text="RED", font=ctk.CTkFont(family="Trebuchet MS", size=42, weight="bold"), text_color="#FFFFFF")
        red_label.pack(side="left")
        
        z_label = ctk.CTkLabel(title_frame, text="Z", font=ctk.CTkFont(family="Trebuchet MS", size=42, weight="bold"), text_color="#E50914")
        z_label.pack(side="left")
        
        bt_label = ctk.CTkLabel(title_frame, text=" BT", font=ctk.CTkFont(family="Trebuchet MS", size=42, weight="bold"), text_color="#888888")
        bt_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(self, text="DUAL BLUETOOTH AUDIO ROUTER", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color="#888888")
        subtitle_label.pack(pady=(2, 6))
        
        self.loopback_label = ctk.CTkLabel(self, text="Initializing WASAPI loopback drivers...", font=ctk.CTkFont(family="Segoe UI", size=11), text_color="#666666")
        self.loopback_label.pack(pady=(0, 16))
        
        # --- Device A Block ---
        frame_a = ctk.CTkFrame(self, fg_color="#111111", corner_radius=12, border_width=1, border_color="#2A0B0D")
        frame_a.pack(pady=10, padx=25, fill="x")
        
        self.label_a = ctk.CTkLabel(frame_a, text="🎧  EARBUDS CHANNEL A (LEFT SINK)", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#E50914")
        self.label_a.pack(anchor="w", padx=20, pady=(15, 2))
        
        self.combo_a = ctk.CTkComboBox(frame_a, width=420, height=36, corner_radius=8,
                                       fg_color="#181818", text_color="#F0F0F0", border_color="#3A1215",
                                       button_color="#E50914", button_hover_color="#B3040E",
                                       dropdown_fg_color="#181818", dropdown_hover_color="#2A0B0D", dropdown_text_color="#F0F0F0")
        self.combo_a.pack(pady=(5, 15), padx=20, fill="x")
        
        # Volume Control Row inside Frame A
        vol_frame_a = ctk.CTkFrame(frame_a, fg_color="transparent")
        vol_frame_a.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(vol_frame_a, text="Volume:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888").pack(side="left")
        self.vol_val_a = ctk.CTkLabel(vol_frame_a, text="100%", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#E50914")
        self.vol_val_a.pack(side="right")
        
        self.vol_a = ctk.CTkSlider(vol_frame_a, from_=0, to=2.0, height=16, button_color="#E50914", progress_color="#E50914", button_hover_color="#B3040E", command=self.update_val_labels)
        self.vol_a.set(1.0)
        self.vol_a.pack(side="right", padx=15, fill="x", expand=True)
        
        # Delay Control Row inside Frame A
        delay_frame_a = ctk.CTkFrame(frame_a, fg_color="transparent")
        delay_frame_a.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(delay_frame_a, text="Sync Delay:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888").pack(side="left")
        self.delay_val_a = ctk.CTkLabel(delay_frame_a, text="0 ms", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#E50914")
        self.delay_val_a.pack(side="right")
        
        self.delay_a = ctk.CTkSlider(delay_frame_a, from_=0, to=500, height=16, button_color="#E50914", progress_color="#E50914", button_hover_color="#B3040E", command=self.update_val_labels)
        self.delay_a.set(0)
        self.delay_a.pack(side="right", padx=15, fill="x", expand=True)
        
        self.vis_a = ctk.CTkProgressBar(frame_a, width=420, height=8, corner_radius=4, progress_color="#E50914", fg_color="#181818")
        self.vis_a.set(0)
        self.vis_a.pack(pady=(0, 15), padx=20, fill="x")

        # --- Device B Block ---
        frame_b = ctk.CTkFrame(self, fg_color="#111111", corner_radius=12, border_width=1, border_color="#2A0B0D")
        frame_b.pack(pady=10, padx=25, fill="x")
        
        self.label_b = ctk.CTkLabel(frame_b, text="🎧  EARBUDS CHANNEL B (RIGHT SINK)", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color="#E50914")
        self.label_b.pack(anchor="w", padx=20, pady=(15, 2))
        
        self.combo_b = ctk.CTkComboBox(frame_b, width=420, height=36, corner_radius=8,
                                       fg_color="#181818", text_color="#F0F0F0", border_color="#3A1215",
                                       button_color="#E50914", button_hover_color="#B3040E",
                                       dropdown_fg_color="#181818", dropdown_hover_color="#2A0B0D", dropdown_text_color="#F0F0F0")
        self.combo_b.pack(pady=(5, 15), padx=20, fill="x")
        
        # Volume Control Row inside Frame B
        vol_frame_b = ctk.CTkFrame(frame_b, fg_color="transparent")
        vol_frame_b.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(vol_frame_b, text="Volume:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888").pack(side="left")
        self.vol_val_b = ctk.CTkLabel(vol_frame_b, text="100%", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#E50914")
        self.vol_val_b.pack(side="right")
        
        self.vol_b = ctk.CTkSlider(vol_frame_b, from_=0, to=2.0, height=16, button_color="#E50914", progress_color="#E50914", button_hover_color="#B3040E", command=self.update_val_labels)
        self.vol_b.set(1.0)
        self.vol_b.pack(side="right", padx=15, fill="x", expand=True)
        
        # Delay Control Row inside Frame B
        delay_frame_b = ctk.CTkFrame(frame_b, fg_color="transparent")
        delay_frame_b.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkLabel(delay_frame_b, text="Sync Delay:", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#888888").pack(side="left")
        self.delay_val_b = ctk.CTkLabel(delay_frame_b, text="0 ms", font=ctk.CTkFont(family="Consolas", size=12, weight="bold"), text_color="#E50914")
        self.delay_val_b.pack(side="right")
        
        self.delay_b = ctk.CTkSlider(delay_frame_b, from_=0, to=500, height=16, button_color="#E50914", progress_color="#E50914", button_hover_color="#B3040E", command=self.update_val_labels)
        self.delay_b.set(0)
        self.delay_b.pack(side="right", padx=15, fill="x", expand=True)
        
        self.vis_b = ctk.CTkProgressBar(frame_b, width=420, height=8, corner_radius=4, progress_color="#E50914", fg_color="#181818")
        self.vis_b.set(0)
        self.vis_b.pack(pady=(0, 15), padx=20, fill="x")

        # --- Controls and Status Block ---
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(pady=15, fill="x", padx=25)
        
        self.start_btn = ctk.CTkButton(controls_frame, text="START ROUTING", height=52, corner_radius=26,
                                       font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                                       command=self.toggle_routing, fg_color="#E50914", hover_color="#B3040E",
                                       text_color="#FFFFFF")
        self.start_btn.pack(fill="x", pady=(0, 10))
        
        # Status LED and description bar
        status_panel = ctk.CTkFrame(controls_frame, fg_color="#111111", height=42, corner_radius=8, border_width=1, border_color="#2A0B0D")
        status_panel.pack(fill="x")
        
        self.status_led = ctk.CTkLabel(status_panel, text="●", font=ctk.CTkFont(size=16), text_color="#888888")
        self.status_led.pack(side="left", padx=(15, 5))
        
        self.status_label = ctk.CTkLabel(status_panel, text="Status: Inactive", text_color="#888888", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"))
        self.status_label.pack(side="left", pady=10)

        # Trigger initial values for volume and delay text labels
        self.update_val_labels()

    def get_device_by_name(self, name):
        for d in self.output_devices:
            if d["name"] == name:
                return d
        return None

    def capture_callback(self, in_data, frame_count, time_info, status):
        if self.is_routing:
            try:
                self.queue_a.put_nowait(in_data)
            except queue.Full:
                pass 
                
            try:
                self.queue_b.put_nowait(in_data)
            except queue.Full:
                pass
        return (in_data, pyaudio.paContinue)

    def write_thread(self, stream, q, channel):
        # Dynamic delay ring buffer
        delay_buffer = collections.deque()
        
        RATE = int(self.default_loopback["defaultSampleRate"])
        CHUNK = 1024
        ms_per_chunk = (CHUNK / RATE) * 1000
        
        while self.is_routing:
            try:
                data = q.get(timeout=0.1)
                
                # 1. Fetch live UI values
                vol = self.vol_a.get() if channel == 'a' else self.vol_b.get()
                delay_ms = self.delay_a.get() if channel == 'a' else self.delay_b.get()
                vis_bar = self.vis_a if channel == 'a' else self.vis_b
                
                # 2. Convert to mathematical array
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # 3. Calculate RMS for Visualizer Bar
                rms = np.sqrt(np.mean(audio_data.astype(np.float32)**2))
                normalized_rms = min(rms / 15000.0, 1.0) # Scale to typical max music volume
                self.after(0, vis_bar.set, normalized_rms)
                
                # 4. Multiply by Volume (0% to 200%)
                if vol != 1.0:
                    audio_data = np.clip(audio_data * vol, -32768, 32767).astype(np.int16)
                    data = audio_data.tobytes()
                    
                # 5. Live Delay Ring Buffer
                delay_buffer.append(data)
                target_chunks = int(delay_ms / ms_per_chunk)
                
                # If user slides delay down, quickly drop buffered chunks
                while len(delay_buffer) > target_chunks + 1:
                    delay_buffer.popleft()
                    
                # If buffer has accumulated enough delay, pop and write to bluetooth
                if len(delay_buffer) >= target_chunks:
                    write_data = delay_buffer.popleft()
                    if stream.is_active():
                        if write_data and len(write_data) > 0:
                            stream.write(write_data)
                            
            except queue.Empty:
                # Decay visualizer if no audio
                vis_bar = self.vis_a if channel == 'a' else self.vis_b
                self.after(0, vis_bar.set, 0)
                continue
            except Exception as e:
                print(f"Hardware Write Interruption: {e}")
                break

    def toggle_routing(self):
        if self.is_routing:
            self.stop_routing()
        else:
            self.start_routing()

    def start_routing(self):
        dev_a = self.get_device_by_name(self.combo_a.get())
        dev_b = self.get_device_by_name(self.combo_b.get())
        
        if not dev_a or not dev_b:
            self.status_label.configure(text="Please select both devices.", text_color="#E50914")
            self.status_led.configure(text_color="#888888")
            return
            
        loopback_name = self.default_loopback["name"]
        if dev_a["name"] in loopback_name or dev_b["name"] in loopback_name:
            self.status_label.configure(text="FEEDBACK DETECTED: Set default speakers!", text_color="#F39C12")
            self.status_led.configure(text_color="#F39C12")
            return
            
        self.is_routing = True
        
        RATE = int(self.default_loopback["defaultSampleRate"])
        CHANNELS = self.default_loopback["maxInputChannels"]
        
        try:
            self.out_stream_a = self.p.open(format=pyaudio.paInt16,
                                           channels=CHANNELS,
                                           rate=RATE,
                                           output=True,
                                           output_device_index=dev_a["index"])
            self.out_stream_b = self.p.open(format=pyaudio.paInt16,
                                           channels=CHANNELS,
                                           rate=RATE,
                                           output=True,
                                           output_device_index=dev_b["index"])
                                           
            while not self.queue_a.empty(): self.queue_a.get()
            while not self.queue_b.empty(): self.queue_b.get()
                                           
            threading.Thread(target=self.write_thread, args=(self.out_stream_a, self.queue_a, 'a'), daemon=True).start()
            threading.Thread(target=self.write_thread, args=(self.out_stream_b, self.queue_b, 'b'), daemon=True).start()
            
            self.in_stream = self.p.open(format=pyaudio.paInt16,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        input=True,
                                        input_device_index=self.default_loopback["index"],
                                        frames_per_buffer=1024,
                                        stream_callback=self.capture_callback)
                                        
            self.start_btn.configure(text="STOP ROUTING", fg_color="#181818", hover_color="#2A0B0D", border_width=1, border_color="#E50914", text_color="#E50914")
            self.status_label.configure(text="Status: Active Routing", text_color="#E50914")
            self.status_led.configure(text_color="#E50914")
            
        except Exception as e:
            self.stop_routing()
            self.status_label.configure(text=f"Hardware mismatch: {str(e)}", text_color="#F39C12")
            self.status_led.configure(text_color="#F39C12")
            print("Detailed traceback:", e)

    def stop_routing(self):
        self.is_routing = False
        time.sleep(0.1) 
        
        if self.in_stream:
            self.in_stream.stop_stream()
            self.in_stream.close()
            self.in_stream = None
            
        if self.out_stream_a:
            self.out_stream_a.stop_stream()
            self.out_stream_a.close()
            self.out_stream_a = None
            
        if self.out_stream_b:
            self.out_stream_b.stop_stream()
            self.out_stream_b.close()
            self.out_stream_b = None
            
        while not self.queue_a.empty(): self.queue_a.get()
        while not self.queue_b.empty(): self.queue_b.get()
        
        self.start_btn.configure(text="START ROUTING", fg_color="#E50914", hover_color="#B3040E", border_width=0, text_color="#FFFFFF")
        self.status_label.configure(text="Status: Inactive", text_color="#888888")
        self.status_led.configure(text_color="#888888")
        self.vis_a.set(0)
        self.vis_b.set(0)

if __name__ == "__main__":
    # This Windows API call forces the Taskbar to use our custom icon instead of the generic Python logo!
    import ctypes
    try:
        myappid = 'redz.bluetooth.router.1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = RedzbtApp()
    app.mainloop()
