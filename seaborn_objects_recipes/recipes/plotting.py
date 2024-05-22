from __future__ import annotations
from matplotlib import style
from dataclasses import dataclass
import statsmodels.formula.api as smf
import seaborn.objects as so  

@dataclass
class RegressionWithCI(so.PolyFit):
    """
Returns a seaborn.objects scatter plot with Dots and a linear
regression with confidence intervals.

:param alpha: Confidence inteval alpha.
:param include_dots: Should data points be included in plot?
"""
    def __init__(self, order=1, gridsize=100, alpha=0.05, include_dots=True):
        super().__init__(order=order, gridsize=gridsize)
        self.alpha = alpha
        self.include_dots = include_dots

    def fit_and_predict(self, data, yvar, xvar):
        if len(data) < 3:
            raise ValueError("Insufficient data points to fit the model.")
        # Filter out missing data and reset index to avoid issues with row indices
        data = data.dropna(subset=[yvar, xvar]).reset_index(drop=True)
        
        # Fit the OLS model
        model = smf.ols(f"{yvar} ~ {xvar}", data=data).fit()

        # Get predicted values
        model_predict = model.get_prediction(data[xvar])
        data["predicted_" + yvar] = model_predict.summary_frame()["mean"]
        data[["ci_low", "ci_high"]] = model_predict.conf_int(alpha=self.alpha)
            
        return data

    def plot(self, data, xvar, yvar):
        # Fit model and extend data with predictions and confidence intervals
        data = self.fit_and_predict(data, yvar, xvar)
        
        # Initialize plot
        plot = so.Plot(data, x=xvar)
        
        # Optionally add original data points
        if self.include_dots:
            plot = plot.add(so.Dots(), y=yvar)
        
        # Add regression line and confidence interval band
        plot = (
            plot.add(so.Lines(), y="predicted_" + yvar)
            .add(so.Band(), ymin="ci_low", ymax="ci_high")
            .theme({**style.library["seaborn-v0_8-whitegrid"]})
        )
        
        return plot