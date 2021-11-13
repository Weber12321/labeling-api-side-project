from enum import Enum
from pathlib import Path

from definition import RULE_FOLDER


INPUT_TABLE = "predicting_jobs_predictingresult"
INPUT_COLUMNS = "source_author, applied_content, created_at"


class ModelType(Enum):
    KEYWORD_MODEL = "keyword_model"
    RULE_MODEL = "rule_model"

class PredictTarget(Enum):
    AUTHOR_NAME = "author_name"
    CONTENT = "content"
    S_AREA_ID = "s_area_id"

class RulesTarget:
    AUTHOR_NAME_KEYWORD = Path(RULE_FOLDER / "author_name.pkl")

class KeywordMatchType:
    PARTIALLY = "partially"
    ABSOLUTELY = "absolutely"
    START = "start"
    END = "end"

class Errors(Enum):
    UNKNOWN_DB_TYPE = "Unknown database type."
    UNKNOWN_PREDICT_TARGET_TYPE = "Unknown predict target type."


class QueryStatements(Enum):
    # QUERY_FEMALE = f'SELECT {INPUT_COLUMNS} FROM {INPUT_TABLE} WHERE label_name LIKE "女%" AND applied_feature="author"'
    # QUERY_MALE = f'SELECT {INPUT_COLUMNS} FROM {INPUT_TABLE} WHERE label_name LIKE "男%" AND applied_feature="author"'
    # MALE_RULE = f'SELECT * FROM male_author_name_rules'
    # FEMALE_RULE = f'SELECT * FROM female_author_name_rules'
    QUERY = f'SELECT * FROM {INPUT_TABLE} WHERE applied_feature="author"'

class SampleResulTable(str, Enum):
    blog = 'wh_panel_mapping_blog'
    Comment = 'wh_panel_mapping_Comment'
    Dcard = 'wh_panel_mapping_Dcard'
    fbfans = 'wh_panel_mapping_fbfans'
    fbgroup = 'wh_panel_mapping_fbgroup'
    fbkol = 'wh_panel_mapping_fbkol'
    fbpm = 'wh_panel_mapping_fbpm'
    fbprivategroup = 'wh_panel_mapping_fbprivategroup'
    forum = 'wh_panel_mapping_forum'
    Instagram = 'wh_panel_mapping_Instagram'
    news = 'wh_panel_mapping_news'
    plurk = 'wh_panel_mapping_plurk'
    Ptt = 'wh_panel_mapping_Ptt'
    Tiktok = 'wh_panel_mapping_Tiktok'
    Twitter = 'wh_panel_mapping_Twitter'
    video = 'wh_panel_mapping_video'
    Youtube = 'wh_panel_mapping_Youtube'




