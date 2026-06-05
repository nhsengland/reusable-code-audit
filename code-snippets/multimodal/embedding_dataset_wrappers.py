"""Source: P22/P31 Txt-Ray Align — https://github.com/nhsx/txt-ray-align (embeddings.py)"""

import numpy as np
import pandas as pd
from torch.utils.data import Dataset


class TextDataset(Dataset):
    def __init__(self, data: str, val_data=None):
        self.data = pd.read_csv(data, index_col=0)[["study_id", "report"]]
        if val_data is not None:
            val_df = pd.read_csv(val_data, index_col=0)[["study_id", "report"]]
            self.data = pd.concat([self.data, val_df], ignore_index=True)

        self.data = self.data.dropna().drop_duplicates().reset_index(drop=True)
        self.keys = list(self.data.index)

    def __len__(self):
        return len(self.keys)

    def __getitem__(self, ind):
        key = self.keys[ind]
        text = str(self.data.loc[key]["report"]).replace("\n", "").replace("\r", "")
        return {"study_id": self.data.loc[key]["study_id"], "text": text}


class SentenceSplitMixin:
    @staticmethod
    def split_reports(data: pd.DataFrame) -> pd.DataFrame:
        data = data.copy()
        data["report"] = data["report"].str.split(".")
        data = data.explode("report").reset_index(drop=True)
        return data.replace("", np.nan).dropna().reset_index(drop=True)
