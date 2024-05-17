import os
import pytest
import seaborn_objects_recipes as sor
import matplotlib.pyplot as plt
import seaborn.objects as so
import seaborn as sns
import pandas as pd
import numpy as np


@pytest.fixture
def sample_data():
    # Parameters for simulation
    game = "ExampleGame"
    agents = ["Agent1", "Agent2", "Agent3"]
    num_iterations = 200
    num_agents = len(agents)

    # Create a simulated DataFrame
    np.random.seed(0)  # For reproducible results
    data = {
        "Game": [game] * num_iterations * num_agents,
        "Episodic Return": np.random.rand(num_iterations * num_agents) * 100,
        "Iteration": list(range(num_iterations)) * num_agents,
        "Agent": np.repeat(agents, num_iterations),
    }

    return pd.DataFrame(data)


@pytest.fixture
def cleanup_files():
    # This will run after each test function to which it is applied.
    yield
    # Cleanup code to delete files after test runs
    if os.path.exists("line_label.png"):
        os.remove("line_label.png")
    if os.path.exists("lowess.png"):
        os.remove("lowess.png")


# Use the sample_data fixture to provide data to the test function
# and the cleanup_files fixture to clean up after the test
def test_line_label(sample_data, cleanup_files):
    # theme = "darkgrid"
    game = "ExampleGame"
    fd_data = sample_data.query(f'`Game` == "{game}"')

    (
        fd_data.pipe(
            so.Plot, y="Episodic Return", x="Iteration", color="Agent", text="Agent"
        )
        .layout(size=(16, 8))
        # .theme(theme)
        .facet("Game")
        .limit(x=(0, 200))
        .scale(
            x=so.Continuous().tick(at=list(range(0, 201, 25))),
            y=so.Continuous().tick(upto=5).label(like="{x:,.0f}"),
        )
        .add(
            so.Lines(),
            so.Agg(),
            sor.Rolling(window_type="gaussian", window_kwargs={"std": 2}),
            legend=False,
        )
        # This will be much easier when compound marks are implemented.
        # Will be able to do so.Line() + LineLabel().
        .add(
            sor.LineLabel(offset=5),
            so.Agg(),
            sor.Rolling(window_type="gaussian", window_kwargs={"std": 2}),
            legend=False,
        )
        .add(so.Band(), so.Est(errorbar="se"), legend=False)
        .save("line_label.png")
        #.show()
    )
    # Assert that the file was created
    assert os.path.exists(
        "line_label.png"
    ), "The plot file line_label.png was not created."


def test_lowess(cleanup_files):
    # Generate data for testing
    np.random.seed(0)
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x) + np.random.normal(size=100) * 0.2
    data = pd.DataFrame({"x": x, "y": y})

    # Initialize LOWESS instance
    lowess = sor.Lowess(frac=0.4)
    # Call the LOWESS method on prepared data
    results = lowess(data)

    fig, ax = plt.subplots(figsize=(9, 5))

    # Scatter plot of the raw data
    sns.scatterplot(x="x", y="y", data=data, ax=ax, color="blue", alpha=0.5)

    # LOWESS smoothed line
    ax.plot(results["x"], results["y"], color="darkblue")

    # Confidence interval shading
    ax.fill_between(
        results["x"], results["ci_lower"], results["ci_upper"], color="blue", alpha=0.3
    )

    # Customizing plot
    ax.set_xlabel("x-axis")
    ax.set_ylabel("y-axis")
    ax.set_title("LOWESS Smoothing with Confidence Intervals for Generated Data")

    # Add gridlines
    ax.grid(True, which="both", color="gray", linewidth=0.5, linestyle="--")
    plt.savefig("lowess.png")
    # plt.show()

    # Assert that the file was created
    assert os.path.exists("lowess.png"), "The plot file lowess.png was not created."


def test_lowess_(cleanup_files):
    # Load Penguins dataset
    data = sns.load_dataset("penguins")

    # Prepare data for 'x' and 'y'
    data = data.rename(columns={"bill_length_mm": "x", "body_mass_g": "y"})

    # Filter data for instance:
    data = data[data["species"] == "Adelie"]

    # Initialize LOWESS instance
    lowess = sor.Lowess(frac=0.4)

    # Call the LOWESS method on prepared data
    results = lowess(data)

    fig, ax = plt.subplots(figsize=(9, 5))

    # Scatter plot of the raw data
    sns.scatterplot(x="x", y="y", data=data, ax=ax, color="blue", alpha=0.5)

    # LOWESS smoothed line
    ax.plot(results["x"], 
            results["y"], 
            color="darkblue"
    )

    # Confidence interval shading
    ax.fill_between(
        results["x"], 
        results["ci_lower"], 
        results["ci_upper"], 
        color="blue", 
        alpha=0.3
    )
    # Customizing plot
    ax.set_xlabel("Bill Length (mm)")
    ax.set_ylabel("Body Mass (g)")
    ax.set_title("LOWESS Smoothing with Confidence Intervals for Adelie Penguins")
    # Add gridlines
    ax.grid(True, which="both", color="gray", linewidth=0.5, linestyle="--")
    #plt.show()
    plt.savefig("lowess_.png")

    # Assert that the file was created
    assert os.path.exists("lowess_.png"), "The plot file lowess.png was not created."

def test_regression_w_ci(cleanup_files):
    # Load Penguins dataset
    penguins = sns.load_dataset("penguins")

    # Create an instance of the class
    regression_plot = sor.RegressionWithCI(alpha=0.05, include_dots=True)

    plot = regression_plot.plot(
        penguins[penguins.species == "Adelie"], xvar="bill_length_mm", yvar="body_mass_g"
    )

    plot.label(x = "Bill Length (mm)", y = "Body Mass (g)")
    plot.save("regression_w_ci.png")
    #plot.show()

    # Assert that the file was created
    assert os.path.exists("regression_w_ci.png"), "The plot file lowess.png was not created."