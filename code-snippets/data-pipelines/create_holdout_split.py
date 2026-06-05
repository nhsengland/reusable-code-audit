"""Source: P33 ELM4PSIR — https://github.com/nhsx/ELM4PSIR (utils/create_lm_data_split.py)"""

import pandas as pd
from sklearn.model_selection import train_test_split


def create_holdout_set(raw_data_file: str, save_path: str, hold_out_percentage: float = 0.10, seed: int = 42):
    all_data = pd.read_csv(raw_data_file, index_col=None)

    train_data, hold_data = train_test_split(
        all_data,
        test_size=hold_out_percentage,
        random_state=seed,
    )
    train_data.to_csv(f"{save_path}/training_data.csv", index=False)
    hold_data.to_csv(f"{save_path}/held_out_data.csv", index=False)

    lm_train_data, lm_test_data = train_test_split(
        train_data,
        test_size=hold_out_percentage,
        random_state=seed,
    )
    lm_train_data.to_csv(f"{save_path}/lm_training_data.csv", index=False)
    lm_test_data.to_csv(f"{save_path}/lm_test_data.csv", index=False)
