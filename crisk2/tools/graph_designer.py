from matplotlib import pyplot as plt


def graph_market_shocks(ms, ms_shocks, scenarios, axis1, axis2):
    """
    Creates a graph with two different axis for market share and relative market share changes -> market shocks
    Directly manipulates passed axis -> no return value
    Args:
        ms: market share dataframe
        ms_shocks: market share shocks dataframe
        scenarios: two scenarios
        axis1: axis on which to plot market shares
        axis2: axis on which to plot market share shocks
    """
    years = list(range(2005, 2051, 5))
    years.extend(list(range(2060, 2101, 10)))
    base_ms = ms.data.query("scenario == @scenarios[0]")["value"].reset_index(drop=True)
    ref_ms = ms.data.query("scenario == @scenarios[1]")["value"].reset_index(drop=True)
    shocks = ms_shocks["value"].reset_index(drop=True)

    axis1.plot(years, base_ms, color="blue", linestyle="-", label=scenarios[0])
    axis1.plot(years, ref_ms, color="blue", linestyle="--", label=scenarios[1])
    axis1.set_ylabel("Market Share %")
    axis1.set_xlabel("Year")
    axis1.set_ylim([0, None])
    axis1.set_xlim([2005, 2100])
    axis1.spines["left"].set_color("blue")
    axis1.tick_params(axis="y", colors="blue")
    axis1.yaxis.label.set_color("blue")

    axis2.plot(years, shocks, color="red", linestyle="--", label="Base to Reference")
    axis2.set_ylabel("Market Share Shock %")
    axis2.set_ylim([min(shocks), max(shocks)])
    axis2.set_xlim([2005, 2100])
    axis2.spines["right"].set_color("red")
    axis2.tick_params(axis="y", colors="red")
    axis2.yaxis.label.set_color("red")

    plt.title("Market share and respective shocks")
    lines, labels = axis1.get_legend_handles_labels()
    lines2, labels2 = axis2.get_legend_handles_labels()
    axis2.legend(lines + lines2, labels + labels2)


def graph_market_shares(data, axis, variable):
    """
    Directly manipulates passed axis -> no return value
    Args:
        data: dataframe of market shares for one variable
        axis: axis on which the plot is drawn
        variable: relevant variable
    """
    data.plot(ax=axis)
    region = data["region"].unique()
    plt.ylabel("Market share (%)")
    plt.xlabel("Year")
    plt.title("Market share of " + variable + " in " + region[0])


def simple_graph(data, axis, title, linestyle):
    """
    Directly manipulates passed axis -> no return value
    Args:
        data: data to plot, data for one variable, one region, etc
        axis: axis on which the plot is drawn
        title: title of the plot
        linestyle: linestyle of the plot
    """
    data.plot(
        ax=axis,
        legend=True,
        title=title,
        linestyle=linestyle,
    )
