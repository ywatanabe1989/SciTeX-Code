#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "ywatanabe (2024-11-07 16:06:50)"
# File: ./scitex_repo/src/scitex/gen/_TimeStamper.py

import time
from typing import Union, Optional
import pandas as pd


class TimeStamper:
    """
    Functionality:
        * Generates timestamps with comments and tracks elapsed time
        * Records timestamps in a DataFrame for analysis
        * Calculates time differences between timestamps
    Input:
        * Comments for each timestamp
        * Format preference (simple or detailed)
    Output:
        * Formatted timestamp strings
        * DataFrame with timestamp records
        * Time differences between specified timestamps
    Prerequisites:
        * pandas
    """

    def __init__(self, is_simple: bool = True) -> None:
        self.id: int = -1
        self.start_time: float = time.time()
        self._is_simple: bool = is_simple
        self._prev: float = self.start_time
        self._df_record: pd.DataFrame = pd.DataFrame(
            columns=[
                "timestamp",
                "elapsed_since_start",
                "elapsed_since_prev",
                "comment",
                "formatted_text",
            ]
        )

    def __call__(self, comment: str = "", verbose: bool = False) -> str:
        now: float = time.time()
        from_start: float = now - self.start_time
        from_prev: float = now - self._prev

        formatted_from_start: str = time.strftime("%H:%M:%S", time.gmtime(from_start))
        formatted_from_prev: str = time.strftime("%H:%M:%S", time.gmtime(from_prev))

        self.id += 1
        self._prev = now

        text: str = (
            f"ID:{self.id} | {formatted_from_start} {comment} | "
            if self._is_simple
            else f"Time (id:{self.id}): total {formatted_from_start}, prev {formatted_from_prev} [hh:mm:ss]: {comment}\n"
        )

        self._df_record.loc[self.id] = [
            now,
            from_start,
            from_prev,
            comment,
            text,
        ]

        if verbose:
            print(text)
        return text

    @property
    def record(self) -> pd.DataFrame:
        """Returns the record DataFrame without the formatted_text column."""
        return self._df_record[
            [
                "timestamp",
                "elapsed_since_start",
                "elapsed_since_prev",
                "comment",
            ]
        ]

    def delta(self, id1: int, id2: int) -> float:
        """Calculates time difference between two timestamps.

        Parameters
        ----------
        id1 : int
            First timestamp ID
        id2 : int
            Second timestamp ID

        Returns
        -------
        float
            Time difference in seconds

        Raises
        ------
        ValueError
            If IDs don't exist in records
        """
        if id1 < 0:
            id1 = len(self._df_record) + id1
        if id2 < 0:
            id2 = len(self._df_record) + id2

        if not all(idx in self._df_record.index for idx in [id1, id2]):
            raise ValueError("Invalid timestamp ID(s)")

        return (
            self._df_record.loc[id1, "timestamp"]
            - self._df_record.loc[id2, "timestamp"]
        )


if __name__ == "__main__":
    ts = TimeStamper(is_simple=True)
    ts("Starting process")
    time.sleep(1)
    ts("One second later")
    time.sleep(2)
    ts("Two seconds later")


# EOF

# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# # Time-stamp: "ywatanabe (2024-11-07 16:06:50)"
# # File: ./scitex_repo/src/scitex/gen/_TimeStamper.py

# import time
# import pandas as pd


# class TimeStamper:
#     """
#     A class for generating timestamps with optional comments, tracking both the time since object creation and since the last call.
#     """

#     def __init__(self, is_simple=True):
#         self.id = -1
#         self.start_time = time.time()
#         self._is_simple = is_simple
#         self._prev = self.start_time
#         self._df_record = pd.DataFrame(
#             columns=[
#                 "timestamp",
#                 "elapsed_since_start",
#                 "elapsed_since_prev",
#                 "comment",
#                 "formatted_text",
#             ]
#         )

#     def __call__(self, comment="", verbose=False):
#         now = time.time()
#         from_start = now - self.start_time
#         from_prev = now - self._prev
#         formatted_from_start = time.strftime(
#             "%H:%M:%S", time.gmtime(from_start)
#         )
#         formatted_from_prev = time.strftime("%H:%M:%S", time.gmtime(from_prev))
#         self.id += 1
#         self._prev = now
#         text = (
#             f"ID:{self.id} | {formatted_from_start} {comment} | "
#             if self._is_simple
#             else f"Time (id:{self.id}): total {formatted_from_start}, prev {formatted_from_prev} [hh:mm:ss]: {comment}\n"
#         )

#         # Update DataFrame directly
#         self._df_record.loc[self.id] = [
#             now,
#             from_start,
#             from_prev,
#             comment,
#             text,
#         ]

#         if verbose:
#             print(text)
#         return text

#     @property
#     def record(self):
#         return self._df_record[
#             [
#                 "timestamp",
#                 "elapsed_since_start",
#                 "elapsed_since_prev",
#                 "comment",
#             ]
#         ]

#     def delta(self, id1, id2):
#         """
#         Calculate the difference in seconds between two timestamps identified by their IDs.

#         Parameters:
#             id1 (int): The ID of the first timestamp.
#             id2 (int): The ID of the second timestamp.

#         Returns:
#             float: The difference in seconds between the two timestamps.

#         Raises:
#             ValueError: If either id1 or id2 is not in the DataFrame index.
#         """
#         # Adjust for negative indices, similar to negative list indexing in Python
#         if id1 < 0:
#             id1 = len(self._df_record) + id1
#         if id2 < 0:
#             id2 = len(self._df_record) + id2

#         # Check if both IDs exist in the DataFrame
#         if (
#             id1 not in self._df_record.index
#             or id2 not in self._df_record.index
#         ):
#             raise ValueError(
#                 "One or both of the IDs do not exist in the record."
#             )

#         # Compute the difference in timestamps
#         time_diff = (
#             self._df_record.loc[id1, "timestamp"]
#             - self._df_record.loc[id2, "timestamp"]
#         )
#         return time_diff


# if __name__ == "__main__":
#     ts = TimeStamper(is_simple=True)
#     ts("Starting process")
#     time.sleep(1)
#     ts("One second later")
#     time.sleep(2)
#     ts("Two seconds later")


# # EOF
