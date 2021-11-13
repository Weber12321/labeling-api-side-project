from datetime import datetime
from unittest import TestCase

from models.rule_model import RuleModel
from models.keyword_model import KeywordModel
from utils.selections import PredictTarget, KeywordMatchType

from utils.input_example import InputExample

post_male = "小弟我沒女友，在八卦版混了很久了在八卦版混，時常會有的福利就是偶爾會有人貼清涼養眼圖上班上久了，心情煩悶，看這些圖多多少少會有解鬱消悶的效果感謝八卦版大的貢獻所以在八卦版上，只要看到巨乳等關鍵字，我都是會直覺地點閱進入觀賞，以調劑身心。"
post_female = "小妹的朋友上週領薪水這週就跟我哭哭說全身上下剩一千五明明是她自己限制自己一個月只能花幾千塊其他買保險跟存起來這樣有什麼好哭哭的就是自己強迫自己啊而且明明就是存起來哪是沒錢啊不懂欸"
post_female_2 = "小妹我男朋友上週領薪水這週就跟我哭哭說全身上下剩一千五明明是她自己限制自己一個月只能花幾千塊其他買保險跟存起來這樣有什麼好哭哭的就是自己強迫自己啊而且明明就是存起來哪是沒錢啊不懂欸"
post_young = "小弟我出社會工作不到兩年，今天辦了人生第一張信用卡...。"

input_female = InputExample(id_="1", s_area_id="ptt_woman_talk", author="Alice", title="", content=post_female,
                            post_time=datetime.now(), label="female")

input_young = InputExample(id_="1", s_area_id="1", author="Alice", title="", content=post_young,
                           post_time=datetime.now())


class TestRuleBaseModel(TestCase):
    content_rules = {"young": ["工作.{0,3}([一兩三]|[1-3])年"]}
    name_rules = {"female": ["alice"]}
    source_rules = {"female": ["ptt_woman_talk"]}

    def setUp(self) -> None:
        self.content_rule_base_model = RuleModel(self.content_rules)
        self.name_rule_base_model = RuleModel(self.name_rules)
        self.source_rule_base_model = RuleModel(self.source_rules)

    def test_predict_content(self):
        """
        預測內文規則
        """
        label = "young"
        rs, prob = self.content_rule_base_model.predict([input_young])
        self.assertTrue(label in rs[0])

    def test_predict_name(self):
        """
        預測作者名稱規則
        """
        label = "female"
        rs, prob = self.name_rule_base_model.predict([input_young], target=PredictTarget.AUTHOR_NAME)
        self.assertTrue(label in rs[0])

    def test_predict_source(self):
        """
        預測作者來源規則
        """
        label = "female"
        rs, prob = self.source_rule_base_model.predict([input_female], target=PredictTarget.S_AREA_ID)
        self.assertTrue(label in rs[0])

class TestKeyWordBaseModel(TestCase):
    source_rules = {"female": [("woman_talk", KeywordMatchType.END), ("_talk", KeywordMatchType.PARTIALLY)]}

    def setUp(self) -> None:
        self.source_rule_base_model = KeywordModel(self.source_rules)

    def test_predict_source(self):
        """
        預測作者來源規則
        """
        label = "female"
        rs, prob = self.source_rule_base_model.predict([input_female], target=PredictTarget.S_AREA_ID)
        self.assertTrue(label in rs[0])
