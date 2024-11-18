import time
import yaml
from pathlib import Path


SCHEME_UPDATE_DURATION = 60 * 5  # schema刷新周期


class Dict2Object:
    """字典转对象"""

    def __init__(self, dictionary: dict):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, Dict2Object(value))
            else:
                setattr(self, key, value)

    def __getattr__(self, __name: str):
        if __name in self.__dict__:
            return self.__dict__[__name]
        return None


class SchemaLoader:
    """配置加载器"""

    def __init__(self, service_file):
        self.status = None
        self.corpus = None
        self.chat_models = None
        self.multi_modal_models = None
        self.embeddings = None
        self.vector_store = None
        self.storage = None
        self.prompts = None
        self.config_data_id = Path(service_file).stem
        self.load_time = 0

    def __getattribute__(self, __name: str):
        last_load_time = super().__getattribute__("load_time")
        if time.time() - last_load_time > SCHEME_UPDATE_DURATION:
            setattr(self, "load_time", time.time())
            config_data_id = super().__getattribute__("config_data_id")
            config_file = f"configs/{config_data_id}.yaml"
            with open(config_file, "r", encoding="utf-8") as file:
                config: dict = yaml.safe_load(file)
            for key, value in config.items():
                if isinstance(value, dict):
                    setattr(self, key, Dict2Object(value))
                else:
                    setattr(self, key, value)
        return super().__getattribute__(__name)
