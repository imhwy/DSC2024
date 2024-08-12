"""
This module provides serveral step of pre-processing the query inputs
"""

import re
from underthesea import word_tokenize

from src.prompt.preprocessing_prompt import (PROMPT_INJECTION_PATTERNS,
                                             POTENTIAL_PROMPT_INJECTION_PATTERNS,
                                             TERMS_DICT,
                                             CORRECT_VI_PROMPT,
                                             TRANSLATE_EN_PROMPT,
                                             TRANSLATE_VI_EN_PROMPT)
from src.models.preprocess import ProcessedData
from src.utils.utility import clean_text

class PreprocessQuestion:
    """
    Handles the preprocessing of queries, including language detection and domain classification.
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
        Initializes the PreprocessQuestion with the necessary models and vectorizers.

        Args:
            gemini: A reference to the Gemini model used for further processing.
            domain_clf_model: The model used for classifying the query's domain.
            domain_clf_vectorizer: The vectorizer.
            lang_detect_model: The model used for detecting the language of the query.
            lang_detect_vectorizer: The vectorizer.
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

    def lang_detect(
        self,
        text: str = None
    ):
        """
        Detects the language of the input text.

        Args:
            text (str): The text to analyze.

        Returns:
            str: The detected language code.
        """
        lang = self.lang_detect_model(text)[0]['label'] 
        return lang

    def is_prompt_injection(self, text):
        """
        Checks if the input text contains any prompt injection patterns.

        Args:
            text (str): The text to analyze.

        Returns:
            bool: True if prompt injection is detected, False otherwise.
        """

        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        for pattern in POTENTIAL_PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                if self.prompt_injection_clf_model.predict(self.prompt_injection_clf_vectorizer.transform([text]))[0]:
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
            CORRECT_VI_PROMPT.format(text=text)
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
            TRANSLATE_EN_PROMPT.format(text=text)
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
            TRANSLATE_VI_EN_PROMPT.format(text=text)
        )
        return response.text.strip()

    async def preprocess_text(self, text_input):
        """
        Processes the input text by performing language detection, correction/translation, 
        prompt injection detection, and domain classification.

        Args:
            text_input (str): The text to process.

        Returns:
            ProcessedData: A tuple containing the processed query (str), 
                   a language flag (bool), and a prompt injection flag (bool).
        """
        query = ""
        language = True
        prompt_injection = False
        outdomain = False
        
        text_input = clean_text(text_input)

        if text_input:
            lang = self.lang_detect(text_input)
            if lang in {"vi", "no_tonemark_vi"}:
                corrected_text = self.correct_vietnamese_text(text_input)
            if lang == "en":
                corrected_text = self.translate_en_text(text_input)
            if lang in {"vi_en", "no_tonemark_vi_en"}:
                corrected_text = self.translate_vi_en_text(text_input)
            if self.is_prompt_injection(corrected_text):
                prompt_injection = True
                outdomain = True
            if outdomain == False:
                domain = self.classify_domain(corrected_text)
                if domain == 0:
                    outdomain = True
                if domain == 1:
                    prompt_injection = False
            if language and not outdomain:
                query = corrected_text
            else:
                query = text_input
        else:
            query = ""
        return ProcessedData(
            query=query,
            language=language,
            is_prompt_injection=prompt_injection,
            is_outdomain=outdomain
        )
