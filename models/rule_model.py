import re
from typing import Iterable, Dict, List


from models.audience_models import AudienceModel
from utils.input_example import InputExample

from utils.selections import ModelType, PredictTarget, Errors


class RuleModel(AudienceModel):
    def __init__(self, model_data: Dict[str, List[str]] = None,
                 name: str = None,
                 model_type: ModelType = ModelType.RULE_MODEL,
                 target: PredictTarget = PredictTarget.CONTENT,
                 verbose: bool = False):
        super().__init__(name=name if name is not None else "RuleModel", model_type=model_type, target=target,
                         logger_name="RuleModel", verbose=verbose)
        self.logger.debug("model Init")
        self.label_patterns = None
        self.labels = []
        if model_data is not None:
            self.load(model_data)

    def load(self, label_patterns: Dict[str, List[str]] = None):
        self.label_patterns = label_patterns
        self.labels = [label for label in self.label_patterns.keys()]
        self.logger.debug(f"labels size: {len(self.labels)}")

    def predict(self, input_examples: Iterable[InputExample],
                target=None):
        target = target if target is not None else self.target
        x = parse_predict_target(input_examples=input_examples, target=target,
                                 case_sensitive=self.case_sensitive)
        matched_labels = []
        match_count_list = []
        for _predict_str in x:
            _match_count_list = []
            _matched_labels = []
            for label, patterns in self.label_patterns.items():
                _matched_count = 0

                for pattern in patterns:
                    if re.search(pattern=pattern, string=_predict_str.lower()):
                        _matched_count += 1


                if _matched_count > 0:
                    _match_count_list.append((label, _matched_count))
                    _matched_labels.append(label)

            if len(_matched_labels) > 0:
                matched_labels.append(tuple(_matched_labels))
                match_count_list.append(_match_count_list)

        self.logger.debug(f"Matched labels size: {len(matched_labels)}")
        self.logger.debug(f"Matched count list size: {len(match_count_list)}")
        if len(matched_labels) > 0:
            return matched_labels, match_count_list
        else:
            return None, None

def parse_predict_target(input_examples: Iterable[InputExample], target: PredictTarget = PredictTarget.CONTENT,
                         case_sensitive: bool = False) -> List[str]:
    return [_parse_predict_target(input_example, target=target, case_sensitive=case_sensitive)
            for input_example in input_examples]

def _parse_predict_target(input_example: InputExample, target: PredictTarget = PredictTarget.CONTENT,
                          case_sensitive: bool = False) -> str:
    if target == PredictTarget.CONTENT:
        return input_example.content if case_sensitive else input_example.content.lower()
    elif target == PredictTarget.AUTHOR_NAME:
        return input_example.author if case_sensitive else input_example.author.lower()
    elif target == PredictTarget.S_AREA_ID:
        return input_example.s_area_id if case_sensitive else input_example.s_area_id.lower()
    else:
        raise ValueError(Errors.UNKNOWN_PREDICT_TARGET_TYPE)
