#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 13:54:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__catboost.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__catboost.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for CatBoost model saving functionality
"""

import os
import tempfile
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

try:
    import catboost
    from catboost import CatBoostClassifier, CatBoostRegressor
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False

    from scitex.io._save_modules import _save_catboost as save_catboost


@pytest.mark.skipif(not CATBOOST_AVAILABLE, reason="CatBoost not installed")
class TestSaveCatBoost:
    """Test suite for save_catboost function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_model.cbm")
        
        # Create sample data
        np.random.seed(42)
        self.X_train = np.random.randn(100, 5)
        self.y_train_clf = np.random.randint(0, 2, 100)
        self.y_train_reg = np.random.randn(100)

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_classifier(self):
        """Test saving CatBoost classifier"""
        model = CatBoostClassifier(
            iterations=10,
            depth=3,
            learning_rate=0.1,
            loss_function='Logloss',
            verbose=False
        )
        model.fit(self.X_train, self.y_train_clf)
        
        save_catboost(model, self.test_file)
        
        assert os.path.exists(self.test_file)
        
        # Load and verify
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        # Check predictions are the same
        original_pred = model.predict(self.X_train)
        loaded_pred = loaded_model.predict(self.X_train)
        np.testing.assert_array_equal(original_pred, loaded_pred)

    def test_save_regressor(self):
        """Test saving CatBoost regressor"""
        model = CatBoostRegressor(
            iterations=10,
            depth=3,
            learning_rate=0.1,
            loss_function='RMSE',
            verbose=False
        )
        model.fit(self.X_train, self.y_train_reg)
        
        save_catboost(model, self.test_file)
        
        assert os.path.exists(self.test_file)
        
        # Load and verify
        loaded_model = CatBoostRegressor()
        loaded_model.load_model(self.test_file)
        
        # Check predictions are close
        original_pred = model.predict(self.X_train)
        loaded_pred = loaded_model.predict(self.X_train)
        np.testing.assert_array_almost_equal(original_pred, loaded_pred)

    def test_save_with_categorical_features(self):
        """Test saving model trained with categorical features"""
        # Create data with categorical features
        X_cat = pd.DataFrame({
            'num1': np.random.randn(100),
            'num2': np.random.randn(100),
            'cat1': np.random.choice(['A', 'B', 'C'], 100),
            'cat2': np.random.choice(['X', 'Y'], 100)
        })
        y = np.random.randint(0, 2, 100)
        
        cat_features = ['cat1', 'cat2']
        
        model = CatBoostClassifier(
            iterations=10,
            verbose=False,
            cat_features=cat_features
        )
        model.fit(X_cat, y)
        
        save_catboost(model, self.test_file)
        
        # Load and verify
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        # Test on new data
        X_test = pd.DataFrame({
            'num1': [0.5],
            'num2': [-0.5],
            'cat1': ['B'],
            'cat2': ['X']
        })
        
        original_pred = model.predict(X_test)
        loaded_pred = loaded_model.predict(X_test)
        assert original_pred[0] == loaded_pred[0]

    def test_save_multiclass_classifier(self):
        """Test saving multiclass classifier"""
        y_multiclass = np.random.randint(0, 3, 100)
        
        model = CatBoostClassifier(
            iterations=10,
            loss_function='MultiClass',
            verbose=False
        )
        model.fit(self.X_train, y_multiclass)
        
        save_catboost(model, self.test_file)
        
        # Load and verify
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        original_pred = model.predict(self.X_train)
        loaded_pred = loaded_model.predict(self.X_train)
        np.testing.assert_array_equal(original_pred, loaded_pred)

    def test_save_with_early_stopping(self):
        """Test saving model trained with early stopping"""
        X_val = np.random.randn(20, 5)
        y_val = np.random.randint(0, 2, 20)
        
        model = CatBoostClassifier(
            iterations=100,
            early_stopping_rounds=10,
            verbose=False
        )
        model.fit(
            self.X_train, 
            self.y_train_clf,
            eval_set=(X_val, y_val)
        )
        
        save_catboost(model, self.test_file)
        
        # Load and verify
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        # Check that best iteration is preserved
        assert loaded_model.best_iteration_ == model.best_iteration_

    def test_save_with_custom_metric(self):
        """Test saving model with custom evaluation metric"""
        model = CatBoostClassifier(
            iterations=10,
            eval_metric='AUC',
            verbose=False
        )
        model.fit(self.X_train, self.y_train_clf)
        
        save_catboost(model, self.test_file)
        
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        # Verify model parameters are preserved
        assert loaded_model.get_params()['eval_metric'] == 'AUC'

    def test_save_json_format(self):
        """Test saving in JSON format"""
        model = CatBoostClassifier(iterations=5, verbose=False)
        model.fit(self.X_train, self.y_train_clf)
        
        json_file = os.path.join(self.temp_dir, "model.json")
        save_catboost(model, json_file, format="json")
        
        assert os.path.exists(json_file)
        
        # JSON format can be loaded
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(json_file, format="json")

    def test_save_with_feature_names(self):
        """Test saving model with feature names"""
        feature_names = ['feature1', 'feature2', 'feature3', 'feature4', 'feature5']
        df = pd.DataFrame(self.X_train, columns=feature_names)
        
        model = CatBoostClassifier(iterations=10, verbose=False)
        model.fit(df, self.y_train_clf)
        
        save_catboost(model, self.test_file)
        
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        # Feature names should be preserved
        assert loaded_model.feature_names_ == feature_names

    def test_save_pool_data(self):
        """Test saving model trained on Pool data"""
        pool = catboost.Pool(
            self.X_train, 
            self.y_train_clf,
            feature_names=['f1', 'f2', 'f3', 'f4', 'f5']
        )
        
        model = CatBoostClassifier(iterations=10, verbose=False)
        model.fit(pool)
        
        save_catboost(model, self.test_file)
        
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        # Test predictions
        test_pool = catboost.Pool(self.X_train[:5])
        original_pred = model.predict(test_pool)
        loaded_pred = loaded_model.predict(test_pool)
        np.testing.assert_array_equal(original_pred, loaded_pred)

    def test_error_non_catboost_model(self):
        """Test error handling for non-CatBoost models"""
        from sklearn.ensemble import RandomForestClassifier
        
        rf_model = RandomForestClassifier()
        rf_model.fit(self.X_train, self.y_train_clf)
        
        with pytest.raises(ValueError, match="Object must be a CatBoost model"):
            save_catboost(rf_model, self.test_file)

    def test_save_gpu_model(self):
        """Test saving GPU-trained model (if GPU available)"""
        try:
            model = CatBoostClassifier(
                iterations=10,
                task_type='GPU',
                devices='0',
                verbose=False
            )
            model.fit(self.X_train, self.y_train_clf)
            
            save_catboost(model, self.test_file)
            
            loaded_model = CatBoostClassifier()
            loaded_model.load_model(self.test_file)
            
            # GPU model can be loaded and used on CPU
            pred = loaded_model.predict(self.X_train[:5])
            assert len(pred) == 5
        except catboost.CatBoostError:
            pytest.skip("GPU not available for CatBoost")

    def test_save_with_text_features(self):
        """Test saving model with text features"""
        text_data = pd.DataFrame({
            'text': ['good product', 'bad quality', 'excellent service', 'poor support'] * 25,
            'rating': np.random.randn(100)
        })
        y = np.random.randint(0, 2, 100)
        
        model = CatBoostClassifier(
            iterations=10,
            text_features=['text'],
            verbose=False
        )
        model.fit(text_data, y)
        
        save_catboost(model, self.test_file)
        
        loaded_model = CatBoostClassifier()
        loaded_model.load_model(self.test_file)
        
        # Test on new text
        test_data = pd.DataFrame({'text': ['great product']})
        pred = loaded_model.predict(test_data)
        assert len(pred) == 1


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_catboost.py
# --------------------------------------------------------------------------------
# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-16 12:29:11 (ywatanabe)"
# # File: /data/gpfs/projects/punim2354/ywatanabe/scitex_repo/src/scitex/io/_save_modules/_catboost.py
# 
# 
# def _save_catboost(obj, spath):
#     """
#     Save a CatBoost model.
#     
#     Parameters
#     ----------
#     obj : catboost.CatBoost
#         The CatBoost model to save.
#     spath : str
#         Path where the CatBoost model file will be saved.
#         
#     Returns
#     -------
#     None
#     """
#     obj.save_model(spath)

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/SciTeX-Code/src/scitex/io/_save_modules/_catboost.py
# --------------------------------------------------------------------------------
