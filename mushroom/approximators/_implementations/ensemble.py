import numpy as np
from sklearn.exceptions import NotFittedError


class Ensemble(object):
    """
    This class is used to create an ensemble of regressors.

    """
    def __init__(self, model, n_models, prediction='mean', **params):
        """
        Constructor.

        Args:
            approximator (object): the model class to approximate the
                Q-function.
            n_models (int): number of regressors in the ensemble;
            prediction (str, 'mean'): the type of prediction to make. It can
                be a 'mean' of the ensembles, or a 'sum'.
            **params (dict): parameters dictionary to create each regressor.

        """
        self._prediction = prediction
        self._model = list()

        for _ in range(n_models):
            self._model.append(model(**params))

    def fit(self, *z, **fit_params):
        """
        Fit the ``idx``-th model of the ensemble if ``idx`` is provided, a
        random model otherwise.

        Args:
            *z (list): a list containing the inputs to use to predict with each
                regressor of the ensemble;
            **fit_params (dict): other params.

        """
        idx = fit_params.pop('idx', None)
        if idx is None:
            self[np.random.choice(len(self))].fit(*z, **fit_params)
        else:
            self[idx].fit(*z, **fit_params)

    def predict(self, *z, **predict_params):
        """
        Predict.

        Args:
            *z (list): a list containing the inputs to use to predict with each
                regressor of the ensemble;
            **predict_params (dict): other params.

        Returns:
            The predictions of the model.

        """
        idx = predict_params.pop('idx', None)
        if idx is None:
            predictions = list()
            for i in range(len(self._model)):
                try:
                    predictions.append(self[i].predict(*z, **predict_params))
                except NotFittedError:
                    pass

            if len(predictions) == 0:
                raise NotFittedError

            if self._prediction == 'mean':
                results = np.mean(predictions, axis=0)
            elif self._prediction == 'sum':
                results = np.sum(predictions, axis=0)
            else:
                raise ValueError
            if predict_params.get('compute_variance', False):
                results = [results] + np.var(predictions, ddof=1, axis=0)
        else:
            try:
                results = self[idx].predict(*z, **predict_params)
            except NotFittedError:
                raise NotFittedError

        return results

    def reset(self):
        """
        Reset the model parameters.

        """
        try:
            for m in self.model:
                m.reset()
        except AttributeError:
            raise NotImplementedError('Attempt to reset weights of a'
                                      ' non-parametric regressor.')

    @property
    def model(self):
        """
        Returns:
            The list of the models in the ensemble.

        """
        return self._model

    def __len__(self):
        return len(self._model)

    def __getitem__(self, idx):
        return self._model[idx]
