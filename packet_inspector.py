import tkinter as tk
from tkinter import ttk
import speedtest
import threading
import json
import os
from datetime import datetime

class PacketInspectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Packet Inspector")
        self.create_widgets()
        self.history_file = "packet_inspector_history.json"
        self.load_history()

    def create_widgets(self):
        self.title_label = tk.Label(self.root, text="Packet Inspector", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        self.test_button = tk.Button(self.root, text="Run Speed Test", command=self.start_speed_test)
        self.test_button.pack(pady=10)

        self.result_text = tk.StringVar()
        self.result_label = tk.Label(self.root, textvariable=self.result_text, font=("Helvetica", 12))
        self.result_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(pady=10, fill=tk.X)

        self.history_label = tk.Label(self.root, text="Test History:", font=("Helvetica", 12))
        self.history_label.pack(pady=10)

        self.history_text = tk.StringVar()
        self.history_display = tk.Label(self.root, textvariable=self.history_text, font=("Helvetica", 10))
        self.history_display.pack(pady=10)

    def start_speed_test(self):
        self.result_text.set("Testing...")
        self.progress.start()
        self.test_button.config(state=tk.DISABLED)

        # Run the speed test in a separate thread
        threading.Thread(target=self.run_speed_test).start()

    def run_speed_test(self):
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            ping = st.results.ping

            result = (f"Download Speed: {download_speed:.2f} Mbps\n"
                      f"Upload Speed: {upload_speed:.2f} Mbps\n"
                      f"Ping: {ping:.2f} ms\n\n"
                      "Speed Test Results:\n"
                      f"- Download Speed: {download_speed:.2f} Mbps ({'Good' if download_speed > 100 else 'Needs Improvement'})\n"
                      f"- Upload Speed: {upload_speed:.2f} Mbps ({'Good' if upload_speed > 100 else 'Needs Improvement'})\n"
                      f"- Ping: {ping:.2f} ms ({'Excellent' if ping < 20 else 'Acceptable' if ping < 50 else 'High Latency'})")

            # Save the result to history
            self.save_to_history(download_speed, upload_speed, ping)

        except Exception as e:
            result = f"An error occurred: {e}"

        self.update_result(result)

    def update_result(self, result):
        self.result_text.set(result)
        self.progress.stop()
        self.test_button.config(state=tk.NORMAL)

    def save_to_history(self, download_speed, upload_speed, ping):
        record = {
            "timestamp": datetime.now().isoformat(),
            "download_speed": download_speed,
            "upload_speed": upload_speed,
            "ping": ping
        }
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                history = json.load(file)
        else:
            history = []
        history.append(record)
        with open(self.history_file, "w") as file:
            json.dump(history, file, indent=4)
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                history = json.load(file)
            history_display = "\n".join([f"{entry['timestamp']}: Download {entry['download_speed']:.2f} Mbps, "
                                        f"Upload {entry['upload_speed']:.2f} Mbps, Ping {entry['ping']} ms"
                                        for entry in history])
            self.history_text.set(history_display)
        else:
            self.history_text.set("No history available.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PacketInspectorApp(root)
    root.geometry("500x400")
    root.mainloop()
