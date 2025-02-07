"""
Neural machine translation starter.
"""
# pylint: disable= too-many-locals
import json
from pathlib import Path
from random import randint

from config.constants import PROJECT_ROOT
from core_utils.llm.metrics import Metrics
from core_utils.llm.time_decorator import report_time
from lab_8_llm.main import (LLMPipeline, RawDataImporter, RawDataPreprocessor, TaskDataset,
                            TaskEvaluator)


@report_time
def main() -> None:
    """
    Run the translation pipeline.
    """
    result = None

    with open(PROJECT_ROOT / "lab_8_llm" / "settings.json", "r", encoding="utf-8") as settings_json:
        settings = json.load(settings_json)

    raw_data = RawDataImporter(settings["parameters"]["dataset"])
    raw_data.obtain()

    preprocessed_data = RawDataPreprocessor(raw_data.raw_data)
    print(preprocessed_data.analyze())

    preprocessed_data.transform()

    dataset = TaskDataset(preprocessed_data.data.head(100))

    llm = LLMPipeline(settings["parameters"]["model"], dataset, 120, 64, "cpu")

    print(llm.analyze_model())

    sample = dataset.data['question'][randint(0, len(dataset) - 1)]
    sample_infer = llm.infer_sample(sample)
    print('prediction for sample (', sample, ')', sample_infer[len(sample):])

    predictions = llm.infer_dataset()
    predictions_path = PROJECT_ROOT / 'lab_8_llm' / 'dist' / 'predictions.csv'

    if not predictions_path.parent.exists():
        predictions_path.parent.mkdir()

    predictions.to_csv(predictions_path, index=False)

    evaluator = TaskEvaluator(
        Path(predictions_path),
        Metrics
    )

    result = evaluator.run()

    print(result)

    assert result is not None, "Demo does not work correctly"


if __name__ == "__main__":
    main()
