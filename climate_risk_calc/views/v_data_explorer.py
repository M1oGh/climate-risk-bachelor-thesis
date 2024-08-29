import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from pandastable import Table

from climate_risk_calc import controller
from climate_risk_calc.connections.iiasa_connection import IIASAConnection
from climate_risk_calc.connections.limits_connection import LimitsConnection

font = "Arial 9"


class DataExplorer(tk.Frame):
    """
    Class managing Data Explorer GUI and logic
    """

    def __init__(self, master):
        super().__init__(master, background="white")
        self.btn_data_viewer = None
        self.placeholder = None
        self.graph_screen = None
        self.table_screen = None
        self.plot_screen = None
        self.cbox_region2 = None
        self.cbox_region = None
        self.cbox_variable = None
        self.cbox_scenario = None
        self.cbox_model = None
        self.cbox_source = None
        self.info_bar = None
        self.ic = None
        self.lc = None
        self.graph_view = "G"
        self.table_view = "T"
        self.current_view = self.graph_view
        self.home_screen = None

    def initialize(self):
        self.ic = IIASAConnection()
        self.lc = LimitsConnection()
        self.view_switch_button_text = tk.StringVar()
        self.view_switch_button_text.set("Switch to Table")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=20)

        var_selection = tk.Frame(
            self,
            background="lightgrey",
            highlightbackground="darkgrey",
            highlightthickness=1,
        )
        self.info_bar = tk.Frame(
            self,
            background="lightblue",
            highlightbackground="darkgrey",
            highlightthickness=1,
        )
        self.plot_screen = tk.Frame(
            self,
            background="white",
            highlightbackground="darkgrey",
            highlightthickness=1,
        )

        # Selection screen configuring
        var_selection.rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)
        var_selection.columnconfigure(0, weight=1)
        var_selection.columnconfigure(1, weight=6)

        self.plot_screen.rowconfigure(0, weight=6)
        self.plot_screen.rowconfigure(1, weight=1)
        self.plot_screen.columnconfigure(0, weight=1)
        self.placeholder = tk.Frame(master=self.plot_screen, background="white")
        self.graph_screen = tk.Frame(master=self.plot_screen, background="white")
        self.graph_screen.rowconfigure(0, weight=6)
        self.graph_screen.rowconfigure(1, weight=1)
        self.graph_screen.columnconfigure(0, weight=1)

        self.table_screen = tk.Frame(master=self.plot_screen, background="white")
        self.placeholder.grid(row=0, column=0, sticky="nsew")
        self.graph_screen.grid(row=0, column=0, sticky="nsew")
        self.table_screen.grid(row=0, column=0, sticky="nsew")
        self.placeholder.tkraise()
        self.placeholder.tkraise()

        self.info_bar.rowconfigure(0, weight=1)
        self.info_bar.columnconfigure(0, weight=1)
        self.info_bar.columnconfigure(1, weight=3)
        self.info_bar.columnconfigure(2, weight=1)

        self.cbox_source = ttk.Combobox(var_selection, values=["LIMITS", "IIASA"])
        self.cbox_source.bind("<<ComboboxSelected>>", self.fill_boxes)

        self.cbox_model = ttk.Combobox(var_selection)
        self.cbox_scenario = ttk.Combobox(var_selection)
        self.cbox_variable = ttk.Combobox(var_selection)
        self.cbox_region = ttk.Combobox(var_selection)
        self.cbox_region.bind("<<ComboboxSelected>>", self.disable_region2)
        self.cbox_region2 = ttk.Combobox(var_selection)
        btn_load_data = tk.Button(
            var_selection,
            text="Load data",
            command=lambda: self.on_load(
                model_=self.cbox_model.get(),
                scenario_=self.cbox_scenario.get(),
                variable_=self.cbox_variable.get(),
                regions_=[self.cbox_region.get(), self.cbox_region2.get()],
            ),
            background="white",
            font="Arial 11",
            borderwidth=1,
            relief="solid",
        )
        px, py = 15, 10
        self.cbox_source.grid(row=0, column=1, sticky="nsew", padx=px, pady=py)
        self.cbox_model.grid(row=1, column=1, sticky="nsew", padx=px, pady=py)
        self.cbox_variable.grid(row=2, column=1, sticky="nsew", padx=px, pady=py)
        self.cbox_scenario.grid(row=3, column=1, sticky="nsew", padx=px, pady=py)
        self.cbox_region.grid(row=4, column=1, sticky="nsew", padx=px, pady=py)
        self.cbox_region2.grid(row=5, column=1, sticky="nsew", padx=px, pady=py)
        btn_load_data.grid(
            row=6, column=0, sticky="nsew", padx=px, pady=py, columnspan=2
        )

        # Labels
        lbl_source = ttk.Label(
            var_selection,
            text="Data source: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_source.grid(row=0, column=0, sticky="nsew", padx=px, pady=py)
        lbl_model = ttk.Label(
            var_selection,
            text="Project: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_model.grid(row=1, column=0, sticky="nsew", padx=px, pady=py)
        lbl_variable = ttk.Label(
            var_selection,
            text="Variable: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_variable.grid(row=2, column=0, sticky="nsew", padx=px, pady=py)
        lbl_scenario = ttk.Label(
            var_selection,
            text="Scenario: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_scenario.grid(row=3, column=0, sticky="nsew", padx=px, pady=py)
        lbl_region = ttk.Label(
            var_selection,
            text="Region: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_region.grid(row=4, column=0, sticky="nsew", padx=px, pady=py)
        lbl_region2 = ttk.Label(
            var_selection,
            text="Region #2: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_region2.grid(row=5, column=0, sticky="nsew", padx=px, pady=py)

        lbl_info = tk.Label(
            master=self.info_bar,
            text="",
            font="Arial 11",
            background="lightblue",
        )
        lbl_info.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        btn_back_home = tk.Button(
            master=self.info_bar,
            text="Home",
            background="white",
            command=lambda: controller.switch_view(self.home_screen),
            font="Arial 11",
        )
        btn_back_home.grid(row=0, column=2, sticky="nsew", padx=5, pady=3)
        btn_data_viewer = tk.Button(
            master=self.info_bar,
            textvariable=self.view_switch_button_text,
            background="white",
            command=self.switch_view,
            font="Arial 11",
        )
        btn_data_viewer.grid(row=0, column=0, sticky="nsew", padx=5, pady=3)

        var_selection.grid(row=0, column=0, sticky=tk.NSEW, rowspan=2)
        self.info_bar.grid(row=0, column=1, sticky=tk.NSEW)
        self.plot_screen.grid(row=1, column=1, sticky=tk.NSEW)
        self.plot_screen.grid_propagate(False)

    def on_load(self, model_, scenario_, variable_, regions_):
        self.graph_screen.rowconfigure(0, weight=6)
        self.graph_screen.rowconfigure(1, weight=1)
        self.graph_screen.columnconfigure(0, weight=1)
        self.placeholder.grid(row=0, column=0, sticky="nsew")
        self.graph_screen.grid(row=0, column=0, sticky="nsew")
        self.table_screen.grid(row=0, column=0, sticky="nsew")
        self.placeholder.tkraise()
        self.placeholder.tkraise()

        # check if input is valid
        for C in {
            self.cbox_source,
            self.cbox_model,
            self.cbox_variable,
            self.cbox_scenario,
            self.cbox_region,
        }:
            if C.get() == "":
                print("Faulty selection")
                messagebox.showwarning(
                    message="Attributes can not be left empty!", title="Selection error"
                )
                return

        if regions_[1] == "":
            regions_ = regions_[0]

        # get data as IamDataFrame
        df = None
        if self.cbox_source.get() == "IIASA":
            df = self.ic.execute_query(
                model=model_, scenario=scenario_, variable=variable_, region=regions_
            )
        elif self.cbox_source.get() == "LIMITS":
            df = self.lc.execute_query(
                model=model_, scenario=scenario_, variable=variable_, region=regions_
            )
        if df is None:
            messagebox.showwarning(
                message="Dataframe is empty!", title="Empty dataframe"
            )
            return
        if self.current_view == self.graph_view:
            fig, ax = plt.subplots()
            ax.clear()
            canvas = FigureCanvasTkAgg(figure=fig, master=self.graph_screen)
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            toolbar_frame = tk.Frame(master=self.plot_screen, background="white")
            toolbar_frame.rowconfigure(0, weight=1)
            toolbar_frame.columnconfigure(0, weight=1)
            toolbar_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

            navigation_toolbar = NavigationToolbar2Tk(
                canvas=canvas, window=toolbar_frame
            )
            navigation_toolbar.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
            title = model_ + ", " + scenario_ + ", " + regions_ + ", " + variable_
            crisk2.tools.graph_designer.simple_graph(df, ax, title, "solid")
            canvas.draw()
            self.graph_screen.tkraise()
            self.graph_screen.tkraise()
        elif self.current_view == self.table_view:
            pt = Table(
                parent=self.table_screen,
                dataframe=df.data.sort_values(
                    ["region", "year"], ascending=[True, True]
                ),
            )
            pt.grid(row=1, column=1, sticky=tk.NSEW)
            pt.show()
            pt.update()
            self.table_screen.tkraise()
            self.table_screen.tkraise()
            pt.update()

    def fill_boxes(self, event):
        con = None
        for C in {
            self.cbox_model,
            self.cbox_variable,
            self.cbox_scenario,
            self.cbox_region,
            self.cbox_region2,
        }:
            C.set("")
        if self.cbox_source.get() == "IIASA":
            con = self.ic
            self.cbox_model.configure(values=con.get_models())
            self.cbox_scenario.configure(values=con.get_scenarios() + ["All"])
            self.cbox_variable.configure(values=con.get_variables())
            self.cbox_region.configure(values=con.get_regions() + ["All"])
            self.cbox_region2.configure(values=con.get_regions())
        elif self.cbox_source.get() == "LIMITS":
            con = self.lc
            self.cbox_model.configure(values=con.get_models())
            self.cbox_scenario.configure(values=con.get_scenarios() + ["All"])
            self.cbox_variable.configure(values=con.get_energy_variables())
            self.cbox_region.configure(values=con.get_regions() + ["All", "Sample"])
            self.cbox_region2.configure(values=con.get_regions())

    def switch_view(self):
        if self.current_view == self.graph_view:
            self.current_view = self.table_view
            self.view_switch_button_text.set("Switch to Graph")
        else:
            self.current_view = self.graph_view
            self.view_switch_button_text.set("Switch to Table ")

    def disable_region2(self, event):
        if self.cbox_region.get().lower() in ["all", "sample"]:
            self.cbox_region2.configure(state="disabled")
            self.cbox_region2.set("")
        else:
            self.cbox_region2.configure(state="normal")

    def set_home_screen(self, frame):
        self.home_screen = frame
