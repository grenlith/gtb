import yaml
from typing import List, Tuple 

class Collector:
    def __init__(self) -> None:
        self.collector_type: str = ""
        self.handle: str = ""
        self.author: str = ""
        self.post_limit: int = 10


class Options:
    def __init__(self) -> None:
        self.log_level: str = "INFO"
        self.timezone: str = "Etc/UTC"


def load(config_file: str = 'config.yml') -> Tuple[Options, List[Collector]]:
    with open(config_file, 'r') as file:
        config_data: List[Collector] = []
        opts = Options()
        yaml_generator = yaml.safe_load_all(file)
        for document in yaml_generator:
            if "options" in document:
                if "log_level" in document["options"]:
                    opts.log_level = document["options"]["log_level"]
                if "timezone" in document["options"]:
                    opts.timezone = document["options"]["timezone"]
            elif "collector" in document:
                cfg = Collector()
                cfg.collector_type = document["collector"]["collector_type"]
                cfg.handle = document["collector"]["handle"]
                cfg.post_limit = document["collector"]["post_limit"]
                config_data.append(cfg)
        return opts, config_data
