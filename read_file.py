import re
from pathlib import Path
from typing import Dict

import pandas as pd


class ReadData(object):

    def __init__(self, instance: str) -> None:
        self._instance = instance

    def get_df(self):
        path_to_read = Path.cwd() / "data" / Path(self._instance)
        self._instance = path_to_read
        sep = self._detect_delimiter()
        column_names = self._generate_cols(sep=sep)
        df = pd.read_csv(
            self._instance,
            sep=sep,
            header=None,
            lineterminator="\n",
            engine="c",
            names=column_names,
        )
        return df

    def _detect_delimiter(self) -> str:
        with open(self._instance) as f:
            line = f.readline()
        if len(re.split("\t", line)) > 1:
            return "\t"
        else:
            return r"\s+"

    def _generate_cols(self, sep: str) -> list:
        with open(self._instance, "r", encoding="utf-8") as temp_f:
            col_count = [len(re.split(sep, l.strip())) for l in temp_f.readlines()]
        column_names = [i for i in range(max(col_count))]
        return column_names
