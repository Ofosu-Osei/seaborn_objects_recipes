from __future__ import annotations
import numpy as np
import pandas as pd
from pandas import DataFrame
from dataclasses import dataclass
from seaborn._stats.base import Stat
import statsmodels.api as sm
from typing import Optional

@dataclass
class Lowess(Stat):
    """
    Perform locally-weighted regression (LOWESS) to smooth data.
    This statistical method allows fitting a smooth curve to your data
    using a local regression. It can be useful to visualize the trend of the data.

    Parameters
    ----------
    frac : float
        The fraction of data used when estimating each y-value.
    gridsize : int
        The number of points in the grid to which the LOWESS is applied.
        Higher values result in a smoother curve.
    delta : float
        Distance within which to use linear-interpolation instead of weighted regression.
    num_bootstrap : int, optional
        The number of bootstrap samples to use for confidence intervals.
    alpha : float
        Confidence level for the intervals.

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame with the smoothed curve's 'x', 'y', 'ymin', and 'ymax' coordinates.
    """

    frac: float = 0.2
    gridsize: int = 100
    delta: float = 0.0
    num_bootstrap: Optional[int] = None
    alpha: float = 0.95
    

    def __post_init__(self):
        # Type checking for the arguments
        if not isinstance(self.frac, float) or not (0 < self.frac <= 1):
            raise ValueError("frac must be a float between 0 and 1.")
        if not isinstance(self.gridsize, int) or self.gridsize <= 0:
            raise ValueError("gridsize must be a positive integer.")
        if self.num_bootstrap is not None and (
            not isinstance(self.num_bootstrap, int) or self.num_bootstrap <= 0
        ):
            raise ValueError("num_bootstrap must be a positive integer or None.")
        if not isinstance(self.alpha, float) or not (0 < self.alpha < 1):
            raise ValueError("alpha must be a float between 0 and 1.")

    def _fit_predict(self, data):
        x = data["x"]
        xx = np.linspace(x.min(), x.max(), self.gridsize)
        result = sm.nonparametric.lowess(
            endog=data["y"], exog=x, frac=self.frac, delta=self.delta, xvals=xx
        )
        if result.ndim == 1:  # Handle single-dimensional return values
            yy = result
        else:
            yy = result[:, 1]  # Select the predicted y-values
        return pd.DataFrame(dict(x=xx, y=yy))

    def _bootstrap_resampling(self, data):
        xx = np.linspace(data["x"].min(), data["x"].max(), self.gridsize)
        bootstrap_estimates = np.empty((self.num_bootstrap, len(xx)))

        for i in range(self.num_bootstrap):
            sample = data.sample(frac=1, replace=True)
            result = sm.nonparametric.lowess(
                endog=sample["y"],
                exog=sample["x"],
                xvals=xx,
                frac=self.frac,
                delta=self.delta,
            )
            # Ensure the result is two-dimensional
            if result.ndim == 1:
                result = np.column_stack(
                    (xx, result)
                )  # Reformat to two-dimensional if needed
            bootstrap_estimates[i, :] = result[:, 1]

        return xx, bootstrap_estimates

    def __call__(self, data: DataFrame, groupby, orient, scales) -> DataFrame:
        if orient == "x":
            xvar = data.columns[0]
            yvar = data.columns[1]
        else:
            xvar = data.columns[1]
            yvar = data.columns[0]

        renamed_data = data.rename(columns={xvar: "x", yvar: "y"})        
        renamed_data = renamed_data.dropna(subset=["x", "y"])
        smoothed = self._fit_predict(renamed_data)

        if self.num_bootstrap:
            xx, bootstrap_estimates = self._bootstrap_resampling(data)
            lower_bound = np.percentile(
                bootstrap_estimates, (1 - self.alpha) / 2 * 100, axis=0
            )
            upper_bound = np.percentile(
                bootstrap_estimates, (1 + self.alpha) / 2 * 100, axis=0
            )
            smoothed["ymin"] = lower_bound
            smoothed["ymax"] = upper_bound

        return smoothed
