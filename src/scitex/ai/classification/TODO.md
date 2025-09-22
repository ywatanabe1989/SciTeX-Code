<!-- ---
!-- Timestamp: 2025-09-22 14:43:32
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification/TODO.md
!-- --- -->

- [ ] Create reporters directory
  - Current
    ```
    /ssh:sp:/home/ywatanabe/proj/scitex_repo/src/scitex/ml/classification:
    drwxr-sr-x  9 ywatanabe punim2354 4.0K Sep 22 14:29 .
    drwxr-sr-x 19 ywatanabe punim2354 4.0K Sep  7 08:17 ..
    -rwxr-xr-x  1 ywatanabe punim2354 8.9K Sep 22 14:24 _BaseClassificationReporter.py
    -rw-r--r--  1 ywatanabe punim2354  13K Sep 22 14:29 _ClassificationReporter.py
    -rwxr-xr-x  1 ywatanabe punim2354 4.6K Jul  1 21:35 _ClassifierServer.py
    -rwxr-xr-x  1 ywatanabe punim2354  11K Sep 22 13:16 cross_validation.py
    drwxr-sr-x  4 ywatanabe punim2354 4.0K Sep 22 13:16 examples
    -rwxr-xr-x  1 ywatanabe punim2354 2.0K Sep 22 14:29 __init__.py
    drwxr-sr-x  3 ywatanabe punim2354 4.0K Sep  7 12:39 legacy
    -rw-r--r--  1 ywatanabe punim2354  13K Sep 22 14:25 _MultiClassificationReporter.py
    drwxr-sr-x  2 ywatanabe punim2354 4.0K Sep 22 14:30 __pycache__
    -rw-r--r--  1 ywatanabe punim2354 7.1K Sep 22 13:16 README.md
    drwxr-sr-x  6 ywatanabe punim2354 4.0K Sep 22 13:22 reporter_utils
    -rwxr-xr-x  1 ywatanabe punim2354  43K Sep 22 14:24 _SingleClassificationReporter.py
    drwxr-sr-x  3 ywatanabe punim2354 4.0K Sep 21 21:24 time_series
    -rw-r--r--  1 ywatanabe punim2354  259 Sep 21 20:20 TODO.md
    ```
  - After
    ```
    reporters/_BaseClassificationReporter.py
    reporters/_ClassificationReporter.py
    reporters/_MultiClassificationreporter.py
    reporters/_SingleClassificationreporter.py
    reporters/reporter_utils/...
    ```
  - Then, expose only the unified version, ClassificationReporter

- [ ] Update demos using only unified API
  /ssh:sp:/home/ywatanabe/proj/scitex_repo/examples/classification_demo:
  drwxr-sr-x  8 ywatanabe punim2354 4.0K Sep 22 14:37 .
  drwxr-sr-x 18 ywatanabe punim2354 4.0K Sep 22 01:24 ..
  drwxr-sr-x  6 ywatanabe punim2354 4.0K Sep 22 01:28 00_generate_data_out
  -rwxr-xr-x  1 ywatanabe punim2354  11K Sep 22 01:27 00_generate_data.py
  drwxr-sr-x  4 ywatanabe punim2354 4.0K Sep 21 23:34 01_single_task_classification_out
  -rwxr-xr-x  1 ywatanabe punim2354 7.1K Sep 22 14:25 01_single_task_classification.py
  -rwxr-xr-x  1 ywatanabe punim2354 7.1K Sep 22 14:32 01_single_task_classification_unified_api.py
  drwxr-sr-x  4 ywatanabe punim2354 4.0K Sep 21 23:36 02_multi_task_classification_out
  -rwxr-xr-x  1 ywatanabe punim2354 7.2K Sep 22 14:25 02_multi_task_classification.py
  -rwxr-xr-x  1 ywatanabe punim2354 7.2K Sep 22 14:33 02_multi_task_classification_unified_api.py
  -rwxr-xr-x  1 ywatanabe punim2354  13K Sep 21 23:36 03_time_series_cv.py
  drwxr-sr-x  3 ywatanabe punim2354 4.0K Sep 22 01:18 examples
  drwxr-sr-x  2 ywatanabe punim2354 4.0K Sep 22 05:36 __pycache__
  -rw-r--r--  1 ywatanabe punim2354 3.5K Sep 21 21:23 README.md
  -rwxr-xr-x  1 ywatanabe punim2354 1004 Sep 21 23:21 run_all_examples.sh

<!-- EOF -->