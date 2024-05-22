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
    if os.path.exists("lowess_b.png"):
        os.remove("lowess_b.png")
    if os.path.exists("lowess_gen.png"):
        os.remove("lowess_gen.png")
    if os.path.exists("lowess_nb.png"):
        os.remove("lowess_nb.png")
    if os.path.exists("reg_with_ci.png"):
        os.remove("reg_with_ci.png")


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


def test_lowess_with_ci_gen(cleanup_files):
    # Generate data for testing
    np.random.seed(0)
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x) + np.random.normal(size=100) * 0.2
    data = pd.DataFrame({"x": x, "y": y})

    # Initialize LOWESS instance with bootstrapping
    lowess = sor.Lowess(frac=0.2, gridsize=100, num_bootstrap=200, alpha=0.95)
    # Call the LOWESS method on prepared data
    results = lowess(data, xvar="x", yvar="y")

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
    plt.savefig("lowess_gen.png")
    # plt.show()

    # Assert that the file was created
    assert os.path.exists("lowess_gen.png"), "The plot file lowess.png was not created."


def test_lowess_with_ci(cleanup_files):
    # Load the penguins dataset
    penguins = sns.load_dataset("penguins")

    # Prepare data
    data = penguins[penguins['species'] == 'Adelie']

    # Initialize LOWESS instance with bootstrapping
    lowess_with_bootstrap = sor.Lowess(frac=0.9, gridsize=100, num_bootstrap=200, alpha=0.95)

    # Call the LOWESS method on prepared data
    results_with_bootstrap = lowess_with_bootstrap(data, xvar ='bill_length_mm', yvar='body_mass_g')

    # Plotting
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(x='bill_length_mm', y='body_mass_g', data=data, ax=ax, color='blue', alpha=0.5)
    ax.plot(results_with_bootstrap['bill_length_mm'], results_with_bootstrap['body_mass_g'], color='darkblue')
    ax.fill_between(results_with_bootstrap['bill_length_mm'], 
                    results_with_bootstrap['ci_lower'], 
                    results_with_bootstrap['ci_upper'], 
                    color='blue', 
                    alpha=0.3
    )
    ax.set_xlabel('Bill Length (mm)')
    ax.set_ylabel('Body Mass (g)')
    ax.set_title('LOWESS Smoothing with Confidence Intervals for Adelie Penguins')
    ax.grid(True, which='both', color='gray', linewidth=0.5, linestyle='--')
    #plt.show()
    plt.savefig("lowess_b.png")

    # Assert that the file was created
    assert os.path.exists("lowess_b.png"), "The plot file lowess.png was not created."



def test_lowess_with_no_ci(cleanup_files):
    # Load the penguins dataset
    penguins = sns.load_dataset("penguins")

    # Prepare data
    data = penguins[penguins['species'] == 'Adelie']

    # Initialize LOWESS instance (no bootstrapping)
    lowess_no_bootstrap = sor.Lowess(frac=0.5, gridsize=100)

    # Call the LOWESS method on prepared data
    results_no_bootstrap = lowess_no_bootstrap(data, xvar ='bill_length_mm', yvar='body_mass_g')

    # Plotting
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(x='bill_length_mm', y='body_mass_g', data=data, ax=ax, color='blue', alpha=0.5)
    ax.plot(results_no_bootstrap['bill_length_mm'], results_no_bootstrap['body_mass_g'], color='darkblue')
    ax.set_xlabel('Bill Length (mm)')
    ax.set_ylabel('Body Mass (g)')
    ax.set_title('LOWESS Smoothing for Adelie Penguins (No Bootstrapping)')
    ax.grid(True, which='both', color='gray', linewidth=0.5, linestyle='--')
    #plt.show()
    plt.savefig("lowess_nb.png")

    # Assert that the file was created
    assert os.path.exists("lowess_nb.png"), "The plot file lowess.png was not created."


def test_regression_with_ci(cleanup_files):
    # Load the penguins dataset
    penguins = sns.load_dataset("penguins")

    # Create an instance of the class
    regression_plot = sor.PolyFitCI(order=2, gridsize=100, alpha=0.05)

    plot = regression_plot.plot(
        penguins[penguins.species == "Adelie"], xvar="bill_length_mm", yvar="body_mass_g"
    )

    plot = (
        plot
        .add(so.Dots(), y="body_mass_g")
        .label(x="Bill Length (mm)", y="Body Mass (g)")
    )
    
    plot.save("reg_with_ci.png")
    #plt.show()

    # Assert that the file was created
    assert os.path.exists("reg_with_ci.png"), "The plot file lowess.png was not created."