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
