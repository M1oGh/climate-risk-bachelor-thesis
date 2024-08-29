import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandastable import Table
from climate_risk_calc import controller
from climate_risk_calc.connections.limits_connection import LimitsConnection


class ScenarioExplorer(tk.Frame):
    """
    Class managing Scenario Explorer GUI and logic
    """

    def __init__(self, master):
        super().__init__(master, background="white")
        self.cbox_mode_picker = None
        self.lc = None
        self.plot_table_frame = None
        self.selection_frame = None
        self.scenario_picker = None

        self.file_name = tk.StringVar()
        self.file_name.set("Choose .csv")
        self.full_file_name = None
        self.mode = ""
        self.market_share_mode = "Market Shares"
        self.market_shock_plot_mode = "Market Shocks"
        self.loan_evaluation_mode = "Loan Evaluation"
        self.top_shock_mode = "Top Shocks"
        self.top_shock_df = None
        self.home_screen = None

    def initialize(self):
        self.lc = LimitsConnection()
        pd.set_option("display.float_format", "{:.2f}".format)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=2)
        self.rowconfigure(2, weight=7)

        # info bar
        info_bar = tk.Frame(self, background="lightblue")
        info_bar.columnconfigure(0, weight=1)
        info_bar.columnconfigure(1, weight=4)
        info_bar.columnconfigure(2, weight=1)
        info_bar.rowconfigure(0, weight=1)
        btn_back_home = tk.Button(
            info_bar,
            text="Home",
            command=lambda: controller.switch_view(self.home_screen),
        )
        btn_back_home.grid(row=0, column=2, padx=5, pady=5, sticky=tk.NSEW)
        info_bar.grid(row=0, column=1, sticky=tk.NSEW)

        # scenario picker
        self.scenario_picker = tk.Frame(self, background="lightgrey")
        self.scenario_picker.columnconfigure(0, weight=1)
        self.scenario_picker.columnconfigure(1, weight=5)
        self.scenario_picker.rowconfigure((0, 1), weight=1)

        # selection frame
        self.selection_frame = tk.Frame(self, background="lightgrey")
        self.selection_frame.columnconfigure(0, weight=1)
        self.selection_frame.columnconfigure(1, weight=6)
        self.selection_frame.rowconfigure((0, 1, 2, 3, 4), weight=1)

        lbl_model = tk.Label(
            self.selection_frame,
            text="Model: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_scenario = tk.Label(
            self.selection_frame,
            text="Scenario: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_variable = tk.Label(
            self.selection_frame,
            text="Variable: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_region = tk.Label(
            self.selection_frame,
            text="Region: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_model.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        lbl_scenario.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        lbl_variable.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        lbl_region.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        self.cbox_model = ttk.Combobox(self.selection_frame)
        self.cbox_model.configure(values=self.lc.get_models())
        self.cbox_scenario = ttk.Combobox(self.selection_frame)
        self.cbox_variable = ttk.Combobox(self.selection_frame)
        self.cbox_region = ttk.Combobox(self.selection_frame)
        btn_load_data = tk.Button(
            master=self.selection_frame,
            text="Load data",
            command=self.load_data,
            background="white",
            font="Arial 11",
            borderwidth=1,
            relief="solid",
        )
        self.cbox_model.bind("<<ComboboxSelected>>", self.fill_boxes)
        self.cbox_model.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=5)

        self.cbox_scenario.grid(row=1, column=1, sticky=tk.NSEW, padx=10, pady=5)
        self.cbox_variable.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=5)
        self.cbox_region.grid(row=3, column=1, sticky=tk.NSEW, padx=10, pady=5)
        btn_load_data.grid(
            row=4, column=0, sticky=tk.NSEW, padx=10, pady=5, columnspan=2
        )

        # selection frame loans
        self.selection_frame_loans = tk.Frame(self, background="lightgrey")
        self.selection_frame_loans.columnconfigure(0, weight=1)
        self.selection_frame_loans.columnconfigure(1, weight=6)
        self.selection_frame_loans.rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        self.selection_frame_loans.rowconfigure(6, weight=2)
        self.cbox_model_loans = ttk.Combobox(self.selection_frame_loans)
        self.cbox_model_loans.configure(values=self.lc.get_models())
        self.cbox_reference_scenario_loans = ttk.Combobox(self.selection_frame_loans)
        self.cbox_reference_scenario_loans.configure(
            values=[
                "LIMITS-RefPol-450",
                "LIMITS-RefPol-500",
                "LIMITS-StrPol-450",
                "LIMITS-StrPol-500",
            ]
        )
        self.year_slider = tk.Scale(
            self.selection_frame_loans,
            from_=2015,
            to=2100,
            resolution=5,
            orient=tk.HORIZONTAL,
        )
        self.rrate_slider = tk.Scale(
            self.selection_frame_loans,
            from_=0,
            to=1,
            orient=tk.HORIZONTAL,
            resolution=0.1,
            digits=2,
        )
        self.elasticity_slider = tk.Scale(
            self.selection_frame_loans,
            from_=0,
            to=2,
            orient=tk.HORIZONTAL,
            resolution=0.1,
            digits=2,
        )
        file_picker = tk.Button(
            master=self.selection_frame_loans,
            textvariable=self.file_name,
            background="white",
            command=self.set_file,
            font="Arial 11",
            borderwidth=1,
            relief="solid",
        )
        btn_load_data_loans = tk.Button(
            master=self.selection_frame_loans,
            text="Load Data",
            command=self.load_data,
            background="white",
            font="Arial 11",
            borderwidth=1,
            relief="solid",
        )
        lbl_model_loans = tk.Label(
            master=self.selection_frame_loans,
            text="Model: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_ref_scen_loans = tk.Label(
            master=self.selection_frame_loans,
            text="Reference scenario: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_year_loans = tk.Label(
            master=self.selection_frame_loans,
            text="Year of shock: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_rrate_loans = tk.Label(
            master=self.selection_frame_loans,
            text="Recovery rate: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_elasticity_loans = tk.Label(
            master=self.selection_frame_loans,
            text="Elasticity: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_file_picker_loans = tk.Label(
            master=self.selection_frame_loans,
            text="Credit portfolio: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_model_loans.grid(row=0, column=0, sticky="NSEW", padx=10, pady=10)
        lbl_ref_scen_loans.grid(row=1, column=0, sticky="NSEW", padx=10, pady=10)
        lbl_year_loans.grid(row=2, column=0, sticky="NSEW", padx=10, pady=10)
        lbl_rrate_loans.grid(row=3, column=0, sticky="NSEW", padx=10, pady=10)
        lbl_elasticity_loans.grid(row=4, column=0, sticky="NSEW", padx=10, pady=10)
        lbl_file_picker_loans.grid(row=5, column=0, sticky="NSEW", padx=10, pady=10)

        self.cbox_model_loans.grid(column=1, row=0, sticky="NSEW", padx=10, pady=10)
        self.cbox_reference_scenario_loans.grid(
            column=1, row=1, sticky="NSEW", padx=10, pady=10
        )
        self.year_slider.grid(column=1, row=2, sticky="NSEW", padx=10, pady=10)
        self.rrate_slider.grid(column=1, row=3, sticky="NSEW", padx=10, pady=10)
        self.elasticity_slider.grid(column=1, row=4, sticky="NSEW", padx=10, pady=10)
        file_picker.grid(column=1, row=5, sticky="NSEW", padx=10, pady=10)
        btn_load_data_loans.grid(
            column=0, row=6, sticky="NSEW", padx=10, pady=10, columnspan=2
        )

        # mode picker
        self.cbox_mode_picker = ttk.Combobox(
            self.scenario_picker,
            font="Arial 11",
        )
        self.cbox_mode_picker.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=10)
        self.cbox_mode_picker.bind("<<ComboboxSelected>>", self.switch_mode)
        self.cbox_mode_picker.configure(
            values=[
                self.market_share_mode,
                self.market_shock_plot_mode,
                self.loan_evaluation_mode,
                self.top_shock_mode,
            ]
        )
        self.mode_description = tk.StringVar()
        lbl_mode_description = tk.Label(
            master=self.scenario_picker, textvariable=self.mode_description
        )

        lbl_mode = tk.Label(
            self.scenario_picker,
            text="Mode: ",
            background="lightgrey",
            font="Arial 11",
        )
        lbl_mode.grid(column=0, row=0, sticky="NSEW", padx=10, pady=10)
        lbl_mode_description.grid(
            column=0, row=1, sticky="NSEW", padx=10, pady=10, columnspan=2
        )

        self.plot_table_frame = tk.Frame(self, background="white")
        self.plot_table_frame.rowconfigure(0, weight=1)
        self.plot_table_frame.columnconfigure(0, weight=1)

        self.scenario_picker.grid(row=0, column=0, sticky=tk.NSEW, rowspan=2)
        self.selection_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self.selection_frame_loans.grid(row=2, column=0, sticky=tk.NSEW)
        self.selection_frame.tkraise()
        self.plot_table_frame.grid(row=1, column=1, sticky=tk.NSEW, rowspan=2)
        self.plot_table_frame.grid_propagate(False)

    def plot_market_share(self):
        frame_ms = tk.Frame(self.plot_table_frame, background="white")
        frame_ms.columnconfigure(0, weight=1)
        frame_ms.rowconfigure(0, weight=5)
        frame_ms.rowconfigure(1, weight=1)
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, frame_ms)
        navigation_toolbar = NavigationToolbar2Tk(canvas, frame_ms)
        navigation_toolbar.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        canvas.get_tk_widget().grid(row=0, column=0, sticky=tk.NSEW)

        variables = [self.cbox_variable.get()]
        base_sector = str.rsplit(self.cbox_variable.get(), "|", 1)[0]
        variables.append(base_sector)

        dataframe = self.lc.execute_query(
            model=self.cbox_model.get(),
            scenario=self.cbox_scenario.get(),
            region=self.cbox_region.get(),
            variable=variables,
        )
        market_shares = crisk2.tools.calculator.get_market_shares(dataframe)
        crisk2.tools.graph_designer.graph_market_shares(
            market_shares, ax, self.cbox_variable.get()
        )
        canvas.draw()

        frame_ms.grid(row=0, column=0, sticky=tk.NSEW)
        frame_ms.tkraise()

    def plot_market_shocks(self):
        frame_ms = tk.Frame(self.plot_table_frame, background="white")
        frame_ms.columnconfigure(0, weight=1)
        frame_ms.rowconfigure(0, weight=5)
        frame_ms.rowconfigure(1, weight=1)
        fig, ax = plt.subplots()
        ax2 = ax.twinx()
        canvas = FigureCanvasTkAgg(fig, frame_ms)
        navigation_toolbar = NavigationToolbar2Tk(canvas, frame_ms)
        navigation_toolbar.grid(row=1, column=0, sticky=tk.NSEW, padx=5, pady=5)
        canvas.get_tk_widget().grid(row=0, column=0, sticky=tk.NSEW)

        variables = [self.cbox_variable.get()]
        base_sector = str.rsplit(self.cbox_variable.get(), "|", 1)[0]
        variables.append(base_sector)

        dataframe = self.lc.execute_query(
            model=self.cbox_model.get(),
            scenario=self.cbox_scenario.get(),
            region=self.cbox_region.get(),
            variable=variables,
        )
        market_shares = crisk2.tools.calculator.get_market_shares(dataframe)
        market_shocks = crisk2.tools.calculator.get_market_share_shocks(dataframe)

        crisk2.tools.graph_designer.graph_market_shocks(
            market_shares, market_shocks, self.cbox_scenario.get().split(","), ax, ax2
        )

        frame_ms.grid(row=0, column=0, sticky=tk.NSEW)
        frame_ms.tkraise()

    def evaluate_loans(self, rr, el, year, top=False, model=None, ref_scenario=None):
        if top:
            # save top shocks after calculating once
            if self.top_shock_df is None:
                df = crisk2.tools.calculator.get_top_shocks(
                    year=year,
                    file_name=self.full_file_name,
                    recovery_rate=rr,
                    elasticity=el,
                )
                # df = df.sort_values(by=["max_shock"], ascending=False)
                self.top_shock_df = df
                self.top_shock_df["total_neg"] = self.top_shock_df["total_neg"].astype(
                    str
                )
                self.top_shock_df["min_shock"] = self.top_shock_df["min_shock"].astype(
                    str
                )
                self.top_shock_df["project_VaR"] = self.top_shock_df[
                    "project_VaR"
                ].astype(str)

            else:
                df = self.top_shock_df
        else:
            df = crisk2.tools.calculator.get_shocks(
                model=model,
                ref_scenario=ref_scenario,
                recovery_rate=rr,
                elasticity=el,
                year=year,
                file_name=self.full_file_name,
            )
            df = df.sort_values(["shock"], ascending=False)
            df = df.round({"shock": 2})
            df["shock"] = df["shock"].astype(str)

        frame_ms = tk.Frame(self.plot_table_frame, background="white")
        pt = Table(parent=frame_ms, dataframe=df)
        pt.grid(row=1, column=1, sticky=tk.NSEW)
        pt.update()

        pt.show()
        pt.update()
        frame_ms.grid(row=0, column=0, sticky=tk.NSEW, rowspan=2)
        frame_ms.tkraise()
        pt.update()

    def fill_boxes(self, event):
        model = self.cbox_model.get()
        if self.mode == self.market_share_mode:
            self.cbox_scenario.configure(
                values=self.lc.get_scenarios(model) + ["Sample scenarios (3)"]
            )
            self.cbox_region.configure(values=self.lc.get_regions(model) + ["sample"])

            self.cbox_variable.configure(values=self.lc.get_energy_variables(model))

        elif self.mode == self.market_shock_plot_mode:
            self.cbox_scenario.configure(values=self.lc.get_scenario_comparisons())
            self.cbox_region.configure(values=self.lc.get_regions(model))
            self.cbox_variable.configure(values=self.lc.get_energy_variables(model))

    def load_data(self):
        """
        Calls desired method depending on chosen mode, e.g. Market share, climate shocks
        Checks if all parameters are selected.

        Returns: Nothing

        """
        if (
            self.mode == self.market_share_mode
            or self.mode == self.market_shock_plot_mode
        ):
            for C in {
                self.cbox_model,
                self.cbox_variable,
                self.cbox_scenario,
                self.cbox_region,
            }:
                if C.get() == "":
                    print("Faulty selection")
                    messagebox.showwarning(
                        message="Attributes can not be left empty!",
                        title="Selection error",
                    )
                    return
            if self.mode == self.market_share_mode:
                self.plot_market_share()

            if self.mode == self.market_shock_plot_mode:
                self.plot_market_shocks()
        elif self.mode == self.loan_evaluation_mode:
            self.evaluate_loans(
                model=self.cbox_model_loans.get(),
                ref_scenario=self.cbox_reference_scenario_loans.get(),
                rr=self.rrate_slider.get(),
                el=self.elasticity_slider.get(),
                year=int(self.year_slider.get()),
            )
        elif self.mode == self.top_shock_mode:
            self.evaluate_loans(
                rr=self.rrate_slider.get(),
                el=self.elasticity_slider.get(),
                year=int(self.year_slider.get()),
                top=True,
            )

    def switch_mode(self, event):
        self.mode = self.cbox_mode_picker.get()
        if (
            self.mode == self.market_share_mode
            or self.mode == self.market_shock_plot_mode
        ):
            self.selection_frame.tkraise()
            for C in {
                self.cbox_model,
                self.cbox_variable,
                self.cbox_scenario,
                self.cbox_region,
            }:
                C.set("")
            self.mode_description.set("Plot market shares")

        if self.mode == self.market_shock_plot_mode:
            self.mode_description.set("Plot market share shocks")

        elif self.mode == self.loan_evaluation_mode:
            self.selection_frame_loans.tkraise()
            self.cbox_model_loans.set("")
            self.cbox_model_loans.configure(state="normal")
            self.cbox_reference_scenario_loans.set("")
            self.cbox_reference_scenario_loans.configure(state="normal")
            self.rrate_slider.set(0)
            self.year_slider.set("2030")
            self.elasticity_slider.set(1)
            self.mode_description.set("Table of potential losses")

        elif self.mode == self.top_shock_mode:
            self.selection_frame_loans.tkraise()
            self.cbox_model_loans.set("")
            self.cbox_model_loans.configure(state="disabled")
            self.cbox_reference_scenario_loans.set("")
            self.cbox_reference_scenario_loans.configure(state="disabled")
            self.rrate_slider.set(0)
            self.year_slider.set("2030")
            self.elasticity_slider.set(1)
            self.mode_description.set(
                "Table of top negative and positive shocks on loans"
            )

    def set_home_screen(self, frame):
        self.home_screen = frame

    def set_file(self):
        self.full_file_name = askopenfilename()
        self.file_name.set(self.full_file_name.rsplit("/", 1)[1])
        if self.file_name.get().rsplit(".", 1)[1] != "csv":
            messagebox.showwarning(
                message="Select a CSV-file!",
                title="File type error",
            )
            self.file_name.set("")
            self.full_file_name = ""
            return
        df = pd.read_csv(self.full_file_name, encoding="UTF-8")
        if not df.columns.values.tolist() == ["region", "sector", "amount"]:
            messagebox.showwarning(
                message="Loan portfolio must have format [region, sector, amount]!",
                title="Format error",
            )
