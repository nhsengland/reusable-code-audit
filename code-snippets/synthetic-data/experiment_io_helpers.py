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
