# Reusable Code Catalog

Purpose: single, extensible catalog of reusable snippet patterns identified in the NHS internship project audit.

Date: 2025-06-05

> [!NOTE]
> **Total projects audited:** 21  
> **Total themes identified:** 7  
> **Total snippet files:** 14  
> **Total reuse candidates:** 14  
> **Most overlapped theme:** NLP / Text Processing (6 projects)

## Overlap Summary Table

| Theme | Projects with overlap | Overlap count | Snippet files | Top reuse candidate |
|---|---|---:|---:|---|
| Synthetic Data | P12, P21, P41, P11 | 4 | 2 | SD-001 |
| NLP / Text Processing | P72, P71, P51, P33, P23, P43 | 6 | 2 | NLP-001 |
| Multimodal | P22, P31, P61, P81 | 4 | 2 | MM-001 |
| Evaluation | P82, P71 | 2 | 2 | EVAL-001 |
| Explainability | P14, P24, P61, P81 | 4 | 2 | XAI-001 |
| Graph / Hypergraph | P34, P32 | 2 | 2 | GRAPH-001 |
| Data Pipelines | P33, P72, P52, P32, P51, P71 | 6 | 2 | DP-001 |

## Synthetic Data

### Which projects overlap

- [P12](https://github.com/nhsx/SynthVAE)
- [P21](https://github.com/nhsx/SynthVAE)
- [P41](https://github.com/nhsengland/NHSSynth)
- [P11](https://github.com/nhsx/SynPath_Diabetes)

### What the overlap is

Projects repeatedly implement synthetic tabular data evaluation and experiment I/O helpers around generation workflows.

### Snippet inventory

| ID | File | Source projects | Reuse candidate | Suggested module |
|---|---|---|---|---|
| SD-001 | [distribution_metrics.py](./code-snippets/synthetic-data/distribution_metrics.py) | P12, P21 | ✅ | `nhs_reuse.synthetic.metrics` |
| SD-002 | [experiment_io_helpers.py](./code-snippets/synthetic-data/experiment_io_helpers.py) | P41 | ✅ | `nhs_reuse.common.io` |

### Raw snippets

#### SD-001 — Synthetic data distribution metrics

File: [`code-snippets/synthetic-data/distribution_metrics.py`](./code-snippets/synthetic-data/distribution_metrics.py)

```python
"""Source: P12/P21 SynthVAE — https://github.com/nhsx/SynthVAE (metrics.py)"""

import numpy as np
import pandas as pd
import gower
from sdv.evaluation import evaluate
from sdv.metrics.tabular import NumericalMLP, CategoricalSVM


def distribution_metrics(distributional_metrics, data_supp, synthetic_supp, categorical_columns, include_gower=False):
    synthetic_supp = synthetic_supp[data_supp.columns]
    synthetic_supp[categorical_columns] = synthetic_supp[categorical_columns].astype(object)
    data_supp[categorical_columns] = data_supp[categorical_columns].astype(object)

    evals = evaluate(synthetic_supp, data_supp, metrics=distributional_metrics, aggregate=False)
    metrics = np.array(evals["raw_score"])

    if include_gower:
        metrics = np.append(metrics, np.mean(gower.gower_matrix(data_supp, synthetic_supp)))
        return pd.DataFrame(data=[metrics], columns=(distributional_metrics + ["Gower"]))

    return pd.DataFrame(data=[metrics], columns=distributional_metrics)


def privacy_metric(private_variable, data_supp, synthetic_supp, categorical_columns, continuous_columns):
    if private_variable in continuous_columns:
        key_fields = [c for c in continuous_columns if c != private_variable]
        return NumericalMLP.compute(
            data_supp.fillna(0),
            synthetic_supp.fillna(0),
            key_fields=key_fields,
            sensitive_fields=[private_variable],
        )

    key_fields = [c for c in categorical_columns if c != private_variable]
    return CategoricalSVM.compute(
        data_supp.fillna(0),
        synthetic_supp.fillna(0),
        key_fields=key_fields,
        sensitive_fields=[private_variable],
    )
```

#### SD-002 — Experiment I/O helpers

File: [`code-snippets/synthetic-data/experiment_io_helpers.py`](./code-snippets/synthetic-data/experiment_io_helpers.py)

```python
"""Source: P41 NHSSynth — https://github.com/nhsengland/NHSSynth (src/nhssynth/common/io.py)"""

from pathlib import Path


def experiment_io(experiment_name: str, dir_experiments: str = "experiments") -> Path:
    dir_experiment = Path(dir_experiments) / experiment_name
    dir_experiment.mkdir(parents=True, exist_ok=True)
    return dir_experiment


def consistent_ending(fn: str, ending: str = ".pkl", suffix: str = "") -> str:
    path_fn = Path(fn)
    return str(path_fn.parent / path_fn.stem) + ("_" if suffix else "") + suffix + ending


def consistent_endings(args: list) -> list[str]:
    return [consistent_ending(arg) if isinstance(arg, str) else consistent_ending(*arg) for arg in args]
```


## NLP / Text Processing

### Which projects overlap

- [P72](https://github.com/nhsengland/nlp_renal_biopsy)
- [P71](https://github.com/nhsengland/priv-lm-health-extended)
- [P51](https://github.com/nhsengland/priv-lm-health)
- [P33](https://github.com/nhsx/ELM4PSIR)
- [P23](https://github.com/nhsx/stm-survey-text)
- [P43](https://github.com/nhsengland/P43_LTHMedCat)

### What the overlap is

Clinical text projects repeatedly clean notes, normalize language, and build reusable preprocessing/tokenization flows.

### Snippet inventory

| ID | File | Source projects | Reuse candidate | Suggested module |
|---|---|---|---|---|
| NLP-001 | [prepare_notes_for_lm.py](./code-snippets/nlp-text-processing/prepare_notes_for_lm.py) | P33 | ✅ | `nhs_reuse.nlp.cleaning` |
| NLP-002 | [clean_text_pipeline.R](./code-snippets/nlp-text-processing/clean_text_pipeline.R) | P23 | ✅ | `nhs_reuse.nlp.r_text` |

### Raw snippets

#### NLP-001 — Prepare notes for language modelling

File: [`code-snippets/nlp-text-processing/prepare_notes_for_lm.py`](./code-snippets/nlp-text-processing/prepare_notes_for_lm.py)

```python
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
```

#### NLP-002 — R text cleaning pipeline

File: [`code-snippets/nlp-text-processing/clean_text_pipeline.R`](./code-snippets/nlp-text-processing/clean_text_pipeline.R)

```r
# Source: P23 STM for survey text — https://github.com/nhsx/stm-survey-text (R/main/functions.R)

prep_dataframe <- function(df, filter_sent = FALSE){
  df <- na.omit(df)
  if (filter_sent == TRUE){
    df <- df[(df$sentiment > 0.05) | (df$sentiment < -0.05),]
  }
  return(df)
}

clean_text <- function(data, StopWords, mintermfreq=2, lemma = TRUE, ngram = FALSE){
  t1 <- corpus(data$Response)
  docvars(t1, "doc_id") <- data$row_index
  docvars(t1) <- data

  t1 <- t1 %>% tolower()%>% textclean::replace_contraction()
  t2 <- gsub("[^[:alnum:][:space:]]","", t1)
  t2 <- gsub("[0-9]+", " ", t2)

  t4 <- quanteda::tokens(t2)
  if(ngram == TRUE){
    t4 <- tokens_ngrams(t4, n = c(1,2), concatenator = " ")
  }

  token <- tokens_remove(t4, pattern = StopWords)
  docfm <- dfm_trim(dfm(token), min_termfreq = mintermfreq)
  list("Tokens" = token, "DocMatrix" = docfm)
}
```


## Multimodal

### Which projects overlap

- [P22](https://github.com/nhsx/txt-ray-align)
- [P31](https://github.com/nhsx/txt-ray-align)
- [P61](https://github.com/nhsengland/mm-healthfair)
- [P81](https://github.com/nhsengland/mm-healthfair)

### What the overlap is

Multimodal projects share dataset wrappers and modality feature handling for text/image/time-series pipelines.

### Snippet inventory

| ID | File | Source projects | Reuse candidate | Suggested module |
|---|---|---|---|---|
| MM-001 | [embedding_dataset_wrappers.py](./code-snippets/multimodal/embedding_dataset_wrappers.py) | P22, P31 | ✅ | `nhs_reuse.multimodal.datasets` |
| MM-002 | [feature_name_mapping.py](./code-snippets/multimodal/feature_name_mapping.py) | P61, P81 | ✅ | `nhs_reuse.multimodal.features` |

### Raw snippets

#### MM-001 — Embedding dataset wrappers

File: [`code-snippets/multimodal/embedding_dataset_wrappers.py`](./code-snippets/multimodal/embedding_dataset_wrappers.py)

```python
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
```

#### MM-002 — Feature name mapping by modality

File: [`code-snippets/multimodal/feature_name_mapping.py`](./code-snippets/multimodal/feature_name_mapping.py)

```python
"""Source: P61/P81 MM-HealthFair — https://github.com/nhsengland/mm-healthfair (src/utils/shap_utils.py)"""


def get_feature_names(test_set, modalities):
    fn_map = {}
    for modality_type in modalities:
        if modality_type == "static":
            fn_map["static"] = test_set.get_feature_list()
        elif modality_type == "timeseries":
            fn_map["ts-vitals"] = test_set.get_feature_list("dynamic0")
            fn_map["ts-labs"] = test_set.get_feature_list("dynamic1")
    return fn_map
```


## Evaluation

### Which projects overlap

- [P82](https://github.com/nhsengland/evalsense)
- [P71](https://github.com/nhsengland/priv-lm-health-extended)

### What the overlap is

Evaluation code overlaps in metric calculators and summary helpers for text and retrieval quality assessment.

### Snippet inventory

| ID | File | Source projects | Reuse candidate | Suggested module |
|---|---|---|---|---|
| EVAL-001 | [bleu_precision_evaluator.py](./code-snippets/evaluation/bleu_precision_evaluator.py) | P82 | ✅ | `nhs_reuse.evaluation.bleu` |
| EVAL-002 | [retrieval_metrics.py](./code-snippets/evaluation/retrieval_metrics.py) | P22, P31 | ✅ | `nhs_reuse.evaluation.retrieval` |

### Raw snippets

#### EVAL-001 — BLEU precision evaluator

File: [`code-snippets/evaluation/bleu_precision_evaluator.py`](./code-snippets/evaluation/bleu_precision_evaluator.py)

```python
"""Source: P82 EvalSense — https://github.com/nhsengland/evalsense (evaluation/evaluators/bleu.py)"""

import evaluate


class BleuPrecisionScoreCalculator:
    def __init__(self):
        self.bleu_module = evaluate.load("bleu")

    def calculate(self, prediction: str, reference: str):
        if reference is None:
            raise ValueError("Reference is required for computing BLEU precision.")

        result = self.bleu_module.compute(
            predictions=[prediction],
            references=[reference],
        )
        return {
            "value": result["precisions"][0],
            "prediction": prediction,
            "reference": reference,
        }
```

#### EVAL-002 — Retrieval metrics summarizer

File: [`code-snippets/evaluation/retrieval_metrics.py`](./code-snippets/evaluation/retrieval_metrics.py)

```python
"""Source: P22/P31 Txt-Ray Align — https://github.com/nhsx/txt-ray-align (evaluate.py)"""


def summarize_retrieval_metrics(precisions, recalls, flat_hits, total):
    avg_precision = sum(precisions) / len(precisions)
    avg_recall = sum(recalls) / len(recalls)
    f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)

    return {
        "Flat hit": flat_hits / total,
        "hits": flat_hits,
        "Precision": avg_precision,
        "Recall": avg_recall,
        "F1": f1,
    }
```


## Explainability

### Which projects overlap

- [P14](https://github.com/nhsx/commercial-data-healthcare-predictions)
- [P24](https://github.com/nhsx/LIME-XAI-Facial-Disease-Classification)
- [P61](https://github.com/nhsengland/mm-healthfair)
- [P81](https://github.com/nhsengland/mm-healthfair)

### What the overlap is

Explainability and fairness work repeats grouped feature attribution and confidence interval estimation patterns.

### Snippet inventory

| ID | File | Source projects | Reuse candidate | Suggested module |
|---|---|---|---|---|
| XAI-001 | [fairness_bootstrap_ci.py](./code-snippets/explainability/fairness_bootstrap_ci.py) | P61, P81 | ✅ | `nhs_reuse.xai.fairness` |
| XAI-002 | [mcr_feature_grouping.py](./code-snippets/explainability/mcr_feature_grouping.py) | P14 | ✅ | `nhs_reuse.xai.mcr` |

### Raw snippets

#### XAI-001 — Fairness bootstrap confidence intervals

File: [`code-snippets/explainability/fairness_bootstrap_ci.py`](./code-snippets/explainability/fairness_bootstrap_ci.py)

```python
"""Source: P61/P81 MM-HealthFair — https://github.com/nhsengland/mm-healthfair (src/utils/fairness_utils.py)"""

import numpy as np
from scipy.stats import norm


def bias_corrected_ci(bootstrap_samples, observed_value):
    sorted_samples = np.sort(bootstrap_samples)
    z0 = norm.ppf((np.sum(sorted_samples < observed_value) + 0.5) / len(sorted_samples))

    jackknife_estimates = [np.mean(np.delete(sorted_samples, i)) for i in range(len(sorted_samples))]
    mean_jackknife = np.mean(jackknife_estimates)
    a = np.sum((mean_jackknife - jackknife_estimates) ** 3) / (
        6 * (np.sum((mean_jackknife - jackknife_estimates) ** 2) ** 1.5)
    )

    alpha = [0.025, 0.975]
    adjusted_percentiles = norm.cdf(z0 + (z0 + norm.ppf(alpha)) / (1 - a * (z0 + norm.ppf(alpha))))

    if np.isnan(adjusted_percentiles[0]):
        adjusted_percentiles = alpha

    lower = np.percentile(sorted_samples, adjusted_percentiles[0] * 100)
    upper = np.percentile(sorted_samples, adjusted_percentiles[1] * 100)
    return lower, upper
```

#### XAI-002 — MCR feature grouping

File: [`code-snippets/explainability/mcr_feature_grouping.py`](./code-snippets/explainability/mcr_feature_grouping.py)

```python
"""Source: P14 Model Class Reliance project — https://github.com/nhsx/commercial-data-healthcare-predictions (MCR_for_op_rf.py)"""

import numpy as np


def build_group_index_map(feature_names, grouping_names, grouped_features):
    grouping_names2indexes = {}
    for i, group_name in enumerate(grouping_names):
        grouping_names2indexes[group_name] = np.asarray(
            [feature_names.index(v) for v in grouped_features[i]]
        )
    return grouping_names2indexes
```


## Graph / Hypergraph

### Which projects overlap

- [P34](https://github.com/nhsx/hypergraph-mm)
- [P32](https://github.com/nhsx/ESNEFT_diabetes_StephenRicher)

### What the overlap is

Graph-centric analysis includes repeated numerical kernels for overlap and centrality in disease network structures.

### Snippet inventory

| ID | File | Source projects | Reuse candidate | Suggested module |
|---|---|---|---|---|
| GRAPH-001 | [degree_centrality.py](./code-snippets/graph-hypergraph/degree_centrality.py) | P34 | ✅ | `nhs_reuse.graph.centrality` |
| GRAPH-002 | [overlap_coefficient.py](./code-snippets/graph-hypergraph/overlap_coefficient.py) | P34 | ✅ | `nhs_reuse.graph.overlap` |

### Raw snippets

#### GRAPH-001 — Hypergraph degree centrality kernel

File: [`code-snippets/graph-hypergraph/degree_centrality.py`](./code-snippets/graph-hypergraph/degree_centrality.py)

```python
"""Source: P34 Hypergraph-MM — https://github.com/nhsx/hypergraph-mm (hypmm/centrality_utils.py)"""

import numba
import numpy as np


@numba.njit(fastmath=True, nogil=True)
def degree_centrality(inc_mat_tail, inc_mat_head, edge_weights):
    n_diseases, n_edges = inc_mat_tail.shape
    node_degree_tail = np.zeros(n_diseases, dtype=np.float64)
    node_degree_head = np.zeros(n_diseases, dtype=np.float64)

    for i in range(n_diseases):
        for j in range(n_edges):
            node_degree_tail[i] += inc_mat_tail[i, j] * edge_weights[j]
            node_degree_head[i] += inc_mat_head[i, j] * edge_weights[j]

    edge_degree_tail = np.zeros(n_edges, dtype=np.float64)
    edge_degree_head = np.zeros(n_edges, dtype=np.float64)
    for j in range(n_edges):
        for i in range(n_diseases):
            edge_degree_tail[j] += inc_mat_tail[i, j]
            edge_degree_head[j] += inc_mat_head[i, j]

    return (node_degree_tail, node_degree_head), (edge_degree_tail, edge_degree_head)
```

#### GRAPH-002 — Hypergraph overlap coefficient

File: [`code-snippets/graph-hypergraph/overlap_coefficient.py`](./code-snippets/graph-hypergraph/overlap_coefficient.py)

```python
"""Source: P34 Hypergraph-MM — https://github.com/nhsx/hypergraph-mm (hypmm/weight_functions.py)"""

import numba
import numpy as np


@numba.njit(fastmath=True, nogil=True)
def comp_overlap_coeff(prev_arr, inds, denom_arr):
    n_diseases = inds.shape[0]
    inds = inds.astype(np.int64)

    bin_int = 0
    for i in range(n_diseases):
        bin_int += 2 ** inds[i]

    numerator = prev_arr[bin_int]

    denominator = denom_arr[inds[0]]
    for i in range(1, n_diseases):
        new_denom = denom_arr[inds[i]]
        if new_denom < denominator:
            denominator = new_denom

    return numerator / denominator, denominator
```


## Data Pipelines

### Which projects overlap

- [P33](https://github.com/nhsx/ELM4PSIR)
- [P72](https://github.com/nhsengland/nlp_renal_biopsy)
- [P52](https://github.com/nhsengland/ProcessMining)
- [P32](https://github.com/nhsx/ESNEFT_diabetes_StephenRicher)
- [P51](https://github.com/nhsengland/priv-lm-health)
- [P71](https://github.com/nhsengland/priv-lm-health-extended)

### What the overlap is

Data engineering code regularly recreates split generation, path setup, and model input preparation helpers.

### Snippet inventory

| ID | File | Source projects | Reuse candidate | Suggested module |
|---|---|---|---|---|
| DP-001 | [create_holdout_split.py](./code-snippets/data-pipelines/create_holdout_split.py) | P33 | ✅ | `nhs_reuse.pipelines.splits` |
| DP-002 | [setup_input_json.py](./code-snippets/data-pipelines/setup_input_json.py) | P72 | ✅ | `nhs_reuse.pipelines.inputs` |

### Raw snippets

#### DP-001 — Create holdout data split

File: [`code-snippets/data-pipelines/create_holdout_split.py`](./code-snippets/data-pipelines/create_holdout_split.py)

```python
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
```

#### DP-002 — Setup model input JSON

File: [`code-snippets/data-pipelines/setup_input_json.py`](./code-snippets/data-pipelines/setup_input_json.py)

```python
"""Source: P72 NER renal biopsy — https://github.com/nhsengland/nlp_renal_biopsy (setup_input_json.py)"""

from pathlib import Path

from src.preprocessing.guidelines import EntityGuidelines
from src.renal_biopsy.preprocessor import RenalBiopsyProcessor


def setup_input_json(guidelines_file: str, raw_data_file: str):
    root_dir = Path("src/renal_biopsy")
    required_files = {
        "guidelines": root_dir / "data" / guidelines_file,
        "raw_data": root_dir / "data" / raw_data_file,
    }

    eg = EntityGuidelines(required_files["guidelines"])
    processor = RenalBiopsyProcessor(guidelines=eg)
    processor.create_input_json(
        data_path=required_files["raw_data"],
        save_path=root_dir / "data/real_input.json",
        full=True,
    )
```

## Cross-Project Overlap Map

| Project | Synthetic | NLP | Multimodal | Graph | Eval | Explainability | Pipelines | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P82 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| P81 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 2 |
| P72 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| P71 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| P62 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| P61 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 2 |
| P52 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| P51 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| P43 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| P41 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| P34 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| P33 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 |
| P32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| P31 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 2 |
| P24 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| P23 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| P22 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 2 |
| P21 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| P14 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| P12 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| P11 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total snippets** | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 14 |

## Reuse Candidates Summary

| ID | Title | Theme | Source projects | Suggested module | File |
|---|---|---|---|---|---|
| SD-001 | Synthetic data distribution metrics | Synthetic Data | P12, P21 | `nhs_reuse.synthetic.metrics` | [distribution_metrics.py](./code-snippets/synthetic-data/distribution_metrics.py) |
| SD-002 | Experiment I/O helpers | Synthetic Data | P41 | `nhs_reuse.common.io` | [experiment_io_helpers.py](./code-snippets/synthetic-data/experiment_io_helpers.py) |
| NLP-001 | Prepare notes for language modelling | NLP / Text Processing | P33 | `nhs_reuse.nlp.cleaning` | [prepare_notes_for_lm.py](./code-snippets/nlp-text-processing/prepare_notes_for_lm.py) |
| NLP-002 | R text cleaning pipeline | NLP / Text Processing | P23 | `nhs_reuse.nlp.r_text` | [clean_text_pipeline.R](./code-snippets/nlp-text-processing/clean_text_pipeline.R) |
| MM-001 | Embedding dataset wrappers | Multimodal | P22, P31 | `nhs_reuse.multimodal.datasets` | [embedding_dataset_wrappers.py](./code-snippets/multimodal/embedding_dataset_wrappers.py) |
| MM-002 | Feature name mapping by modality | Multimodal | P61, P81 | `nhs_reuse.multimodal.features` | [feature_name_mapping.py](./code-snippets/multimodal/feature_name_mapping.py) |
| EVAL-001 | BLEU precision evaluator | Evaluation | P82 | `nhs_reuse.evaluation.bleu` | [bleu_precision_evaluator.py](./code-snippets/evaluation/bleu_precision_evaluator.py) |
| EVAL-002 | Retrieval metrics summarizer | Evaluation | P22, P31 | `nhs_reuse.evaluation.retrieval` | [retrieval_metrics.py](./code-snippets/evaluation/retrieval_metrics.py) |
| XAI-001 | Fairness bootstrap confidence intervals | Explainability | P61, P81 | `nhs_reuse.xai.fairness` | [fairness_bootstrap_ci.py](./code-snippets/explainability/fairness_bootstrap_ci.py) |
| XAI-002 | MCR feature grouping | Explainability | P14 | `nhs_reuse.xai.mcr` | [mcr_feature_grouping.py](./code-snippets/explainability/mcr_feature_grouping.py) |
| GRAPH-001 | Hypergraph degree centrality kernel | Graph / Hypergraph | P34 | `nhs_reuse.graph.centrality` | [degree_centrality.py](./code-snippets/graph-hypergraph/degree_centrality.py) |
| GRAPH-002 | Hypergraph overlap coefficient | Graph / Hypergraph | P34 | `nhs_reuse.graph.overlap` | [overlap_coefficient.py](./code-snippets/graph-hypergraph/overlap_coefficient.py) |
| DP-001 | Create holdout data split | Data Pipelines | P33 | `nhs_reuse.pipelines.splits` | [create_holdout_split.py](./code-snippets/data-pipelines/create_holdout_split.py) |
| DP-002 | Setup model input JSON | Data Pipelines | P72 | `nhs_reuse.pipelines.inputs` | [setup_input_json.py](./code-snippets/data-pipelines/setup_input_json.py) |
