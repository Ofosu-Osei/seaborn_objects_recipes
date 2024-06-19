from __future__ import annotations
from matplotlib import style
from dataclasses import dataclass
import statsmodels.formula.api as smf
from seaborn._stats.base import Stat
import seaborn.objects as so
import pandas as pd
import numpy as np  
from typing import Optional

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


@dataclass
class PolyFit(Stat):
    """
    Fit a polynomial of the given order and resample data onto predicted curve
    including confidence intervals.
    """
    alpha: float = 0.05
    order: int = 2
    gridsize: int = 100

    def __post_init__(self):
        # Type checking for the arguments
        if not isinstance(self.order, int) or self.order <= 0:
            raise ValueError("order must be a positive integer.")
        if not isinstance(self.gridsize, int) or self.gridsize <= 0:
            raise ValueError("gridsize must be a positive integer.")
        if not isinstance(self.alpha, float) or not (0 < self.alpha < 1):
            raise ValueError("alpha must be a float between 0 and 1.")
        
    def _fit_predict(self, data):
        data = data.dropna(subset=["x", "y"])
        x = data["x"].values
        y = data["y"].values
        if x.size <= self.order:
            xx = yy = []
        else:
            p = np.polyfit(x, y, self.order)
            xx = np.linspace(x.min(), x.max(), self.gridsize)
            yy = np.polyval(p, xx)
            
            # Calculate confidence intervals
            # Design matrix
            X_design = np.vander(xx, self.order + 1)
            
            # Calculate standard errors
            y_hat = np.polyval(p, x)
            residuals = y - y_hat
            dof = max(0, len(x) - (self.order + 1))
            residual_std_error = np.sqrt(np.sum(residuals**2) / dof)
            
            # Covariance matrix of coefficients
            C_matrix = np.linalg.inv(X_design.T @ X_design) * residual_std_error**2
            
            # Calculate the standard error for the predicted values
            y_err = np.sqrt(np.sum((X_design @ C_matrix) * X_design, axis=1))
            
            # Calculate the confidence intervals
            ci = y_err * 1.96  # For approximately 95% CI
            ci_lower = yy - ci
            ci_upper = yy + ci
        
        results = pd.DataFrame(dict(x=xx, y=yy, ci_lower=ci_lower, ci_upper=ci_upper))

        return results
    
    def __call__(self, data, xvar, yvar):
        # Rename columns to match expected input for _fit_predict
        data_renamed = data.rename(columns={xvar: "x", yvar: "y"})
        results = self._fit_predict(data_renamed)
        return results.rename(columns={"x": xvar, "y": yvar, "ci_lower": "ci_lower", "ci_upper": "ci_upper"})

