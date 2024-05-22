from __future__ import annotations
from matplotlib import style
from dataclasses import dataclass
import statsmodels.formula.api as smf
import seaborn.objects as so
import pandas as pd
import numpy as np  

@dataclass
class PolyFitCI(so.PolyFit):
    """
    Fit a polynomial of the given order and include confidence intervals.
    Returns a seaborn.objects scatter plot with Dots and a polynomial
    regression with confidence intervals.

    :param alpha: Confidence interval alpha.
    """
    alpha: float = 0.05

    def __init__(self, order=1, gridsize=100, alpha=0.05):
        super().__init__(order=order, gridsize=gridsize)
        self.alpha = alpha
       

    def fit_and_predict(self, data, yvar, xvar):
        if len(data) < 3:
            raise ValueError("Insufficient data points to fit the model.")
        # Filter out missing data and reset index to avoid issues with row indices
        data = data.dropna(subset=[yvar, xvar]).reset_index(drop=True)
        
        # Construct polynomial formula for the specified order
        formula = f"{yvar} ~ " + " + ".join([f"np.power({xvar}, {i})" for i in range(1, self.order + 1)])
        
        # Fit the OLS model
        model = smf.ols(formula, data=data).fit()

        # Generate grid for predictions
        x_grid = np.linspace(data[xvar].min(), data[xvar].max(), self.gridsize)
        pred_data = pd.DataFrame({xvar: x_grid})

        # Get predicted values
        model_predict = model.get_prediction(pred_data)
        pred_data[yvar] = model_predict.summary_frame()["mean"]
        pred_data[["ci_low", "ci_high"]] = model_predict.conf_int(alpha=self.alpha)
           
        return pred_data

    def plot(self, data, xvar, yvar):
        # Fit model and extend data with predictions and confidence intervals
        data = self.fit_and_predict(data, yvar, xvar)
        
        # Initialize plot
        plot = so.Plot(data, x=xvar)
        
        # Add regression line and confidence interval band
        plot = (
            plot.add(so.Lines(), y=yvar)
            .add(so.Band(), ymin="ci_low", ymax="ci_high")
            .theme({**style.library["seaborn-v0_8-whitegrid"]})
        )
        
        
        return plot
    