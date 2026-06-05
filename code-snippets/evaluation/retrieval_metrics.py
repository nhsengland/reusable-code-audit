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
