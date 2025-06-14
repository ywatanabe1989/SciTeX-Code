#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-12 14:01:00 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/.claude-worktree/scitex_repo/tests/scitex/io/_save_modules/test__save_optuna_study_as_csv_and_pngs.py
# ----------------------------------------
import os

__FILE__ = "./tests/scitex/io/_save_modules/test__save_optuna_study_as_csv_and_pngs.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Test cases for saving Optuna study as CSV and PNG files
"""

import os
import tempfile
import pytest
import numpy as np
from pathlib import Path

try:
    import optuna
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

    from scitex.io._save_modules import save_optuna_study_as_csv_and_pngs


@pytest.mark.skipif(not OPTUNA_AVAILABLE, reason="Optuna not installed")
class TestSaveOptunaStudyAsCSVAndPNGs:
    """Test suite for save_optuna_study_as_csv_and_pngs function"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.output_prefix = os.path.join(self.temp_dir, "optuna_study")

    def teardown_method(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def create_simple_study(self):
        """Create a simple Optuna study for testing"""
        def objective(trial):
            x = trial.suggest_float("x", -10, 10)
            y = trial.suggest_float("y", -10, 10)
            return (x - 2) ** 2 + (y + 3) ** 2
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=20)
        return study

    def test_save_basic_study(self):
        """Test saving basic Optuna study"""
        study = self.create_simple_study()
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # Check CSV files exist
        assert os.path.exists(f"{self.output_prefix}_trials.csv")
        assert os.path.exists(f"{self.output_prefix}_best_params.csv")
        
        # Check PNG files exist
        assert os.path.exists(f"{self.output_prefix}_optimization_history.png")
        assert os.path.exists(f"{self.output_prefix}_param_importances.png")

    def test_save_multi_objective_study(self):
        """Test saving multi-objective study"""
        def multi_objective(trial):
            x = trial.suggest_float("x", 0, 5)
            y = trial.suggest_float("y", 0, 5)
            obj1 = x ** 2
            obj2 = (x - 2) ** 2 + y ** 2
            return obj1, obj2
        
        study = optuna.create_study(
            directions=["minimize", "minimize"]
        )
        study.optimize(multi_objective, n_trials=30)
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # Multi-objective studies should have pareto front plot
        assert os.path.exists(f"{self.output_prefix}_pareto_front.png")

    def test_save_categorical_params_study(self):
        """Test saving study with categorical parameters"""
        def objective(trial):
            classifier = trial.suggest_categorical(
                "classifier", ["SVM", "RandomForest", "XGBoost"]
            )
            if classifier == "SVM":
                c = trial.suggest_float("svm_c", 0.1, 10)
                return c * 0.1
            elif classifier == "RandomForest":
                n_estimators = trial.suggest_int("rf_n_estimators", 10, 100)
                return 100 / n_estimators
            else:
                learning_rate = trial.suggest_float("xgb_lr", 0.01, 0.3)
                return learning_rate
        
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=30)
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # Check files exist
        assert os.path.exists(f"{self.output_prefix}_trials.csv")

    def test_save_with_custom_plots(self):
        """Test saving with custom plot selection"""
        study = self.create_simple_study()
        
        # Specify which plots to generate
        plots = ["optimization_history", "param_importances", "contour"]
        save_optuna_study_as_csv_and_pngs(
            study, 
            self.output_prefix,
            plots=plots
        )
        
        # Check specified plots exist
        assert os.path.exists(f"{self.output_prefix}_optimization_history.png")
        assert os.path.exists(f"{self.output_prefix}_param_importances.png")
        assert os.path.exists(f"{self.output_prefix}_contour.png")

    def test_save_pruned_trials(self):
        """Test saving study with pruned trials"""
        def objective(trial):
            # Simulate pruning
            for step in range(10):
                value = trial.suggest_float(f"x_{step}", 0, 1)
                if step > 5 and value < 0.3:
                    raise optuna.TrialPruned()
            return sum(trial.params.values())
        
        study = optuna.create_study(
            direction="minimize",
            pruner=optuna.pruners.MedianPruner()
        )
        study.optimize(objective, n_trials=20)
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # Check that pruned trials are included in CSV
        import pandas as pd
        trials_df = pd.read_csv(f"{self.output_prefix}_trials.csv")
        assert "state" in trials_df.columns

    def test_save_with_user_attrs(self):
        """Test saving study with user attributes"""
        def objective(trial):
            x = trial.suggest_float("x", 0, 1)
            
            # Set user attributes
            trial.set_user_attr("squared", x ** 2)
            trial.set_user_attr("category", "A" if x > 0.5 else "B")
            
            return x
        
        study = optuna.create_study()
        study.optimize(objective, n_trials=10)
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # Check user attributes in CSV
        import pandas as pd
        trials_df = pd.read_csv(f"{self.output_prefix}_trials.csv")
        assert "user_attr_squared" in trials_df.columns or "squared" in trials_df.columns

    def test_save_large_study(self):
        """Test saving large study with many trials"""
        def objective(trial):
            return sum(
                trial.suggest_float(f"x{i}", -1, 1) ** 2
                for i in range(5)
            )
        
        study = optuna.create_study()
        study.optimize(objective, n_trials=100)
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # Check all files generated
        import pandas as pd
        trials_df = pd.read_csv(f"{self.output_prefix}_trials.csv")
        assert len(trials_df) == 100

    def test_save_study_with_constraints(self):
        """Test saving study with constraints"""
        def objective(trial):
            x = trial.suggest_float("x", -10, 10)
            y = trial.suggest_float("y", -10, 10)
            
            # Add constraint
            c = x + y - 5
            trial.set_user_attr("constraint", c)
            
            return x ** 2 + y ** 2
        
        study = optuna.create_study()
        study.optimize(objective, n_trials=30)
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # Constraint should be in trials data
        import pandas as pd
        trials_df = pd.read_csv(f"{self.output_prefix}_trials.csv")
        assert any("constraint" in col for col in trials_df.columns)

    def test_save_empty_study(self):
        """Test handling empty study"""
        study = optuna.create_study()
        
        # Should handle empty study gracefully
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # At least trials CSV should exist (even if empty)
        assert os.path.exists(f"{self.output_prefix}_trials.csv")

    def test_save_with_datetime_params(self):
        """Test saving study with datetime parameters"""
        from datetime import datetime, timedelta
        
        def objective(trial):
            # Optuna doesn't directly support datetime, but we can use user attrs
            days_offset = trial.suggest_int("days_offset", 0, 30)
            trial.set_user_attr("date", str(datetime.now() + timedelta(days=days_offset)))
            return days_offset
        
        study = optuna.create_study()
        study.optimize(objective, n_trials=10)
        
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        assert os.path.exists(f"{self.output_prefix}_trials.csv")

    def test_visualization_error_handling(self):
        """Test handling of visualization errors"""
        # Create study with single trial (some plots need multiple trials)
        def objective(trial):
            return trial.suggest_float("x", 0, 1)
        
        study = optuna.create_study()
        study.optimize(objective, n_trials=1)
        
        # Should not crash even if some visualizations fail
        save_optuna_study_as_csv_and_pngs(study, self.output_prefix)
        
        # CSV should still be created
        assert os.path.exists(f"{self.output_prefix}_trials.csv")

    def test_save_with_custom_filename(self):
        """Test saving with custom filename pattern"""
        study = self.create_simple_study()
        
        custom_path = os.path.join(self.temp_dir, "my_experiment/results")
        os.makedirs(os.path.dirname(custom_path), exist_ok=True)
        
        save_optuna_study_as_csv_and_pngs(study, custom_path)
        
        assert os.path.exists(f"{custom_path}_trials.csv")
        assert os.path.exists(f"{custom_path}_optimization_history.png")

    def test_parallel_coordinate_plot(self):
        """Test parallel coordinate plot for high-dimensional studies"""
        def objective(trial):
            return sum(
                trial.suggest_float(f"x{i}", -1, 1) ** 2
                for i in range(10)
            )
        
        study = optuna.create_study()
        study.optimize(objective, n_trials=50)
        
        save_optuna_study_as_csv_and_pngs(
            study, 
            self.output_prefix,
            plots=["parallel_coordinate"]
        )
        
        assert os.path.exists(f"{self.output_prefix}_parallel_coordinate.png")


# EOF