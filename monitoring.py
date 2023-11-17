import tkinter as tk
from tkinter import ttk
import random
import threading
import queue
import time

def fetch_data(queue):
    while True:
        data = random.randint(1, 100)
        queue.put(data)
        time.sleep(1)

def update_gui(window, queue, data_label):
    try:
        while not queue.empty():
            data = queue.get()
            data_label.config(text=str(data))
    finally:
        window.after(1000, update_gui, window, queue, data_label)

window = tk.Tk()
window.title("Predictive Maintenance Monitoring System")

data_label = ttk.Label(window, text="No data yet", font=('Arial', 24))
data_label.pack(pady=20)

data_queue = queue.Queue()

threading.Thread(target=fetch_data, args=(data_queue,), daemon=True).start()

update_gui(window, data_queue, data_label)

window.mainloop()
