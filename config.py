from typing import Dict, Any
from aqt import mw


class AddonConfig:
    """The AddonConfig object loads the user configurations.

    Attributes
    ----------
    language : str
        Language for the translations. One of `English`, `German`, `Russian`, `Spanish`, `Swedish`, `French`, `Dutch`,
        `Hungarian`, `Slovenian`, `Japanese`
    api_config : Dict[str, str]
        URLs to the JOTOBA instance.
    """

    def __init__(self) -> None:
        self.config = mw.addonManager.getConfig(__name__)
        self._initialize_default_values()

    def refresh(self) -> None:
        """Refreshes this object with the data in the config.
        """

        if self.config is None:
            return None

        self._refresh_api_config()
        self._refresh_language()

    # Initialize this object's attributes to their default values
    def _initialize_default_values(self) -> None:
        self.language: str = "English"
        self.api_config: Dict[str, str] = {
            "JOTOBA_URL": "https://jotoba.de",
            "WORDS_Suffix": "/api/search/words",
            "SENTENCE_Suffix": "/api/search/sentences",
        }

        self.config: Dict[str, Any] = mw.addonManager.getConfig(__name__)

    # Load the api config
    def _refresh_api_config(self) -> None:
        if "API Config" not in self.config:
            return None

        for setting, value in self.config["API Config"].items():
            if setting in self.api_config:
                self.api_config[setting] = value

    # Load the language
    def _refresh_language(self) -> None:
        if "Language" not in self.config:
            return None

        if self.config["Language"] not in ["English", "German", "Russian", "Spanish", "Swedish", "French", "Dutch",
                                           "Hungarian", "Slovenian", "Japanese"]:
            return None

        self.language = self.config["Language"]
