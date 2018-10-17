"""
The :mod:`sklearnext.model_selection.search` includes utilities to search
the parameter and model space.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>
# License: BSD 3 clause

from dask_searchcv.model_selection import GridSearchCV, check_cv
from dask_searchcv.model_selection import _RETURN_TRAIN_SCORE_DEFAULT

from ..utils import check_estimator_type, check_param_grids, _ParametrizedClassifiers, _ParametrizedRegressors

_DOC_TEMPLATE = """{oneliner}

{name} implements a "fit" and a "score" method.
It also implements "predict", "predict_proba", "decision_function",
"transform" and "inverse_transform" if they are implemented in the
estimator used.

{description}

Parameters
----------
estimator : estimator object.
    This is assumed to implement the scikit-learn estimator interface.
    Either estimator needs to provide a ``score`` function,
    or ``scoring`` must be passed.

{parameters}

scoring : string, callable, list/tuple, dict or None, default: None
    A single string or a callable to evaluate the predictions on the test
    set.

    For evaluating multiple metrics, either give a list of (unique) strings
    or a dict with names as keys and callables as values.

    NOTE that when using custom scorers, each scorer should return a single
    value. Metric functions returning a list/array of values can be wrapped
    into multiple scorers that return one value each.

    If None, the estimator's default scorer (if available) is used.

iid : boolean, default=True
    If True, the data is assumed to be identically distributed across
    the folds, and the loss minimized is the total loss per sample,
    and not the mean loss across the folds.

cv : int, cross-validation generator or an iterable, optional
    Determines the cross-validation splitting strategy.
    Possible inputs for cv are:
        - None, to use the default 3-fold cross validation,
        - integer, to specify the number of folds in a ``(Stratified)KFold``,
        - An object to be used as a cross-validation generator.
        - An iterable yielding train, test splits.

    For integer/None inputs, if the estimator is a classifier and ``y`` is
    either binary or multiclass, ``StratifiedKFold`` is used. In all
    other cases, ``KFold`` is used.

refit : boolean, or string, default=True
    Refit an estimator using the best found parameters on the whole
    dataset.

    For multiple metric evaluation, this needs to be a string denoting the
    scorer is used to find the best parameters for refitting the estimator
    at the end.

    The refitted estimator is made available at the ``best_estimator_``
    attribute and permits using ``predict`` directly on this
    ``GridSearchCV`` instance.

    Also for multiple metric evaluation, the attributes ``best_index_``,
    ``best_score_`` and ``best_parameters_`` will only be available if
    ``refit`` is set and all of them will be determined w.r.t this specific
    scorer.

    See ``scoring`` parameter to know more about multiple metric
    evaluation.

error_score : 'raise' (default) or numeric
    Value to assign to the score if an error occurs in estimator fitting.
    If set to 'raise', the error is raised. If a numeric value is given,
    FitFailedWarning is raised. This parameter does not affect the refit
    step, which will always raise the error.

return_train_score : boolean, default=True
    If ``'False'``, the ``cv_results_`` attribute will not include training
    scores.

    Note that for scikit-learn >= 0.19.1, the default of ``True`` is
    deprecated, and a warning will be raised when accessing train score results
    without explicitly asking for train scores.

scheduler : string, callable, Client, or None, default=None
    The dask scheduler to use. Default is to use the global scheduler if set,
    and fallback to the threaded scheduler otherwise. To use a different
    scheduler either specify it by name (either "threading", "multiprocessing",
    or "synchronous"), pass in a ``dask.distributed.Client``, or provide a
    scheduler ``get`` function.

n_jobs : int, default=-1
    Number of jobs to run in parallel. Ignored for the synchronous and
    distributed schedulers. If ``n_jobs == -1`` [default] all cpus are used.
    For ``n_jobs < -1``, ``(n_cpus + 1 + n_jobs)`` are used.

cache_cv : bool, default=True
    Whether to extract each train/test subset at most once in each worker
    process, or every time that subset is needed. Caching the splits can
    speedup computation at the cost of increased memory usage per worker
    process.

    If True, worst case memory usage is ``(n_splits + 1) * (X.nbytes +
    y.nbytes)`` per worker. If False, worst case memory usage is
    ``(n_threads_per_worker + 1) * (X.nbytes + y.nbytes)`` per worker.

Examples
--------
{example}

Attributes
----------
cv_results_ : dict of numpy (masked) ndarrays
    A dict with keys as column headers and values as columns, that can be
    imported into a pandas ``DataFrame``.

    For instance the below given table

    +------------+-----------+------------+-----------------+---+---------+
    |param_kernel|param_gamma|param_degree|split0_test_score|...|rank.....|
    +============+===========+============+=================+===+=========+
    |  'poly'    |     --    |      2     |        0.8      |...|    2    |
    +------------+-----------+------------+-----------------+---+---------+
    |  'poly'    |     --    |      3     |        0.7      |...|    4    |
    +------------+-----------+------------+-----------------+---+---------+
    |  'rbf'     |     0.1   |     --     |        0.8      |...|    3    |
    +------------+-----------+------------+-----------------+---+---------+
    |  'rbf'     |     0.2   |     --     |        0.9      |...|    1    |
    +------------+-----------+------------+-----------------+---+---------+

    will be represented by a ``cv_results_`` dict of::

        {{
        'param_kernel': masked_array(data = ['poly', 'poly', 'rbf', 'rbf'],
                                        mask = [False False False False]...)
        'param_gamma': masked_array(data = [-- -- 0.1 0.2],
                                    mask = [ True  True False False]...),
        'param_degree': masked_array(data = [2.0 3.0 -- --],
                                        mask = [False False  True  True]...),
        'split0_test_score'  : [0.8, 0.7, 0.8, 0.9],
        'split1_test_score'  : [0.82, 0.5, 0.7, 0.78],
        'mean_test_score'    : [0.81, 0.60, 0.75, 0.82],
        'std_test_score'     : [0.02, 0.01, 0.03, 0.03],
        'rank_test_score'    : [2, 4, 3, 1],
        'split0_train_score' : [0.8, 0.7, 0.8, 0.9],
        'split1_train_score' : [0.82, 0.7, 0.82, 0.5],
        'mean_train_score'   : [0.81, 0.7, 0.81, 0.7],
        'std_train_score'    : [0.03, 0.04, 0.03, 0.03],
        'mean_fit_time'      : [0.73, 0.63, 0.43, 0.49],
        'std_fit_time'       : [0.01, 0.02, 0.01, 0.01],
        'mean_score_time'    : [0.007, 0.06, 0.04, 0.04],
        'std_score_time'     : [0.001, 0.002, 0.003, 0.005],
        'params'             : [{{'kernel': 'poly', 'degree': 2}}, ...],
        }}

    NOTE that the key ``'params'`` is used to store a list of parameter
    settings dict for all the parameter candidates.

    The ``mean_fit_time``, ``std_fit_time``, ``mean_score_time`` and
    ``std_score_time`` are all in seconds.

best_estimator_ : estimator
    Estimator that was chosen by the search, i.e. estimator
    which gave highest score (or smallest loss if specified)
    on the left out data. Not available if refit=False.

best_score_ : float or dict of floats
    Score of best_estimator on the left out data.
    When using multiple metrics, ``best_score_`` will be a dictionary
    where the keys are the names of the scorers, and the values are
    the mean test score for that scorer.

best_params_ : dict
    Parameter setting that gave the best results on the hold out data.

best_index_ : int or dict of ints
    The index (of the ``cv_results_`` arrays) which corresponds to the best
    candidate parameter setting.

    The dict at ``search.cv_results_['params'][search.best_index_]`` gives
    the parameter setting for the best model, that gives the highest
    mean score (``search.best_score_``).

    When using multiple metrics, ``best_index_`` will be a dictionary
    where the keys are the names of the scorers, and the values are
    the index with the best mean score for that scorer, as described above.

scorer_ : function or dict of functions
    Scorer function used on the held out data to choose the best
    parameters for the model. A dictionary of ``{{scorer_name: scorer}}``
    when multiple metrics are used.

n_splits_ : int
    The number of cross-validation splits (folds/iterations).

Notes
------
The parameters selected are those that maximize the score of the left out
data, unless an explicit score is passed in which case it is used instead.
"""

_grid_oneliner = """\
Exhaustive search over specified parameter values for an estimator.\
"""
_grid_description = """\
The parameters of the estimator used to apply these methods are optimized
by cross-validated grid-search over a parameter grid.\
"""
_grid_parameters = """\
param_grid : dict or list of dictionaries
    Dictionary with parameters names (string) as keys and lists of
    parameter settings to try as values, or a list of such
    dictionaries, in which case the grids spanned by each dictionary
    in the list are explored. This enables searching over any sequence
    of parameter settings.\
"""
_grid_example = """\
>>> import dask_searchcv as dcv
>>> from sklearn import svm, datasets
>>> iris = datasets.load_iris()
>>> parameters = {'kernel': ['linear', 'rbf'], 'C': [1, 10]}
>>> svc = svm.SVC()
>>> clf = dcv.GridSearchCV(svc, parameters)
>>> clf.fit(iris.data, iris.target)  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
GridSearchCV(cache_cv=..., cv=..., error_score=...,
        estimator=SVC(C=..., cache_size=..., class_weight=..., coef0=...,
                      decision_function_shape=..., degree=..., gamma=...,
                      kernel=..., max_iter=-1, probability=False,
                      random_state=..., shrinking=..., tol=...,
                      verbose=...),
        iid=..., n_jobs=..., param_grid=..., refit=..., return_train_score=...,
        scheduler=..., scoring=...)
>>> sorted(clf.cv_results_.keys())  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
['mean_fit_time', 'mean_score_time', 'mean_test_score',...
 'mean_train_score', 'param_C', 'param_kernel', 'params',...
 'rank_test_score', 'split0_test_score',...
 'split0_train_score', 'split1_test_score', 'split1_train_score',...
 'split2_test_score', 'split2_train_score',...
 'std_fit_time', 'std_score_time', 'std_test_score', 'std_train_score'...]\
"""


class ModelSearchCV(GridSearchCV):
    __doc__ = _DOC_TEMPLATE.format(name="ModelSearchCV",
                                   oneliner=_grid_oneliner,
                                   description=_grid_description,
                                   parameters=_grid_parameters,
                                   example=_grid_example)

    def __init__(self,
                 estimators,
                 param_grids,
                 scoring=None,
                 iid=True,
                 refit=True,
                 cv=None,
                 error_score='raise',
                 return_train_score=_RETURN_TRAIN_SCORE_DEFAULT,
                 scheduler='multiprocessing',
                 n_jobs=-1,
                 cache_cv=True,
                 verbose=True):
        self.estimators = estimators
        self.param_grids = param_grids
        self.verbose = verbose
        estimator = _ParametrizedClassifiers(estimators) \
            if check_estimator_type(estimators) == 'classifier' \
            else _ParametrizedRegressors(estimators)
        super(ModelSearchCV, self).__init__(estimator=estimator,
                                            param_grid=check_param_grids(param_grids, estimators),
                                            scoring=scoring,
                                            iid=iid,
                                            refit=refit,
                                            cv=cv,
                                            error_score=error_score,
                                            return_train_score=return_train_score,
                                            scheduler=scheduler,
                                            n_jobs=n_jobs,
                                            cache_cv=cache_cv)

    @staticmethod
    def _split_est_name(param_grid):
        """Split the estimator name."""

        # Exclude random state
        param_grid = {param:value for param, value in param_grid.items() if param != 'random_state'}

        # Remove and get the estimator name
        est_name = param_grid.pop('est_name')

        return est_name, {'__'.join(param.split('__')[1:]):value for param, value in param_grid.items()}

    def _modify_grid_search_attrs(self):
        """Modify the object's grid search attributes."""

        # Create best estimator attribte
        if hasattr(self, 'best_estimator_'):
            self.best_estimator_ = self.best_estimator_.estimator_
        
        # Populate models list
        models = []
        for ind, param_grid in enumerate(self.cv_results_['params']):
            est_name, self.cv_results_['params'][ind] = self._split_est_name(param_grid)
            models.append(est_name)
        
        # Append models list to results
        self.cv_results_.update({'models': models})

    def fit(self, X, y=None, groups=None, **fit_params):

        # Print progress bas
        if self.verbose:
            n_fitting_tasks = len(self._get_param_iterator()) * check_cv(self.cv).n_splits + int(self.refit)
            self.estimator._create_progress_bar(n_fitting_tasks, self.scheduler)

        # Call superclass fit method
        super(ModelSearchCV, self).fit(X, y, groups, **fit_params)
        
        # Modify attributes
        self._modify_grid_search_attrs()

        return self

