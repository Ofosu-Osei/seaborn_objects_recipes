from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from seaborn._stats.base import Stat
import statsmodels.api as sm

@dataclass
class Lowess(Stat):
    frac: float = 0.2
    gridsize: int = 100
    num_bootstrap: int = 200
    confidence_level: float = 0.95

    def _fit_predict(self, data):
        x = data["x"]
        xx = np.linspace(x.min(), x.max(), self.gridsize)
        result = sm.nonparametric.lowess(endog=data["y"], exog=x, frac=self.frac, xvals=xx)
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
            result = sm.nonparametric.lowess(endog=sample["y"], exog=sample["x"], xvals=xx, frac=self.frac)
            # Ensure the result is two-dimensional
            if result.ndim == 1:
                result = np.column_stack((xx, result))  # Reformat to two-dimensional if needed
            bootstrap_estimates[i, :] = result[:, 1]

        return xx, bootstrap_estimates

    def __call__(self, data):
        data = data.dropna(subset=["x", "y"])
        smoothed = self._fit_predict(data)
        xx, bootstrap_estimates = self._bootstrap_resampling(data)
        
        lower_bound = np.percentile(bootstrap_estimates, (1 - self.confidence_level) / 2 * 100, axis=0)
        upper_bound = np.percentile(bootstrap_estimates, (1 + self.confidence_level) / 2 * 100, axis=0)
        
        return pd.DataFrame({
            'x': xx,
            'y': smoothed['y'],
            'ci_lower': lower_bound,
            'ci_upper': upper_bound
        })
