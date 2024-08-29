import tkinter as tk
from tkinter import ttk
import crisk2.views.v_scenario_explorer as scenario_explorer
import crisk2.views.v_data_explorer as data_explorer
from crisk2 import controller


class HomeScreen(tk.Frame):
    """
    Class managing Homescreen GUI and logic
    """

    def __init__(self, master):
        super().__init__(master, background="white")
        self.master = master

    def initialize(self):
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=5)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=2)
        self.rowconfigure(4, weight=1)
        dataexplorer = data_explorer.DataExplorer(self.master)
        scenexplorer = scenario_explorer.ScenarioExplorer(self.master)

        lbl_title = ttk.Label(
            self,
            text="Climate risk calculator",
            font=("Arial", 30),
            background="white",
            anchor="w",
        )
        btn_to_dataexplorer = ttk.Button(
            self,
            text="Data Explorer",
            command=lambda: controller.switch_view(dataexplorer),
        )
        btn_to_scenarioexplorer = ttk.Button(
            self,
            text="Mode Explorer",
            command=lambda: controller.switch_view(scenexplorer),
        )
        lbl_dataexplorer = tk.Label(
            self,
            background="white",
            text="Explore data from different sources in graph or table format",
            font=("Arial", 10),
            wraplength=700,
            justify="left",
            anchor="nw",
        )
        lbl_scenexplorer = tk.Label(
            self,
            background="white",
            text="Explore different scenarios like market share change, shocks on market share and effects on credit portfolios",
            font=("Arial", 10),
            wraplength=700,
            justify="left",
            anchor="nw",
        )
        lbl_background = tk.Label(
            self,
            text="Program created for Bachelor Thesis by Henri Dannenhöfer",
            font=("Arial", 12),
            background="white",
            anchor="w",
        )

        btn_to_dataexplorer.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)
        lbl_title.grid(row=0, column=1, sticky=tk.NSEW, padx=5, pady=5)
        btn_to_scenarioexplorer.grid(row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)
        lbl_dataexplorer.grid(row=1, column=2, sticky=tk.NSEW, padx=5, pady=5)
        lbl_scenexplorer.grid(row=2, column=2, sticky=tk.NSEW, padx=5, pady=5)
        lbl_background.grid(row=0, column=2, sticky=tk.NSEW, padx=5, pady=5)

        dataexplorer.initialize()
        dataexplorer.grid(row=0, column=0, sticky="nsew")
        dataexplorer.set_home_screen(self)
        scenexplorer.initialize()
        scenexplorer.grid(row=0, column=0, sticky="nsew")
        scenexplorer.set_home_screen(self)
        self.tkraise()
