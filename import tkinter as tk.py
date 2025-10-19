import tkinter as tk
from tkinter import filedialog, messagebox
from pynput import mouse, keyboard
import time, pickle, threading, os

class MouseRecorderGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("RMS Mouse Recorder")
        self.master.geometry("420x380")
        self.master.configure(bg="#1e1e1e")

        self.recording = False
        self.playing = False
        self.events = []
        self.last_time = None
        self.listener_mouse = None
        self.keyboard_listener = None
        self.play_thread = None

        # --- GUI Elements ---
        self.title_label = tk.Label(master, text="Mouse Recorder", fg="white", bg="#1e1e1e", font=("Segoe UI", 16, "bold"))
        self.title_label.pack(pady=10)

        self.status_label = tk.Label(master, text="Status: Idle", fg="lightgray", bg="#1e1e1e", font=("Segoe UI", 12))
        self.status_label.pack(pady=5)

        frame = tk.Frame(master, bg="#1e1e1e")
        frame.pack(pady=10)

        self.btn_load = tk.Button(frame, text="Load .rms", command=self.load_file, width=12, bg="#333", fg="white")
        self.btn_load.grid(row=0, column=0, padx=5)

        self.btn_save = tk.Button(frame, text="Save .rms", command=self.save_file, width=12, bg="#333", fg="white")
        self.btn_save.grid(row=0, column=1, padx=5)

        self.info_label = tk.Label(master, text="Hotkeys:\nF9 = Record / Stop\nF10 = Play / Stop",
                                   fg="#BBBBBB", bg="#1e1e1e", font=("Segoe UI", 10))
        self.info_label.pack(pady=10)

        # --- Repeat Options ---
        self.repeat_label = tk.Label(master, text="Playback Repeat Options:", fg="white", bg="#1e1e1e", font=("Segoe UI", 12, "bold"))
        self.repeat_label.pack()

        repeat_frame = tk.Frame(master, bg="#1e1e1e")
        repeat_frame.pack(pady=8)

        self.repeat_mode = tk.StringVar(value="once")

        tk.Radiobutton(repeat_frame, text="Once", variable=self.repeat_mode, value="once", bg="#1e1e1e", fg="white", selectcolor="#333").grid(row=0, column=0, sticky="w")
        tk.Radiobutton(repeat_frame, text="Repeat (x times)", variable=self.repeat_mode, value="count", bg="#1e1e1e", fg="white", selectcolor="#333").grid(row=1, column=0, sticky="w")
        tk.Radiobutton(repeat_frame, text="Repeat for duration (sec)", variable=self.repeat_mode, value="duration", bg="#1e1e1e", fg="white", selectcolor="#333").grid(row=2, column=0, sticky="w")
        tk.Radiobutton(repeat_frame, text="Until Stopped", variable=self.repeat_mode, value="until_stop", bg="#1e1e1e", fg="white", selectcolor="#333").grid(row=3, column=0, sticky="w")

        self.entry_count = tk.Entry(repeat_frame, width=8)
        self.entry_count.insert(0, "3")
        self.entry_count.grid(row=1, column=1, padx=5)

        self.entry_duration = tk.Entry(repeat_frame, width=8)
        self.entry_duration.insert(0, "10")
        self.entry_duration.grid(row=2, column=1, padx=5)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Global keyboard listener
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    # ---------------- Record / Play Functions ----------------
    def on_click(self, x, y, button, pressed):
        if not self.recording:
            return
        if pressed:
            now = time.time()
            delay = 0 if self.last_time is None else now - self.last_time
            self.last_time = now
            self.events.append((x, y, str(button), delay))
            print(f"Recorded click: {button} at ({x},{y}) after {delay:.2f}s")

    def start_recording(self):
        if self.recording:
            return
        self.recording = True
        self.events = []
        self.last_time = None
        self.status_label.config(text="Status: Recording...", fg="#00FF00")
        self.listener_mouse = mouse.Listener(on_click=self.on_click)
        self.listener_mouse.start()
        print("Recording started...")

    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        if self.listener_mouse:
            self.listener_mouse.stop()
        self.status_label.config(text="Status: Recording Stopped", fg="#FFCC00")
        print("Recording stopped.")

    def play_events(self):
        from pynput.mouse import Controller, Button
        if not self.events:
            messagebox.showinfo("No Data", "No recorded clicks to play.")
            return

        def _play():
            self.playing = True
            self.status_label.config(text="Status: Playing...", fg="#00FFFF")
            mouse_ctrl = Controller()

            mode = self.repeat_mode.get()
            count = int(self.entry_count.get()) if self.entry_count.get().isdigit() else 1
            duration = float(self.entry_duration.get()) if self.entry_duration.get().replace('.', '', 1).isdigit() else 10
            start_time = time.time()
            loop_counter = 0

            while self.playing:
                for x, y, btn, delay in self.events:
                    if not self.playing:
                        break
                    time.sleep(delay)
                    button = Button.left if "left" in btn else Button.right
                    mouse_ctrl.position = (x, y)
                    mouse_ctrl.click(button)

                loop_counter += 1

                if mode == "once":
                    break
                elif mode == "count" and loop_counter >= count:
                    break
                elif mode == "duration" and (time.time() - start_time) >= duration:
                    break
                elif mode == "until_stop":
                    continue  # Keep looping until manually stopped

            self.playing = False
            self.status_label.config(text="Status: Idle", fg="lightgray")

        self.play_thread = threading.Thread(target=_play, daemon=True)
        self.play_thread.start()

    def stop_playing(self):
        if self.playing:
            self.playing = False
            self.status_label.config(text="Status: Playback Stopped", fg="#FF6666")
            print("Playback stopped.")

    # ---------------- File Handling ----------------
    def save_file(self):
        if not self.events:
            messagebox.showinfo("No Data", "No recorded data to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".rms",
                                                 filetypes=[("RMS Files", "*.rms")])
        if file_path:
            with open(file_path, "wb") as f:
                pickle.dump(self.events, f)
            messagebox.showinfo("Saved", f"File saved to {file_path}")

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("RMS Files", "*.rms")])
        if file_path and os.path.exists(file_path):
            with open(file_path, "rb") as f:
                self.events = pickle.load(f)
            messagebox.showinfo("Loaded", f"Loaded {len(self.events)} recorded clicks.")

    # ---------------- Keyboard Hotkeys ----------------
    def on_key_press(self, key):
        try:
            if key == keyboard.Key.f9:
                if not self.recording:
                    self.start_recording()
                else:
                    self.stop_recording()
            elif key == keyboard.Key.f10:
                if not self.playing:
                    self.play_events()
                else:
                    self.stop_playing()
        except Exception as e:
            print(f"Error in key handler: {e}")

    def on_close(self):
        self.stop_recording()
        self.stop_playing()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MouseRecorderGUI(root)
    root.mainloop()
