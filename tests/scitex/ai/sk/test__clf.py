#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2025-06-01 12:52:00 (ywatanabe)"
# File: ./tests/scitex/ai/sk/test__clf.py

"""Tests for scitex.ai.sk._clf module."""

import pytest
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sktime.transformations.panel.rocket import Rocket
from sktime.transformations.panel.reduce import Tabularizer
from scitex.ai.sk import rocket_pipeline, GB_pipeline


class TestRocketPipeline:
    """Test suite for rocket_pipeline function."""

    def test_rocket_pipeline_creation(self):
        """Test that rocket_pipeline creates a valid pipeline."""
        pipeline = rocket_pipeline()
        
        assert isinstance(pipeline, Pipeline)
        assert len(pipeline.steps) == 2
        
        # Check pipeline components
        assert isinstance(pipeline.steps[0][1], Rocket)
        assert isinstance(pipeline.steps[1][1], LogisticRegression)

    def test_rocket_pipeline_with_args(self):
        """Test rocket_pipeline with custom arguments."""
        pipeline = rocket_pipeline(n_kernels=100, random_state=42)
        
        assert isinstance(pipeline, Pipeline)
        rocket_transform = pipeline.steps[0][1]
        assert rocket_transform.n_kernels == 100
        assert rocket_transform.random_state == 42

    def test_rocket_pipeline_methods(self):
        """Test that the pipeline has expected sklearn methods."""
        pipeline = rocket_pipeline()
        
        assert hasattr(pipeline, 'fit')
        assert hasattr(pipeline, 'predict')
        assert hasattr(pipeline, 'fit_predict')
        assert hasattr(pipeline, 'score')
        assert hasattr(pipeline, 'transform')

    def test_rocket_pipeline_logistic_regression_params(self):
        """Test that LogisticRegression has correct parameters."""
        pipeline = rocket_pipeline()
        lr = pipeline.steps[1][1]
        
        assert lr.max_iter == 1000
        assert isinstance(lr, LogisticRegression)

    def test_rocket_pipeline_step_names(self):
        """Test that pipeline steps have appropriate names."""
        pipeline = rocket_pipeline()
        
        step_names = [name for name, _ in pipeline.steps]
        assert 'rocket' in step_names[0].lower()
        assert 'logisticregression' in step_names[1].lower()

    @pytest.mark.parametrize("n_kernels", [10, 50, 100])
    def test_rocket_pipeline_different_kernels(self, n_kernels):
        """Test rocket_pipeline with different numbers of kernels."""
        pipeline = rocket_pipeline(n_kernels=n_kernels)
        
        rocket = pipeline.steps[0][1]
        assert rocket.n_kernels == n_kernels

    def test_rocket_pipeline_kwargs_passthrough(self):
        """Test that kwargs are properly passed to Rocket."""
        custom_kwargs = {
            'n_kernels': 200,
            'normalise': False,
            'random_state': 123,
            'n_jobs': 2
        }
        
        pipeline = rocket_pipeline(**custom_kwargs)
        rocket = pipeline.steps[0][1]
        
        assert rocket.n_kernels == 200
        assert rocket.normalise == False
        assert rocket.random_state == 123
        assert rocket.n_jobs == 2


class TestGBPipeline:
    """Test suite for GB_pipeline."""

    def test_gb_pipeline_structure(self):
        """Test that GB_pipeline has correct structure."""
        assert isinstance(GB_pipeline, Pipeline)
        assert len(GB_pipeline.steps) == 2
        
        # Check pipeline components
        assert isinstance(GB_pipeline.steps[0][1], Tabularizer)
        assert isinstance(GB_pipeline.steps[1][1], GradientBoostingClassifier)

    def test_gb_pipeline_methods(self):
        """Test that GB_pipeline has expected sklearn methods."""
        assert hasattr(GB_pipeline, 'fit')
        assert hasattr(GB_pipeline, 'predict')
        assert hasattr(GB_pipeline, 'fit_predict')
        assert hasattr(GB_pipeline, 'score')

    def test_gb_pipeline_step_names(self):
        """Test that GB_pipeline steps have appropriate names."""
        step_names = [name for name, _ in GB_pipeline.steps]
        assert 'tabularizer' in step_names[0].lower()
        assert 'gradientboostingclassifier' in step_names[1].lower()

    def test_gb_pipeline_immutability(self):
        """Test that GB_pipeline is the same object each time."""
        from scitex.ai.sk import GB_pipeline as gb1
        from scitex.ai.sk import GB_pipeline as gb2
        
        assert gb1 is gb2  # Same object reference

    def test_gb_pipeline_clone(self):
        """Test that GB_pipeline can be cloned."""
        from sklearn.base import clone
        
        cloned_pipeline = clone(GB_pipeline)
        
        assert isinstance(cloned_pipeline, Pipeline)
        assert cloned_pipeline is not GB_pipeline
        assert len(cloned_pipeline.steps) == len(GB_pipeline.steps)


class TestPipelineIntegration:
    """Test integration aspects of the pipelines."""

    @pytest.fixture
    def sample_sktime_data(self):
        """Create sample data in sktime format."""
        n_samples, n_dims, n_timepoints = 20, 3, 50
        
        # Create sktime-formatted data
        data_list = []
        for i in range(n_samples):
            sample_data = []
            for d in range(n_dims):
                ts = pd.Series(np.random.randn(n_timepoints), name=f"dim_{d}")
                sample_data.append(ts)
            data_list.append(pd.Series(sample_data))
        
        X = pd.DataFrame(data_list)
        y = np.random.randint(0, 2, size=n_samples)
        
        return X, y

    def test_rocket_pipeline_fit_predict(self, sample_sktime_data):
        """Test that rocket_pipeline can fit and predict."""
        X, y = sample_sktime_data
        
        pipeline = rocket_pipeline(n_kernels=10)  # Small for speed
        
        # Should not raise any errors
        pipeline.fit(X, y)
        predictions = pipeline.predict(X)
        
        assert len(predictions) == len(y)
        assert all(pred in [0, 1] for pred in predictions)

    def test_gb_pipeline_fit_predict(self, sample_sktime_data):
        """Test that GB_pipeline can fit and predict."""
        X, y = sample_sktime_data
        
        # Clone to avoid modifying the global object
        from sklearn.base import clone
        pipeline = clone(GB_pipeline)
        
        # Should not raise any errors
        pipeline.fit(X, y)
        predictions = pipeline.predict(X)
        
        assert len(predictions) == len(y)
        assert all(pred in [0, 1] for pred in predictions)

    def test_pipeline_probability_predictions(self, sample_sktime_data):
        """Test probability predictions from pipelines."""
        X, y = sample_sktime_data
        
        # Test rocket_pipeline
        rocket = rocket_pipeline(n_kernels=10)
        rocket.fit(X, y)
        proba = rocket.predict_proba(X)
        
        assert proba.shape == (len(y), 2)
        assert np.allclose(proba.sum(axis=1), 1.0)
        
        # Test GB_pipeline
        from sklearn.base import clone
        gb = clone(GB_pipeline)
        gb.fit(X, y)
        proba_gb = gb.predict_proba(X)
        
        assert proba_gb.shape == (len(y), 2)
        assert np.allclose(proba_gb.sum(axis=1), 1.0)

    def test_pipeline_scoring(self, sample_sktime_data):
        """Test that pipelines can compute scores."""
        X, y = sample_sktime_data
        
        # Test rocket_pipeline
        rocket = rocket_pipeline(n_kernels=10)
        rocket.fit(X, y)
        score = rocket.score(X, y)
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
        
        # Test GB_pipeline
        from sklearn.base import clone
        gb = clone(GB_pipeline)
        gb.fit(X, y)
        score_gb = gb.score(X, y)
        
        assert isinstance(score_gb, float)
        assert 0 <= score_gb <= 1

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/sk/_clf.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "2024-03-23 17:36:05 (ywatanabe)"
# 
# import numpy as np
# from sklearn.decomposition import PCA
# from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
# from sklearn.feature_selection import SelectKBest, f_classif
# from sklearn.linear_model import LogisticRegression, RidgeClassifierCV
# from sklearn.pipeline import make_pipeline
# from sklearn.svm import SVC, LinearSVC
# from sktime.classification.deep_learning.cnn import CNNClassifier
# from sktime.classification.deep_learning.inceptiontime import (
#     InceptionTimeClassifier,
# )
# from sktime.classification.deep_learning.lstmfcn import LSTMFCNClassifier
# from sktime.classification.dummy import DummyClassifier
# from sktime.classification.feature_based import TSFreshClassifier
# from sktime.classification.hybrid import HIVECOTEV2
# from sktime.classification.interval_based import TimeSeriesForestClassifier
# from sktime.classification.kernel_based import RocketClassifier, TimeSeriesSVC
# from sktime.transformations.panel.reduce import Tabularizer
# from sktime.transformations.panel.rocket import Rocket
# 
# # _rocket_pipeline = make_pipeline(
# #     Rocket(n_jobs=-1),
# #     RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)),
# # )
# 
# 
# # def rocket_pipeline(*args, **kwargs):
# #     return _rocket_pipeline
# 
# 
# def rocket_pipeline(*args, **kwargs):
#     return make_pipeline(
#         Rocket(*args, **kwargs),
#         LogisticRegression(
#             max_iter=1000
#         ),  # Increase max_iter if needed for convergence
#         # RidgeClassifierCV(alphas=np.logspace(-3, 3, 10)),
#         # SVC(probability=True, kernel="linear"),
#     )
# 
# 
# # def rocket_pipeline(*args, **kwargs):
# #     return make_pipeline(
# #         Rocket(*args, **kwargs),
# #         SelectKBest(f_classif, k=500),
# #         PCA(n_components=100),
# #         LinearSVC(dual=False, tol=1e-3, C=0.1, probability=True),
# #     )
# 
# 
# GB_pipeline = make_pipeline(
#     Tabularizer(),
#     GradientBoostingClassifier(),
# )

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/ai/sk/_clf.py
# --------------------------------------------------------------------------------
