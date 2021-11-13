from collections import defaultdict
from typing import Iterable, Dict, List, Tuple

from ahocorapy.keywordtree import KeywordTree

from models.audience_models import AudienceModel
from utils.input_example import InputExample
from utils.selections import ModelType, PredictTarget, KeywordMatchType, Errors


class KeywordModel(AudienceModel):
    def __init__(self, label_keywords: Dict[str, List[Tuple[str, KeywordMatchType]]] = None,
                 name: str = None,
                 model_type: ModelType = ModelType.KEYWORD_MODEL.value,
                 case_sensitive: bool = False,
                 target=PredictTarget.CONTENT.value,
                 verbose: bool = False):
        super().__init__(name=name if name is not None else "KeywordModel", model_type=model_type,
                         case_sensitive=case_sensitive, target=target, logger_name="KeywordModel", verbose=verbose)
        self.logger.debug("model Init")
        self.label_match_any_trees = dict()
        self.label_match_start = defaultdict(list)
        self.label_match_end = defaultdict(list)
        self.label_match_full = defaultdict(list)
        self.labels = []
        if label_keywords is not None:
            self.load(label_keywords)

    def load(self, label_keywords: Dict[str, List[Tuple[str, KeywordMatchType]]]):
        for label, keywords in label_keywords.items():
            if label not in self.labels:
                self.labels.append(label)
            self.label_match_any_trees[label] = KeywordTree(case_insensitive=(not self.case_sensitive))
            for keyword, match_types in keywords:
                if isinstance(match_types, KeywordMatchType):
                    match_types = [match_types]
                _keyword = keyword if self.case_sensitive else keyword.lower()
                if KeywordMatchType.PARTIALLY in match_types:
                    self.label_match_any_trees[label].add(_keyword)
                if KeywordMatchType.START in match_types:
                    self.label_match_start[label].append(_keyword)
                if KeywordMatchType.END in match_types:
                    self.label_match_end[label].append(_keyword)
                if KeywordMatchType.ABSOLUTELY in match_types:
                    self.label_match_full[label].append(_keyword)
            self.label_match_any_trees[label].finalize()
        self.logger.debug(f"label match any trees: {len(self.label_match_any_trees)}")
        self.logger.debug(f"label match start: {len(self.label_match_start)}")
        self.logger.debug(f"label match end: {len(self.label_match_end)}")
        self.logger.debug(f"label match full: {len(self.label_match_full)}")

    def predict(self, input_examples: Iterable[InputExample],
                target: PredictTarget = None):
        target = target if target is not None else self.target
        x = parse_predict_target(input_examples=input_examples, target=target,
                                 case_sensitive=self.case_sensitive)
        matched_labels = []
        match_count_list = []
        for _predict_str in x:
            _match_count_list = []
            _matched_labels = []
            for label in self.labels:
                _matched_count = 0

                # start matching rules
                if self.label_match_any_trees[label].search(_predict_str.lower()):
                    # matched_result[label].append(1)
                    _matched_count += 1
                    # break
                for keyword in self.label_match_full[label]:
                    if keyword == _predict_str:
                        # matched_result[label].append(1)
                        _matched_count += 1
                        # break
                for keyword in self.label_match_start[label]:
                    if _predict_str.startswith(keyword):
                        # matched_result[label].append(1)
                        _matched_count += 1
                        # break

                for keyword in self.label_match_end[label]:
                    if _predict_str.endswith(keyword):
                        # matched_result[label].append(1)
                        _matched_count += 1
                        # break
                if _matched_count > 0:
                    _match_count_list.append((label, _matched_count))
                    _matched_labels.append(label)
            if len(_matched_labels) > 0:
                matched_labels.append(tuple(_matched_labels))
                match_count_list.append(_match_count_list)

        self.logger.debug(f"Matched labels size: {len(matched_labels)}")
        self.logger.debug(f"Matched count list size: {len(match_count_list)}")
        if matched_labels:
            return matched_labels, match_count_list
        else:
            return None, None

def parse_predict_target(input_examples: Iterable[InputExample], target: PredictTarget = PredictTarget.CONTENT.value,
                         case_sensitive: bool = False) -> List[str]:
    return [_parse_predict_target(input_example, target=target, case_sensitive=case_sensitive)
            for input_example in input_examples]

def _parse_predict_target(input_example: InputExample, target: PredictTarget = PredictTarget.CONTENT.value,
                          case_sensitive: bool = False) -> str:
    if target == PredictTarget.CONTENT.value:
        return input_example.content if case_sensitive else input_example.content.lower()
    elif target == PredictTarget.AUTHOR_NAME.value:
        return input_example.author if case_sensitive else input_example.author.lower()
    elif target == PredictTarget.S_AREA_ID.value:
        return input_example.s_area_id if case_sensitive else input_example.s_area_id.lower()
    else:
        raise ValueError(Errors.UNKNOWN_PREDICT_TARGET_TYPE.value)
