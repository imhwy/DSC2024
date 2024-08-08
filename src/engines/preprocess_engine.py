"""

"""

import re
import time
from underthesea import word_tokenize

from src.prompt.prompt_template import (prompt_injection_patterns,
                                        correct_vi_prompt,
                                        translate_en_prompt,
                                        translate_vi_en_prompt)


class PreprocessQuestion:
    """
    """

    def __init__(
        self,
        gemini,
        domain_clf_model,
        domain_clf_vectorizer,
        lang_detect_model,
        lang_detect_vectorizer
    ) -> None:
        """
        """
        self.gemini = gemini
        self.domain_clf_model = domain_clf_model
        self.domain_clf_vectorizer = domain_clf_vectorizer
        self.lang_detect_model = lang_detect_model
        self.lang_detect_vectorizer = lang_detect_vectorizer

    def tokenize_text(self, text):
        """
        Tokenizes the input text using underthesea.

        Args:
            text (str): The text to be tokenized.

        Returns:
            str: The tokenized text.
        """
        tokens = word_tokenize(text, format='text')
        return tokens

    def classify_domain(self, text):
        """
        Classifies the domain of the input text using a pre-trained SVM model.

        Args:
            text (str): The text to classify.

        Returns:
            int: The predicted domain label of the text.
        """
        # Preprocess the text
        processed_text = self.tokenize_text(text)

        # Convert to TF-IDF features
        text_tfidf = self.domain_clf_vectorizer.transform([processed_text])

        # Predict and measure time
        prediction = self.domain_clf_model.predict(text_tfidf)
        return prediction[0]

    def lang_detect(self, text):
        """
        Detects the language of the input text.

        Args:
            text (str): The text to analyze.

        Returns:
            str: The detected language code.
        """
        lang = "vi"  # or "en" or "vi_en" "no_tonemark_vi" "no_tonemark_vi_en"
        return lang

    def is_prompt_injection(self, text):
        """
        Checks if the input text contains any prompt injection patterns.

        Args:
            text (str): The text to analyze.

        Returns:
            bool: True if prompt injection is detected, False otherwise.
        """

        for pattern in prompt_injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def correct_vietnamese_text(self, text):
        """
        Uses Google Generative AI to correct and add Vietnamese tone marks to the text.

        Args:
            text (str): The Vietnamese text to correct.

        Returns:
            str: The corrected Vietnamese text.
        """
        response = self.gemini.generate_content(
            correct_vi_prompt.format(text=text)
        )
        return response.text.strip()

    def translate_en_text(self, text):
        """
        Translates English text to Vietnamese using Google Generative AI.

        Args:
            text (str): The English text to translate.

        Returns:
            str: The translated Vietnamese text.
        """

        response = self.gemini.generate_content(
            translate_en_prompt.format(text=text)
        )
        return response.text.strip()

    def translate_vi_en_text(self, text):
        """
        Translates a mixed Vietnamese-English text to Vietnamese using Google Generative AI.

        Args:
            text (str): The mixed Vietnamese-English text to translate.

        Returns:
            str: The fully translated and corrected Vietnamese text.
        """

        response = self.gemini.generate_content(
            translate_vi_en_prompt.format(text=text)
        )
        return response.text.strip()

    def preprocess_text(self, text_input):
        """
        Processes the input text by performing language detection, correction/translation, 
        prompt injection detection, and domain classification.

        Args:
            text_input (str): The text to process.

        Returns:
            tuple: A tuple containing the processed query (str), 
                   a language flag (bool), and a prompt injection flag (bool).
        """
        query = ""
        language = True
        flag = False

        if text_input:
            s1 = time.time()
            lang = self.lang_detect(text_input)
            e1 = time.time()
            print(f"Language detection time: {e1 - s1}")

            if lang == "vi" or lang == "no_tonemark_vi":
                language = True
                s2 = time.time()
                corrected_text = self.correct_vietnamese_text(text_input)
                e2 = time.time()
            if lang == "en":
                language = True
                s2 = time.time()
                corrected_text = self.translate_en_text(text_input)
                e2 = time.time()

            if lang == "vi_en" or lang == "no_tonemark_vi_en":
                language = True
                s2 = time.time()
                corrected_text = self.translate_vi_en_text(text_input)
                e2 = time.time()

            print(f"Text correction time: {e2 - s2}")

            s3 = time.time()
            if self.is_prompt_injection(corrected_text):
                flag = True
            e3 = time.time()
            print(f"Prompt injection detection time: {e3 - s3}")

            s4 = time.time()
            domain = self.classify_domain(corrected_text)
            e4 = time.time()
            print(f"Domain classification time: {e4 - s4}")

            if domain == 0:
                flag = True

            if language and not flag:
                query = corrected_text
            else:
                query = text_input

        else:
            query = ""
        return query, language, flag
