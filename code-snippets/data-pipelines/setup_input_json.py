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
