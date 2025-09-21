from tabulate import tabulate
from deep_translator import GoogleTranslator

# Optional: map a few common names to ISO codes
LANG_ALIASES = {
    "english": "en", "en": "en",
    "hindi": "hi", "hi": "hi",
    "spanish": "es", "es": "es",
    "french": "fr", "fr": "fr",
    "german": "de", "de": "de",
    "chinese": "zh-CN", "zh": "zh-CN",
    "japanese": "ja", "ja": "ja",
    "korean": "ko", "ko": "ko",
    "arabic": "ar", "ar": "ar",
}

class TranslateView:
    def __init__(self, text: str, dest_lang: str = "hi"):
        self.text = text
        # normalize language input (accepts 'hi' or 'hindi')
        self.dest_lang = LANG_ALIASES.get(dest_lang.strip().lower(), dest_lang)

    def __str__(self):
        try:
            translated = GoogleTranslator(source="auto", target=self.dest_lang).translate(self.text)
        except Exception as e:
            translated = f"[Translation failed: {e}]"

        data = [
            ["Language", "Sentence"],
            ["English (auto)", self.text],
            [self.dest_lang, translated],
        ]
        return tabulate(data, headers="firstrow", tablefmt="grid")

if __name__ == "__main__":
    sentence = input("Enter Sentence: ")
    lang_input = input("Enter target language (code or name, e.g. 'hi' or 'hindi'): ").strip() or "hi"
    print(TranslateView(sentence, lang_input))
