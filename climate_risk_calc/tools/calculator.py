from math import ceil
import pandas as pd
import pyam

from climate_risk_calc.connections.limits_connection import LimitsConnection


def get_base_sector(variable):
    """
    Args:
        variable: String of sector variable like "Secondary Energy|Electricity|Coal"
    Returns: Base sector of variable, i.e. removing the last subpart: "Secondary Energy|Electricity"
    """
    base = str.rsplit(variable, "|", 1)
    return base[0]


def get_market_share_shocks(dataframe, as_percent=True, show_till_2050=False):
    """
    Args:
        dataframe: dataframe with necessary data, i.e. data for 2 scenarios, 1 sector, x regions
        as_percent: indicator whether shocks should be returned as percentages
        show_till_2050: indicator whether data after 2050 should be omitted
    Returns: IamDataframe with market share shock data
    """
    scenarios = dataframe.data["scenario"].unique().tolist()
    scenarios = sorted(scenarios, key=len)
    if len(scenarios) != 2:
        raise ValueError("Scenarios not valid")
    base_scenario_df = get_market_shares(dataframe.filter(scenario=scenarios[0]))
    compared_scenario_df = get_market_shares(dataframe.filter(scenario=scenarios[1]))
    shocks = pd.DataFrame()
    shocks["shock"] = (
        compared_scenario_df["value"] - base_scenario_df["value"]
    ) / base_scenario_df["value"]
    if as_percent:
        shocks["shock"] = shocks["shock"] * 100
    shock_iamdf = compared_scenario_df.data
    shock_iamdf["value"] = shocks["shock"]
    shock_iamdf["variable"] = "shock"
    if show_till_2050:
        shock_iamdf.query("year <=2050", inplace=True)
    return pyam.IamDataFrame(shock_iamdf)


def get_market_shares(dataframe, as_percent=True):
    """
    Args:
        dataframe: dataframe with necessary data, i.e. data for 2 scenarios, 1 sector, x regions
        as_percent: indicator whether shocks should be returned as percentages
    Returns: IamDataframe with market share data
    """
    variables = dataframe.data["variable"].unique().tolist()
    variables = sorted(variables, key=len)
    market_shares = dataframe.divide(
        a=variables[1], b=variables[0], name="Market Share", ignore_units=True
    )
    if as_percent:
        market_shares = market_shares.multiply(
            a="Market Share", b=100, name="Market Share", ignore_units=True
        )
    return market_shares


def get_single_shock(dataframe_source, region, sector, year):
    """
    Args:
        dataframe_source: dataframe with necessary data
        region: region for which to calculate shock
        sector: sector for which to calculate shock
        year: year for which to calculate shock
    Returns: single shock as float
    """
    base_sector = get_base_sector(sector)
    sectors = [sector, base_sector]
    df = pyam.IamDataFrame(
        dataframe_source.data.query("variable in @sectors & region == @region")
    )
    shocks = get_market_share_shocks(df, as_percent=False).data
    shocks.loc[shocks["value"] >= 1, "value"] = 1
    shocks = shocks.query("year == @year")
    return shocks["value"].item()


def get_shocks(model, ref_scenario, year, file_name, recovery_rate=0, elasticity=1):
    """
    Args:
        model: model for which to calculate shocks
        ref_scenario: reference scenario for which to calculate shocks
        year: year of shock occurrence
        file_name: file path of credit portfolio CSV-file
        recovery_rate: assumed recovery rate
        elasticity: assumed elasticity
    Returns: credit portfolio dataframe with added column "shock"
    """
    pd.set_option("display.float_format", "{:.2f}".format)
    loans = pd.read_csv(file_name, encoding="UTF-8")
    lc = LimitsConnection()
    scenarios = "LIMITS-Base," + ref_scenario
    variables = loans["sector"].unique().tolist()
    all_sectors = []
    # reduce repeated querying of large dataset by filtering as much as possible before For-loop
    for var in variables:
        all_sectors.append(var)
        all_sectors.append(get_base_sector(var))
    all_sectors = list(set(all_sectors))
    df = pyam.IamDataFrame(
        lc.execute_query(
            model=model, scenario=scenarios, region="all", variable=all_sectors
        )
    )
    loans["shock"] = 0

    for index in loans.index:
        loans.at[index, "shock"] = (
            loans.at[index, "amount"]
            * (1 - recovery_rate)
            * elasticity
            * get_single_shock(
                dataframe_source=df,
                region=loans.at[index, "region"],
                sector=loans.at[index, "sector"],
                year=year,
            )
        )
    loans = loans
    return loans


def get_top_shocks(
    year,
    file_name,
    recovery_rate=0,
    elasticity=1,
    scenarios=None,
    models=None,
    confidence_level=0.95,
):
    """
    Args:
        year: year of shock occurrence
        file_name: file path of credit portfolio CSV-file
        recovery_rate: assumed recovery rate
        elasticity: assumed elasticity
        scenarios: list of scenarios for which to calculate shocks
        models: list of models for which to calculate shocks
        confidence_level: confidence level for calculating Value at Risk
    Returns: pandas dataframe with shock highlight data
    """
    loans = pd.read_csv(file_name, encoding="UTF-8")
    total = loans["amount"].sum()
    n_entries = loans.shape[0]
    # value_at_risk_index = n_entries - floor(n_entries * confidence_level)
    value_at_risk_index = ceil(n_entries * confidence_level)
    scenarios = [
        "LIMITS-RefPol-450",
        "LIMITS-RefPol-500",
        "LIMITS-StrPol-450",
        "LIMITS-StrPol-500",
    ]
    models = ["GCAM", "WITCH"]
    shock_highlights = []
    for model in models:
        for scenario in scenarios:
            df = get_shocks(
                model,
                ref_scenario=scenario,
                year=year,
                recovery_rate=recovery_rate,
                elasticity=elasticity,
                file_name=file_name,
            )
            df = df.sort_values(["shock"], ascending=[False])
            df = df.reset_index(drop=True)
            shock_highlights.append(
                [
                    model,
                    scenario,
                    df.min(axis=0)["shock"],
                    df.max(axis=0)["shock"],
                    df.query("shock < 0").sum(axis=0)["shock"],
                    df.query("shock > 0").sum(axis=0)["shock"],
                    df.query("shock < 0").sum(axis=0)["shock"] / total,
                    df.at[value_at_risk_index, "shock"],
                ]
            )
    top_shocks = pd.DataFrame(
        data=shock_highlights,
        columns=(
            "model",
            "scenario",
            "min_shock",
            "max_shock",
            "total_neg",
            "total_pos",
            "total_neg_rel",
            "project_VaR",
        ),
    )
    top_shocks = top_shocks.round({"total_neg": 2})
    top_shocks = top_shocks.round({"project_VaR": 2})
    top_shocks = top_shocks.round({"min_shock": 2})
    top_shocks = top_shocks.round({"max_shock": 2})

    top_shocks.sort_values(by="scenario", ascending=True, inplace=True)
    return top_shocks
