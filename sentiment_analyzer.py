import os

# Optional Windows download/cache settings.
# These must be set before importing Hugging Face libraries.
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# If Xet downloads are unreliable on your connection,
# this uses the regular Hugging Face download mechanism.
os.environ["HF_HUB_DISABLE_XET"] = "1"

from transformers import pipeline


class SentimentAnalyzer:

    MODEL_NAME = (
        "j-hartmann/emotion-english-distilroberta-base"
    )

    VALID_EMOTIONS = {
        "anger",
        "disgust",
        "fear",
        "joy",
        "neutral",
        "sadness",
        "surprise"
    }

    def __init__(self):

        self.classifier = None
        self.available = False
        self.error_message = None

        self.load_model()

    def load_model(self):

        print("E.L.I. is loading the emotion analysis model...")
        print("The first download may take some time.")

        try:

            self.classifier = pipeline(
                "text-classification",
                model=self.MODEL_NAME
            )

            self.available = True

            print("E.L.I. emotion model loaded successfully.")

        except Exception as error:

            self.classifier = None
            self.available = False
            self.error_message = str(error)

            print("WARNING: Emotion model could not be loaded.")
            print(error)

            print(
                "E.L.I. will continue using neutral fallback responses."
            )

    def analyse(self, message):

        message = message.strip()

        if not message or not self.available:

            return {
                "emotion": "uncertain",
                "confidence": 0.0
            }

        try:

            results = self.classifier(
                message,
                truncation=True
            )

            if not results:

                return {
                    "emotion": "uncertain",
                    "confidence": 0.0
                }

            prediction = results[0]

            emotion = prediction["label"].lower()
            confidence = float(prediction["score"])

            if emotion not in self.VALID_EMOTIONS:
                emotion = "uncertain"

            if confidence < 0.45:
                emotion = "uncertain"

            return {
                "emotion": emotion,
                "confidence": confidence
            }

        except Exception as error:

            print("Emotion analysis error:", error)

            return {
                "emotion": "uncertain",
                "confidence": 0.0
            }
