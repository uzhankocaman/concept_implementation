# import tkinter as tk
# from tkinter import ttk
import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import threading
import queue
import time


class MonitoringUI:
    def __init__(self, data_queue):
        self.window = tk.Tk()
        self.window.title("Predictive Maintenance Monitoring System")
        self.data_queue = data_queue
        self.data_labels = {}
        self.data_points = {metric: [] for metric in ["Metric1", "Metric2"]}

        # Create labels for each metric
        for metric in self.data_points.keys():
            label = ttk.Label(
                self.window, text=f"{metric}: No data yet", font=("Arial", 12)
            )
            label.pack(pady=5)
            self.data_labels[metric] = label

        # Set up Matplotlib graph
        self.fig, self.ax = plt.subplots()
        self.lines = [self.ax.plot([], [])[0] for _ in range(len(self.data_labels))]
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

        # threading.Thread(target=self.fetch_data, args=(self.data_queue,), daemon=True).start()
        self.update_gui()

    # def fetch_data(self, queue):
    #     while True:
    #         data = {
    #             'Metric1': 30,
    #             'Metric2': 30
    #         }
    #         queue.put(data)
    #         time.sleep(0.5)

    def update_gui(self):
        try:
            while not self.data_queue.empty():
                data = self.data_queue.get()

                # Update labels and data points for the graph
                for key, label in self.data_labels.items():
                    value = data.get(key, "N/A")
                    label.config(text=f"{key}: {value}")

                    # Update data points
                    self.data_points[key].append(value)
                    if len(self.data_points[key]) > 50:
                        self.data_points[key].pop(0)

                # Update graph
                x_data = list(range(50))
                for line, key in zip(self.lines, self.data_labels.keys()):
                    y_data = self.data_points[key] + [None] * (
                        50 - len(self.data_points[key])
                    )
                    line.set_data(x_data, y_data)
                    self.ax.relim()
                    self.ax.autoscale_view()

                self.canvas.draw()

        finally:
            self.window.after(1000, self.update_gui)

    def run(self):
        self.window.mainloop()


# Create and run the monitoring UI
# monitoring_ui = MonitoringUI()
# monitoring_ui.run()
