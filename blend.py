import pandas as pd
import numpy as np

from sklearn.base import ClassifierMixin, RegressorMixin, TransformerMixin, BaseEstimator
from sklearn.linear_model.base import LinearModel
from sklearn.metrics import get_scorer

from scipy.optimize import minimize

from robusta.preprocessing import RankTransformer


__all__ = [
    'BlendRegressor',
    'BlendClassifier',
    'RankBlendRegressor',
    'RankBlendClassifier',
]




class BaseBlend(LinearModel):
    '''Base Blending Estimator

    Parameters
    ----------
    avg_type : string or callable (default='mean')
        Select weighted average function:

            - 'mean': Arithmetic mean
            - 'hmean': Harmonic mean
            - 'gmean': Geometric mean

    scoring : string or None (default=None)
        Objective for optimization. If None, all weights are equal.
        Otherwise, calculate the optimal weights for blending.

    opt_func : function (default=None)
        Optimization function. First argument should take objective to minimize.

    opt_kws : dict, optional
        Parameters for <opt_func> function


    Attributes
    ----------
    coef_ : Series, shape (n_features, )
        Estimated weights of blending model.

    n_iters_ : int
        Number of evaluations

    scores_ : list of float
        Evaluation results

    '''
    def __init__(self, avg_type='mean', scoring=None, opt_func=None, **opt_kws):
        self.avg_type = avg_type
        self.scoring = scoring
        self.opt_func = opt_func
        self.opt_kws = opt_kws


    def fit(self, X, y, weights=None):

        if self._estimator_type is 'classifier':
            self.classes_ = np.unique(y)

        self.avg = check_avg_type(self.avg_type)
        self.n_features_ = X.shape[1]
        self.set_weights(weights)

        if self.scoring:

            self.scorer = get_scorer(self.scoring)
            objective = lambda w: -self.set_weights(w).score(Xt, y)

            if self.opt_func is None:
                self.opt_func = minimize
                self.opt_kws = dict(x0=self.get_weights(), method='SLSQP',
                    options={'maxiter': 1000}, bounds=[(0., 1.)] * self.n_features_,
                    constraints=[{'type': 'eq', 'fun': lambda w: np.sum(w)-1}]),

            result = self.opt_func(objective, **self.opt_kws)

            self.set_weights(result['x'])
            self.result_ = result

        return self


    def set_weights(self, weights):
        if weights is None:
            self.coef_ = np.ones(self.n_features_) / self.n_features_
        else:
            self.coef_ = np.array(weights) / np.sum(weights)
        return self


    def get_weights(self):
        return self.coef_


    def score(self, X, y):
        return self.scorer(self, X, y)


    @property
    def _is_fitted(self):
        return (hasattr(self, 'result_') or not self.scoring)


    @property
    def intercept_(self):
        return .0


    def _blend(self, X):
        return self.avg(X, self.coef_).values



class BlendRegressor(BaseBlend, RegressorMixin):

    def predict(self, X):
        return self._blend(X)




class BlendClassifier(BaseBlend, ClassifierMixin):

    def predict_proba(self, X):
        y = self._blend(X)
        return np.stack([1-y, y], axis=-1)

    def predict(self, X):
        y = self.predict_proba(X)
        return np.rint(y[:, 1]).astype(int)



def RankBlendRegressor(**params):
    return make_pipeline(RankTransformer(), BlendRegressor(**params))



def RankBlendClassifier(**params):
    return make_pipeline(RankTransformer(), BlendClassifier(**params))



AVG_TYPES = {
    'mean': lambda X, w: X.dot(w),
    'hmean': lambda X, w: 1/(1/X).dot(w),
    'gmean': lambda X, w: np.exp(np.log(X).dot(w)),
}


def check_avg_type(avg_type):

    avg_types = list(AVG_TYPES.keys())

    if avg_type in avg_types:
        return AVG_TYPES[avg_type]

    else:
        raise ValueError("Invalid value '{}' for <avg_type>. Allowed values: "
                         "".format(avg_types))
