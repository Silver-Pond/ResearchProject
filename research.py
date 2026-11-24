import csv
import math
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path

import pygame


class ResearchManager:
    """
    Manages consent confirmation, random condition allocation, the
    post-game questionnaire, and anonymous CSV exports.

    The application should call:
        handle_intro_event(event)
        start_session() after handle_intro_event returns "begin"
        handle_questionnaire_event(event)
        save_results(station) after the questionnaire returns "submitted"

    The participant must first read the approved information sheet and
    consent materials. Pressing ENTER on the introduction screen records
    their in-application confirmation; it does not replace the approved
    consent process or ethics approval.
    """

    QUESTIONS = [
        ("immersion", "I felt immersed in the environment and experience."),
        ("engagement", "I felt engaged while interacting with E.L.I."),
        ("satisfaction", "I was satisfied with the interaction with E.L.I."),
        ("perceived_realism", "E.L.I.'s responses felt realistic and appropriate."),
        (
            "perceived_adaptability",
            "E.L.I. appeared to respond appropriately to my messages.",
        ),
    ]

    LABELS = {
        1: "Strongly disagree",
        2: "Disagree",
        3: "Neither agree nor disagree",
        4: "Agree",
        5: "Strongly agree",
    }

    FIELDS = [
        "session_code",
        "condition",
        "timestamp_utc",
        "session_completed",
        "total_session_duration_seconds",
        "immersion",
        "engagement",
        "satisfaction",
        "perceived_realism",
        "perceived_adaptability",
        "conversation_count",
        "average_emotion_confidence",
    ]

    INTERACTION_FIELDS = [
        "session_code",
        "condition",
        "interaction_number",
        "detected_emotion",
        "emotion_confidence",
    ]

    def __init__(self, screen, export_path="research_data.csv"):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.export_path = Path(export_path)

        self.title = pygame.font.SysFont("arial", 34, bold=True)
        self.heading = pygame.font.SysFont("arial", 22, bold=True)
        self.font = pygame.font.SysFont("arial", 18)
        self.small = pygame.font.SysFont("arial", 14)

        self.white = (235, 240, 255)
        self.cyan = (60, 220, 255)
        self.green = (80, 230, 160)
        self.grey = (155, 175, 195)
        self.red = (255, 125, 125)
        self.background = (5, 9, 25)

        self.session_code = None
        self.condition = None
        self.consent_confirmed = False
        self.session_start_time = None

        # None means that the participant has not answered that item.
        self.ratings = {key: None for key, _ in self.QUESTIONS}
        self.answered = {key: False for key, _ in self.QUESTIONS}
        self.index = 0

        self.questionnaire_message = ""
        self.export_message = ""
        self.export_error = ""

    # ------------------------------------------------------------------
    # SESSION SETUP AND CONSENT
    # ------------------------------------------------------------------

    def start_session(self):
        """
        Allocate a condition only after the participant confirms that
        they have read the approved study information and agree to take
        part. Call this after handle_intro_event returns "begin".
        """
        if not self.consent_confirmed:
            raise RuntimeError(
                "The participant must confirm consent before a session starts."
            )

        self.session_code = "P-" + secrets.token_hex(4).upper()
        self.condition = secrets.choice(("control", "adaptive"))
        self.session_start_time = time.monotonic()

        self.ratings = {key: None for key, _ in self.QUESTIONS}
        self.answered = {key: False for key, _ in self.QUESTIONS}
        self.index = 0
        self.questionnaire_message = ""
        self.export_message = ""
        self.export_error = ""

        return self.condition

    def handle_intro_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            # The on-screen wording must clearly state what ENTER means.
            self.consent_confirmed = True
            return "begin"

        if event.key == pygame.K_ESCAPE:
            self.consent_confirmed = False
            return "menu"

        return None

    # ------------------------------------------------------------------
    # QUESTIONNAIRE
    # ------------------------------------------------------------------

    def handle_questionnaire_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        key = self.QUESTIONS[self.index][0]

        if event.key in (pygame.K_LEFT, pygame.K_a):
            current = self.ratings[key]
            self.ratings[key] = 5 if current is None else max(1, current - 1)
            self.answered[key] = True
            self.questionnaire_message = ""

        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            current = self.ratings[key]
            self.ratings[key] = 1 if current is None else min(5, current + 1)
            self.answered[key] = True
            self.questionnaire_message = ""

        elif event.key in (pygame.K_UP, pygame.K_w):
            self.index = max(0, self.index - 1)
            self.questionnaire_message = ""

        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.index = min(len(self.QUESTIONS) - 1, self.index + 1)
            self.questionnaire_message = ""

        elif event.key == pygame.K_BACKSPACE:
            self.ratings[key] = None
            self.answered[key] = False
            self.questionnaire_message = "This answer has been cleared."

        elif event.key == pygame.K_RETURN:
            if not self.answered[key]:
                self.questionnaire_message = (
                    "Please select a rating before continuing."
                )
                return None

            if self.index < len(self.QUESTIONS) - 1:
                self.index += 1
                self.questionnaire_message = ""
                return None

            unanswered = [
                question
                for question, _ in self.QUESTIONS
                if not self.answered[question]
            ]

            if unanswered:
                self.index = next(
                    i for i, (question, _) in enumerate(self.QUESTIONS)
                    if not self.answered[question]
                )
                self.questionnaire_message = (
                    "Please answer every question before submitting."
                )
                return None

            return "submitted"

        elif event.key == pygame.K_ESCAPE:
            # The main program should return to its menu without saving.
            return "menu"

        return None

    # ------------------------------------------------------------------
    # CSV EXPORT
    # ------------------------------------------------------------------

    @staticmethod
    def _append_csv_rows(path, fieldnames, rows):
        """
        Append rows and write a header for a new file.
        Refuse to append if an older file has a different column layout,
        rather than silently producing a corrupted/misaligned dataset.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        file_exists = path.exists() and path.stat().st_size > 0

        if file_exists:
            with path.open("r", newline="", encoding="utf-8-sig") as handle:
                existing_header = next(csv.reader(handle), [])

            if existing_header != fieldnames:
                raise ValueError(
                    f"{path.name} has a different CSV structure. "
                    "Move the old file to an archive location or use a new "
                    "export filename before collecting more sessions."
                )

        with path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            if not file_exists:
                writer.writeheader()

            writer.writerows(rows)

    @staticmethod
    def _get_valid_confidence(history):
        values = []

        for item in history:
            try:
                value = float(item.get("confidence", 0.0))
            except (TypeError, ValueError):
                continue

            if math.isfinite(value) and 0.0 <= value <= 1.0:
                values.append(value)

        return values

    def save_results(self, station):
        """
        Save one participant-level row and the corresponding interaction
        rows. Raw typed messages are deliberately excluded.
        """
        if not self.consent_confirmed:
            raise RuntimeError("Cannot save a session without consent confirmation.")

        if not self.session_code or self.condition not in ("control", "adaptive"):
            raise RuntimeError("No valid research session is currently active.")

        if not all(self.answered.values()):
            raise RuntimeError("Cannot save an incomplete questionnaire.")

        history = getattr(
            getattr(station, "eli", None),
            "conversation_history",
            [],
        )

        if not isinstance(history, list):
            history = []

        # Confidence values are meaningful only in the adaptive condition.
        confidence_values = (
            self._get_valid_confidence(history)
            if self.condition == "adaptive"
            else []
        )

        average_confidence = (
            round(sum(confidence_values) / len(confidence_values), 4)
            if confidence_values
            else ""
        )

        duration = (
            round(time.monotonic() - self.session_start_time, 2)
            if self.session_start_time is not None
            else ""
        )

        participant_row = {
            "session_code": self.session_code,
            "condition": self.condition,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ),
            "session_completed": True,
            "total_session_duration_seconds": duration,
            "conversation_count": len(history),
            "average_emotion_confidence": average_confidence,
        }
        participant_row.update(self.ratings)

        interaction_path = self.export_path.with_name(
            "research_interactions.csv"
        )

        interaction_rows = []

        for number, item in enumerate(history, start=1):
            if self.condition == "adaptive":
                detected_emotion = item.get(
                    "detected_emotion",
                    "uncertain",
                )
                try:
                    confidence = float(item.get("confidence", 0.0))
                    if not math.isfinite(confidence) or not 0.0 <= confidence <= 1.0:
                        confidence = ""
                except (TypeError, ValueError):
                    confidence = ""
            else:
                # Do not imply that the control condition used emotion-based
                # dialogue selection.
                detected_emotion = "not_applicable"
                confidence = ""

            interaction_rows.append({
                "session_code": self.session_code,
                "condition": self.condition,
                "interaction_number": number,
                "detected_emotion": detected_emotion,
                "emotion_confidence": (
                    round(confidence, 4)
                    if isinstance(confidence, (int, float))
                    else confidence
                ),
            })

        # Export participant-level data first, then interaction-level data.
        # If either operation fails, the calling application should show an
        # error and should not display the success screen.
        try:
            self._append_csv_rows(
                self.export_path,
                self.FIELDS,
                [participant_row],
            )

            if interaction_rows:
                self._append_csv_rows(
                    interaction_path,
                    self.INTERACTION_FIELDS,
                    interaction_rows,
                )

        except (OSError, ValueError, csv.Error) as error:
            self.export_error = str(error)
            self.export_message = ""
            raise

        self.export_message = (
            f"{self.export_path.resolve()} | {interaction_path.resolve()}"
        )
        self.export_error = ""
        return True

    # ------------------------------------------------------------------
    # DRAWING HELPERS
    # ------------------------------------------------------------------

    def draw_text(self, message, y, font=None, colour=None):
        font = font or self.font
        colour = colour or self.white
        surface = font.render(str(message), True, colour)
        self.screen.blit(
            surface,
            surface.get_rect(center=(self.width // 2, y)),
        )

    def draw_wrapped_text(
        self,
        message,
        y,
        max_width=None,
        font=None,
        colour=None,
        line_gap=6,
    ):
        font = font or self.small
        colour = colour or self.grey
        max_width = max_width or self.width - 100

        words = str(message).split()
        lines = []
        current_line = ""

        for word in words:
            candidate = f"{current_line} {word}".strip()

            if font.size(candidate)[0] <= max_width:
                current_line = candidate
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        line_height = font.get_linesize() + line_gap

        for line in lines:
            self.draw_text(line, y, font, colour)
            y += line_height

        return y

    # ------------------------------------------------------------------
    # SCREENS
    # ------------------------------------------------------------------

    def draw_intro(self):
        self.screen.fill(self.background)

        self.draw_text(
            "RESEARCH SESSION",
            95,
            self.title,
            self.cyan,
        )

        lines = [
            "This study explores emotion-aware AI dialogue in games.",
            "After agreeing to participate, you will be assigned to one of two dialogue conditions.",
            "Both conditions use the same environment and interaction tasks.",
            "After the activity, you will answer five short experience questions.",
        ]

        y = 195
        for line in lines:
            y = self.draw_wrapped_text(
                line,
                y,
                font=self.font,
                colour=self.white,
                line_gap=10,
            ) + 12

        self.draw_wrapped_text(
            "Participation is voluntary. Do not enter your name or identifying details.",
            y + 5,
            font=self.font,
            colour=self.grey,
        )

        self.draw_wrapped_text(
            "Before continuing, read the approved participant information and consent materials. "
            "Press ENTER only if you agree to participate. Press ESC to decline and return to the menu.",
            y + 65,
            font=self.small,
            colour=self.white,
        )

        self.draw_text(
            "ENTER: I AGREE AND CONTINUE     ESC: DECLINE",
            self.height - 65,
            self.heading,
            self.green,
        )

    def draw_questionnaire(self):
        self.screen.fill(self.background)

        self.draw_text(
            "POST-GAME QUESTIONNAIRE",
            75,
            self.title,
            self.cyan,
        )

        self.draw_text(
            f"Question {self.index + 1} of {len(self.QUESTIONS)}",
            145,
            self.small,
            self.grey,
        )

        key, question = self.QUESTIONS[self.index]

        self.draw_wrapped_text(
            question,
            235,
            max_width=self.width - 100,
            font=self.heading,
            colour=self.white,
        )

        spacing = min(112, (self.width - 160) // 4)
        start = self.width // 2 - 2 * spacing

        for rating in range(1, 6):
            x = start + (rating - 1) * spacing
            y = 355
            selected = self.ratings[key] == rating

            pygame.draw.circle(
                self.screen,
                self.cyan if selected else (75, 100, 125),
                (x, y),
                24,
                0 if selected else 2,
            )

            number_surface = self.heading.render(
                str(rating),
                True,
                (5, 9, 25) if selected else self.white,
            )
            self.screen.blit(
                number_surface,
                number_surface.get_rect(center=(x, y)),
            )

            label = self.small.render(
                self.LABELS[rating],
                True,
                self.grey,
            )
            self.screen.blit(
                label,
                label.get_rect(center=(x, y + 48)),
            )

        self.draw_text(
            "LEFT / RIGHT: select rating     UP / DOWN: change question",
            485,
            self.small,
            self.grey,
        )

        action = (
            "ENTER: NEXT QUESTION"
            if self.index < len(self.QUESTIONS) - 1
            else "ENTER: SUBMIT ANSWERS"
        )
        self.draw_text(action, 535, self.heading, self.green)

        if self.questionnaire_message:
            self.draw_text(
                self.questionnaire_message,
                585,
                self.small,
                self.red,
            )

        self.draw_text(
            "BACKSPACE clears this answer     ESC leaves without saving",
            self.height - 40,
            self.small,
            self.grey,
        )

    def draw_error(self):
        """Display a clear message when research data could not be exported."""
        self.screen.fill(self.background)
        self.draw_text(
            "RESEARCH DATA COULD NOT BE SAVED",
            155,
            self.title,
            self.red,
        )
        self.draw_wrapped_text(
            self.export_error or "An unexpected export error occurred.",
            255,
            max_width=self.width - 100,
            font=self.font,
            colour=self.white,
        )
        self.draw_wrapped_text(
            "Do not close the application until the researcher has recorded "
            "the export problem and followed the approved data-handling procedure.",
            365,
            max_width=self.width - 100,
            font=self.small,
            colour=self.grey,
        )
        self.draw_text(
            "ENTER OR ESC: RETURN TO MAIN MENU",
            self.height - 65,
            self.heading,
            self.green,
        )

    def draw_saved(self):
        self.screen.fill(self.background)

        self.draw_text(
            "RESEARCH RESPONSE SAVED",
            150,
            self.title,
            self.green,
        )

        self.draw_text(
            f"Anonymous session code: {self.session_code}",
            230,
            self.heading,
            self.white,
        )

        self.draw_text("CSV files:", 300, self.font, self.white)

        y = 345
        y = self.draw_wrapped_text(
            str(self.export_path.resolve()),
            y,
            max_width=self.width - 80,
            font=self.small,
            colour=self.cyan,
        ) + 18

        self.draw_wrapped_text(
            str(
                self.export_path.with_name(
                    "research_interactions.csv"
                ).resolve()
            ),
            y,
            max_width=self.width - 80,
            font=self.small,
            colour=self.cyan,
        )

        self.draw_text(
            "No participant names or raw chat messages are exported.",
            490,
            self.small,
            self.grey,
        )

        self.draw_text(
            "ENTER OR ESC: RETURN TO MAIN MENU",
            self.height - 65,
            self.heading,
            self.green,
        )
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