"""Source: P33 ELM4PSIR — https://github.com/nhsx/ELM4PSIR (utils/prepare_notes_for_lm.py)"""

import re
import pandas as pd
from tqdm import tqdm


def clean_data(notes_df: pd.DataFrame, text_col: str, replacement_map: list[tuple[str, str]], admin_language=None):
    filtered_df = notes_df.copy()

    for original, replacement in tqdm(replacement_map):
        filtered_df = filtered_df[filtered_df[text_col].notna()]
        if filtered_df.empty:
            return filtered_df
        filtered_df[text_col] = filtered_df[text_col].str.replace(original, replacement)

    if admin_language is not None:
        for admin_token in admin_language:
            filtered_df[text_col] = filtered_df[text_col].str.replace(admin_token, " ")

    filtered_df[text_col] = filtered_df[text_col].str.strip().str.lower()
    filtered_df[text_col] = [re.sub(r"\\s+", " ", x) for x in filtered_df[text_col]]
    return filtered_df.dropna()
