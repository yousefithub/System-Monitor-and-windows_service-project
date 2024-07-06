import psutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
import smtplib, ssl
from email.mime.base import MIMEBase
from email import encoders
import email.utils
import tempfile
import os

class SystemMonitor:
    def __init__(self, master):
        self.master = master
        master.title("System Monitor")

        # Performance Counters
        self.cpu_percent = psutil.cpu_percent(interval=1)
        self.memory_percent = psutil.virtual_memory().percent
        self.disk_percent = psutil.disk_usage("/").percent
        self.sent_bytes = 0
        self.received_bytes = 0
        self.io_flag = 0

        # Labels
        self.cpu_label = Label(master, text="CPU Usage:")
        self.cpu_label.grid(row=0, column=0, sticky=W)
        self.cpu_percent_label = Label(master, text=f"{self.cpu_percent}%")
        self.cpu_percent_label.grid(row=0, column=1, sticky=W)

        self.memory_label = Label(master, text="Memory Usage:")
        self.memory_label.grid(row=1, column=0, sticky=W)
        self.memory_percent_label = Label(master, text=f"{self.memory_percent}%")
        self.memory_percent_label.grid(row=1, column=1, sticky=W)

        self.disk_label = Label(master, text="Disk Usage:")
        self.disk_label.grid(row=2, column=0, sticky=W)
        self.disk_percent_label = Label(master, text=f"{self.disk_percent}%")
        self.disk_percent_label.grid(row=2, column=1, sticky=W)

        self.network_label = Label(master, text="Network:")
        self.network_label.grid(row=3, column=0, sticky=W)
        self.network_info_label = Label(master, text="S: 0.00 R: 0.00 Kbps")
        self.network_info_label.grid(row=3, column=1, sticky=W)

        # Graphs
        self.fig, self.ax = plt.subplots(figsize=(6, 2), dpi=100)
        self.ax.set_ylim(0, 100)
        (self.cpu_plot,) = self.ax.plot([], [], color="blue", label="CPU")
        (self.memory_plot,) = self.ax.plot([], [], color="green", label="Memory")
        (self.disk_plot,) = self.ax.plot([], [], color="red", label="Disk")
        self.ax.legend(loc="upper right")
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=4, padx=10, pady=10)

        # Animation
        self.animation = FuncAnimation(
            self.fig, self.update_graph, frames=100, interval=1000
        )

    def update_info(self):
        # Update system performance information
        self.cpu_percent = psutil.cpu_percent(interval=1)
        self.memory_percent = psutil.virtual_memory().percent
        self.disk_percent = psutil.disk_usage("/").percent

        # Calculate network usage
        net_io = psutil.net_io_counters()
        sent_bytes_diff = net_io.bytes_sent - self.sent_bytes
        received_bytes_diff = net_io.bytes_recv - self.received_bytes
        self.sent_bytes = net_io.bytes_sent
        self.received_bytes = net_io.bytes_recv

        # Update labels with new information
        self.cpu_percent_label.config(text=f"{self.cpu_percent:.2f}%")
        self.memory_percent_label.config(text=f"{self.memory_percent:.2f}%")
        self.disk_percent_label.config(text=f"{self.disk_percent:.2f}%")
        self.network_info_label.config(
            text=f"S: {sent_bytes_diff / 1024:.2f} R: {received_bytes_diff / 1024:.2f} Kbps"
        )

        # Save data to file and send email (only once)
        self.save_data_to_file()
        if self.io_flag == 0:
            self.send_mail()
            self.io_flag += 1

    def save_data_to_file(self):
        # Save system performance data to a temporary file
        data = (
            f"CPU Usage: {self.cpu_percent}%\nMemory Usage: {self.memory_percent}%\nDisk Usage: {self.disk_percent}%\n"
            f"Sent Bytes: {self.sent_bytes} bytes\nReceived Bytes: {self.received_bytes} bytes"
        )
        self.temp_file_path = os.path.join(tempfile.gettempdir(), "PC_workload_data.txt")
        with open(self.temp_file_path, "w") as temp_file:
            temp_file.write(data)

    def send_mail(self):
        # Send an email with the system performance data as an attachment
        port = 587  # For starttls
        smtp_server = "smtp-mail.outlook.com"
        sender_email = "yousefeltahawy@hotmail.com"
        receiver_email = "yousef.eltahawy@ejust.edu.eg"
        password = "yousef12345670"
        filename = self.temp_file_path
        message = MIMEMultipart("alternative")
        message["From"] = email.utils.formataddr(("no-reply service", sender_email))
        message["To"] = receiver_email
        message["Subject"] = "PC Workload"
        message.attach(MIMEText("PC Workload File Attached Below ↓↓", "plain"))
        with open(filename, "rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            "attachment; filename=PC_workload_data.txt",
        )
        message.attach(part)
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())

    def update_graph(self, frame):
        # Update the graph with new system performance data
        self.update_info()
        self.cpu_plot.set_xdata(range(len(self.cpu_plot.get_ydata()) + 1))
        self.cpu_plot.set_ydata(list(self.cpu_plot.get_ydata()) + [self.cpu_percent])
        self.memory_plot.set_xdata(range(len(self.memory_plot.get_ydata()) + 1))
        self.memory_plot.set_ydata(
            list(self.memory_plot.get_ydata()) + [self.memory_percent]
        )
        self.disk_plot.set_xdata(range(len(self.disk_plot.get_ydata()) + 1))
        self.disk_plot.set_ydata(list(self.disk_plot.get_ydata()) + [self.disk_percent])
        self.ax.relim()
        self.ax.autoscale_view(True, True, True)
        self.canvas.draw()

def main():
    root = Tk()
    monitor = SystemMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
