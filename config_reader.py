import yaml
from pathlib import Path


class ConfigReader:
    _config_content = {}

    @property
    def amadeus_cred(self):
        return self._get_config_content()['flights_api_cred']

    @property
    def prompt_classification(self):
        return self._get_config_content()['prompt_classification_topics']


    def _get_config_content(self):
        if not ConfigReader._config_content:
            congif_path = Path(__file__).parent / "config" / "config.yaml"
            with congif_path.open() as f:
                ConfigReader._config_content = yaml.load(f, Loader=yaml.Loader)
        return ConfigReader._config_content