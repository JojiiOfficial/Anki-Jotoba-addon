# Configuration for Anki Jotoba Addon

- `Language` (String): Language of the translations retrieved from Jotoba. Must be one of: _English_, _German_, _Russian_, _Spanish_, _Swedish_, _French_, _Dutch_, _Hungarian_, _Slovenian_, _Japanese_. Default: "English"
- `Jotoba_URL` (String): URL to the Jotoba Instance. For more infos on how to set up your own Jotoba instance see [here](https://github.com/WeDontPanic/Jotoba/wiki/Selfhost). Default: "https://jotoba.de"
- `API_Words_Suffix` (String): Suffix relative to `Jotoba_URL` to the api responsible for word queries. Default: "/api/search/words"
- `API_Sentence_Suffix` (String): Suffix relative to `Jotoba_URL` to the api responsible for sentence queries. Default: "/api/search/sentences"