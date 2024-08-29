import tkinter as tk
from tkinter import ttk

from crisk2.views.v_data_explorer import DataExplorer
from crisk2.views.v_home_screen import HomeScreen
from crisk2.views.v_scenario_explorer import ScenarioExplorer


def start_view():
    root = tk.Tk()
    style = ttk.Style(root)
    style.configure(style="TButton", font="Arial 13")
    root.geometry("1800x900")
    root.update_idletasks()
    root.title("Climate Risk Calculator")
    root.option_add("*Font", "Arial 11")
    root.resizable(False, False)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame = HomeScreen(root)
    frame.initialize()
    frame.grid(row=0, column=0, sticky="nsew")
    frame.tkraise()
    root.mainloop()
    print("[INFO] Program terminated")


def switch_view(new_view):
    new_view.tkraise()
