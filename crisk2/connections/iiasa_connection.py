import pyam.iiasa
import os


class IIASAConnection:
    wildcard = "all"

    # note: for shorter loading times and ease of use, only ngfs_phase_3 database is considered here
    def __init__(self, database="ngfs_phase_3"):
        """
        Args:
            database: string of name of database/project to connect with
        """
        self.con = pyam.iiasa.Connection(database)

    def get_connections(self):
        """
        Returns: possible databases to connect with
        """
        return self.con.valid_connections

    def get_models(self):
        """
        Returns: list of all models available for the connected database
        """
        return self.con.models().to_list()

    def get_scenarios(self):
        """
        Returns: list of all climate scenarios available for the connected database
        """
        file_name = os.path.join(
            os.path.dirname(__file__), "mapping/gcam_scenarios.txt"
        )
        return open(file_name, "r", encoding="utf-8").read().split(",")

    def get_regions(self):
        """
        Returns: list of all regions available for the connected database
        """
        file_name = os.path.join(os.path.dirname(__file__), "mapping/gcam_regions.txt")
        return open(file_name, "r", encoding="utf-8").read().split(",")

    def get_variables(self):
        """
        Returns: list of all variables available for the connected database
        """
        file_name = os.path.join(
            os.path.dirname(__file__), "mapping/gcam_variables.txt"
        )
        return open(file_name, "r", encoding="utf-8").read().split(",")

    def execute_query(self, model, scenario, region, variable):
        """
        Args:
            model: (list of) model(s)
            scenario: (list of) scenario(s), allowing wildcards
            region: (list of) region(s), allowing wildcards
            variable: (list of) variable(s)

        Returns: IamDataframe containing the results of the query
        """
        if not isinstance(region, list):
            region = [region]

        if scenario.lower() == self.wildcard:
            scenario = "*"
        if region[0].lower() == self.wildcard:
            region = "*"

        params = []
        for P in [model, scenario, region, variable]:
            if not isinstance(P, list):
                params.append([P])
            else:
                params.append(P)

        df = self.con.query(
            model=model, scenario=scenario, variable=variable, region=region
        )
        return df
