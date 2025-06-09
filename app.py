# this is the main file for the alarm data app
# using tkinter to get user input and save the alarm data in a csv file
from model import DailyWorker
import tkinter as tk


worker = DailyWorker()

# get start date and end date from user input with tkinter gui
root = tk.Tk()
root.title("Alarm Data")
root.geometry("300x150")
root.resizable(False, False)
start_date_label = tk.Label(root, text="Start Date (YYYYMMDD):")
start_date_label.pack()
start_date_entry = tk.Entry(root)
start_date_entry.pack()
end_date_label = tk.Label(root, text="End Date (YYYYMMDD):")
end_date_label.pack()
end_date_entry = tk.Entry(root)
end_date_entry.pack()


def get_alarm_data():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()

    # get alarm data
    result = worker.get_alarm_data_in_range(start_date, end_date)

get_data_button = tk.Button(root, text="Get Data", command=get_alarm_data)
get_data_button.pack()

if __name__ == "__main__":
    root.mainloop()
