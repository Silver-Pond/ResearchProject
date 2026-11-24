"""
Text-based emotion classification for The Last Signal.

The returned category is a model prediction from typed text, not a measurement
or diagnosis of the player's actual emotional state.
"""

import os

# Set Hugging Face options before importing transformers.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

from transformers import pipeline


class SentimentAnalyzer:
    MODEL_NAME = "j-hartmann/emotion-english-distilroberta-base"
    VALID_EMOTIONS = {
        "anger", "disgust", "fear", "joy", "neutral", "sadness", "surprise"
    }
    MIN_CONFIDENCE = 0.45
    MAX_INPUT_LENGTH = 512

    def __init__(self, classifier=None, load_model=True):
        self.classifier = classifier
        self.available = classifier is not None
        self.error_message = None
        if load_model and classifier is None:
            self.load_model()

    def load_model(self):
        print("E.L.I. is loading the emotion analysis model...")
        print("The first download may take some time.")
        try:
            self.classifier = pipeline(
                task="text-classification",
                model=self.MODEL_NAME,
                device=-1,
            )
            self.available = True
            self.error_message = None
            print("E.L.I. emotion model loaded successfully.")
        except Exception as error:
            self.classifier = None
            self.available = False
            self.error_message = str(error)
            print("WARNING: Emotion model could not be loaded.")
            print(error)
            print("Emotion display will report an uncertain result.")

    @staticmethod
    def _uncertain_result():
        return {"emotion": "uncertain", "confidence": 0.0}

    def analyse(self, message):
        message = str(message or "").strip()
        if not message or not self.available or self.classifier is None:
            return self._uncertain_result()

        try:
            results = self.classifier(
                message[:self.MAX_INPUT_LENGTH],
                truncation=True,
                top_k=1,
            )
            if not results:
                return self._uncertain_result()

            # Transformers versions can return either a list of dictionaries
            # or a one-item nested list for top_k=1.
            prediction = results[0]
            if isinstance(prediction, list):
                if not prediction:
                    return self._uncertain_result()
                prediction = prediction[0]

            emotion = str(prediction.get("label", "")).lower().strip()
            confidence = float(prediction.get("score", 0.0))
            confidence = max(0.0, min(1.0, confidence))

            if emotion not in self.VALID_EMOTIONS or confidence < self.MIN_CONFIDENCE:
                return {"emotion": "uncertain", "confidence": confidence}

            return {"emotion": emotion, "confidence": confidence}
        except Exception as error:
            print("Emotion analysis error:", error)
            return self._uncertain_result()

    # American spelling alias for callers that prefer it.
    def analyze(self, message):
        return self.analyse(message)
"""
REFERENCE LIST

Hartmann, J., 2022. Emotion English DistilRoBERTa-base. 
[Online] Available at: https://huggingface.co/j-hartmann/emotion-english-distilroberta-base/ 
[Accessed: 25 November 2026].

Hugging Face, n.d. Pipelines. Hugging Face Transformers documentation. 
[Online] Available at: https://huggingface.co/docs/transformers/en/main_classes/pipelines 
[Accessed: 25 November 2026].

Pygame, n.d. Pygame documentation. 
[Online] Available at: https://www.pygame.org/docs/ 
[Accessed: 25 November 2026].
"""