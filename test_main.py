import os
import pytest
import seaborn_objects_recipes as sor
import seaborn.objects as so
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
        # .show()
    )
    # Assert that the file was created
    assert os.path.exists(
        "line_label.png"
    ), "The plot file line_label.png was not created."


def test_lowess(cleanup_files):
    np.random.seed(0)
    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x) + np.random.normal(size=100) * 0.2
    data = pd.DataFrame({"x": x, "y": y})

    (
        so.Plot(
            data,
            x="x",
            y="y",
        )
        .add(so.Dot())
        .add(so.Lines(), sor.Lowess())
        .label(x="x-axis", y="y-axis", title="Lowess Plot Example")
        .save("lowess.png")
        # .show()
    )
    # Assert that the file was created
    assert os.path.exists("lowess.png"), "The plot file lowess.png was not created."
