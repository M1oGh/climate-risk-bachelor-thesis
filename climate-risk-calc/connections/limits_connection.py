import os
import pandas as pd
import pyam


class LimitsConnection:
    wildcard = "all"

    def __init__(self):
        df = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "LIMITS.csv"),
            encoding="cp1252",
            na_filter=False,
        )
        self.limits_dataframe = pyam.IamDataFrame(df)

    def get_models(self):
        """
        Returns: list of models from the LIMITS project/database
        """
        return self.limits_dataframe.data["model"].unique().tolist()

    def get_scenarios(self, model=None):
        """
        Args:
            model: model for which to get scenarios
        Returns: list of scenarios
        """
        if model is None:
            df = self.limits_dataframe.data["scenario"].unique().tolist()
            df = [
                e
                for e in df
                if "-EE" not in e and "-PC" not in e and "2030-500" not in e
            ]
            return df

        df = (
            self.limits_dataframe.data.query("model == @model")["scenario"]
            .unique()
            .tolist()
        )
        df = [
            e for e in df if "-EE" not in e and "-PC" not in e and "2030-500" not in e
        ]

        return df

    def get_regions(self, model=None):
        """
        Args:
            model: model for which to get regions
        Returns: list of regions
        """

        if model is None:
            return self.limits_dataframe.data["region"].unique().tolist()

        return (
            self.limits_dataframe.data.query("model == @model")["region"]
            .unique()
            .tolist()
        )

    def get_energy_variables(self, model=None):
        """
        Args:
            model: model for which to get variables related to energy sectors
        Returns: list of energy variables
        """
        if model is None:
            vars = self.limits_dataframe.data["variable"].unique().tolist()
            vars.sort()
            vars = [v for v in vars if "Energy" in v]
            return vars

        vars = (
            self.limits_dataframe.data.query("model == @model")["variable"]
            .unique()
            .tolist()
        )
        vars.sort()
        vars = [v for v in vars if "Energy" in v]
        return vars

    def get_sample_regions(self):
        """
        Returns: list of a sample of regions across the world
        """
        return [
            "AFRICA",
            "CHINA+",
            "EUROPE",
            "INDIA+",
            "LATIN_AM",
            "MIDDLE_EAST",
            "NORTH_AM",
            "PAC_OECD",
            "REF_ECON",
            "REST_ASIA",
        ]

    def get_sample_scenarios(self):
        """
        Returns: list of sample scenarios
        """
        return ["LIMITS-Base", "LIMITS-RefPol-500", "LIMITS-StrPol-450"]

    def get_scenario_comparisons(self):
        """
        Returns: List of scenario tuples for comparisons in market shock calculation
        """
        return [
            "LIMITS-Base,LIMITS-RefPol-500",
            "LIMITS-Base,LIMITS-RefPol-450",
            "LIMITS-Base,LIMITS-StrPol-500",
            "LIMITS-Base,LIMITS-StrPol-450",
        ]

    def execute_query(self, model, scenario, region, variable):
        """
        Args:
            model: (list of) model(s)
            scenario: (list of) scenario(s), allowing wildcards
            region: (list of) region(s), allowing wildcards
            variable: (list of) variable(s)

        Returns: IamDataframe containing the results of the query
        """
        scenario = scenario.split(",")
        params = []
        # params[0] = model list
        # params[1] = scenario list
        # params[2] = region list
        # params[3] = variable list
        for P in [model, scenario, region, variable]:
            if not isinstance(P, list):
                params.append([P])
            else:
                params.append(P)

        # check if scenarios is "all" or sample keyword
        if params[1][0].lower() == self.wildcard:
            params[1] = self.get_scenarios(model=model)
        elif "sample" in params[1][0].lower():
            params[1] = self.get_sample_scenarios()
        # check if region is "all" or sample keyword
        if params[2][0].lower() == self.wildcard:
            params[2] = self.get_regions(model=model)
        elif "sample" in params[2][0].lower():
            params[2] = self.get_sample_regions()

        query = (
            "MODEL in @params[0] & SCENARIO in @params[1] "
            "& REGION in @params[2] & VARIABLE in @params[3]"
        ).lower()
        df = self.limits_dataframe.data.query(query)

        if df.empty:
            return None

        df = pyam.IamDataFrame(data=df)
        return df
