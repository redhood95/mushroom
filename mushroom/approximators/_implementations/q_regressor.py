import numpy as np


class QRegressor:
    """
    This class is used to create a regressor that approximates the Q-function
    using a multi-dimensional output where each output corresponds to the
    Q-value of each action. This is used, for instance, by the ``ConvNet`` used
    in examples/atari_dqn.

    """
    def __init__(self, approximator, **params):
        """
        Constructor.

        Args:
            approximator (object): the model class to approximate the
                Q-function;
            params (dict): parameters dictionary to the regressor.

        """
        self._input_preprocessor = params.pop('input_preprocessor', list())
        self._output_preprocessor = params.pop('output_preprocessor', list())
        self.model = approximator(**params)

    def fit(self, state, action, q, **fit_params):
        """
        Fit the model.

        Args:
            state (np.ndarray): states;
            action (np.ndarray): actions;
            q (np.ndarray): target q-values;
            **fit_params (dict): other parameters used by the fit method of the
                regressor.

        """
        state, q = self._preprocess(state, q)
        self.model.fit(state, action, q, **fit_params)

    def predict(self, *z, **predict_params):
        """
        Predict.

        Args:
            *z (list): a list containing states or states and actions depending
                on whether the call requires to predict all q-values or only
                one q-value corresponding to the provided action;
            **predict_params (dict): other parameters used by the predict method
                of each regressor.

        Returns:
            The predictions of the model.

        """
        assert len(z) == 1 or len(z) == 2

        state = self._preprocess(z[0])
        q = self.model.predict(state, **predict_params)

        if len(z) == 2:
            action = z[1].ravel()
            if q.ndim == 1:
                return q[action]
            else:
                return q[np.arange(q.shape[0]), action]
        else:
            return q

    def reset(self):
        """
        Reset the model parameters.

        """
        try:
            self.model.reset()
        except AttributeError:
            raise NotImplementedError('Attempt to reset weights of a'
                                      ' non-parametric regressor.')

    @property
    def weights_size(self):
        return self.model.weights_size

    def get_weights(self):
        return self.model.get_weights()

    def set_weights(self, w):
        self.model.set_weights(w)

    def diff(self, state, action=None):
        return self.model.diff(state, action)

    def _preprocess(self, state, q=None):
        for p in self._input_preprocessor:
            state = p(state)

        if q is not None:
            for p in self._output_preprocessor:
                q = p(q)

            return state, q
        return state

    def __len__(self):
        return len(self.model)
