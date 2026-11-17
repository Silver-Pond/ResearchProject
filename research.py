import csv
import secrets
from datetime import datetime, timezone
from pathlib import Path
import pygame


class ResearchManager:
    QUESTIONS = [
        ("immersion", "I felt immersed in the environment and experience."),
        ("engagement", "I felt engaged while interacting with E.L.I."),
        ("satisfaction", "I was satisfied with the interaction with E.L.I."),
        ("perceived_realism", "E.L.I.'s responses felt realistic and appropriate."),
        ("perceived_adaptability", "E.L.I. appeared to respond appropriately to my messages.")
    ]
    LABELS = {
        1: "Strongly disagree", 2: "Disagree",
        3: "Neither agree nor disagree", 4: "Agree",
        5: "Strongly agree"
    }
    FIELDS = [
        "session_code", "condition", "timestamp_utc", "session_completed",
        "immersion", "engagement", "satisfaction", "perceived_realism",
        "perceived_adaptability", "conversation_count",
        "average_emotion_confidence"
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
        self.background = (5, 9, 25)
        self.session_code = None
        self.condition = None
        self.ratings = {key: 3 for key, _ in self.QUESTIONS}
        self.index = 0
        self.export_message = ""

    def start_session(self):
        self.session_code = "P-" + secrets.token_hex(4).upper()
        self.condition = secrets.choice(["control", "adaptive"])
        self.ratings = {key: 3 for key, _ in self.QUESTIONS}
        self.index = 0
        return self.condition

    def handle_intro_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "begin"
            if event.key == pygame.K_ESCAPE:
                return "menu"
        return None

    def handle_questionnaire_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None
        key = self.QUESTIONS[self.index][0]
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.ratings[key] = max(1, self.ratings[key] - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.ratings[key] = min(5, self.ratings[key] + 1)
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.index = max(0, self.index - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.index = min(len(self.QUESTIONS) - 1, self.index + 1)
        elif event.key == pygame.K_BACKSPACE:
            self.ratings[key] = 3
        elif event.key == pygame.K_RETURN:
            if self.index < len(self.QUESTIONS) - 1:
                self.index += 1
            else:
                return "submitted"
        elif event.key == pygame.K_ESCAPE:
            return "menu"
        return None

    def save_results(self, station):
        history = station.eli.conversation_history
        confidence = [float(item.get("confidence", 0)) for item in history]
        row = {
            "session_code": self.session_code,
            "condition": self.condition,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "session_completed": True,
            "conversation_count": len(history),
            "average_emotion_confidence": round(sum(confidence) / len(confidence), 4)
                if confidence else 0.0
        }
        row.update(self.ratings)
        self.export_path.parent.mkdir(parents=True, exist_ok=True)
        exists = self.export_path.exists() and self.export_path.stat().st_size > 0
        with self.export_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.FIELDS)
            if not exists:
                writer.writeheader()
            writer.writerow(row)

        # Export interaction-level analysis without raw participant messages.
        interaction_path = self.export_path.with_name("research_interactions.csv")
        interaction_fields = [
            "session_code", "condition", "interaction_number",
            "detected_emotion", "emotion_confidence"
        ]
        interaction_exists = (
            interaction_path.exists() and interaction_path.stat().st_size > 0
        )
        with interaction_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=interaction_fields)
            if not interaction_exists:
                writer.writeheader()
            for number, item in enumerate(history, start=1):
                writer.writerow({
                    "session_code": self.session_code,
                    "condition": self.condition,
                    "interaction_number": number,
                    "detected_emotion": item.get("detected_emotion", "uncertain"),
                    "emotion_confidence": round(float(item.get("confidence", 0.0)), 4)
                })

        self.export_message = (
            f"{self.export_path.resolve()}  |  "
            f"{interaction_path.resolve()}"
        )

    def draw_text(self, message, y, font=None, colour=None):
        font = font or self.font
        colour = colour or self.white
        surface = font.render(message, True, colour)
        self.screen.blit(surface, surface.get_rect(center=(self.width // 2, y)))

    def draw_intro(self):
        self.screen.fill(self.background)
        self.draw_text("RESEARCH SESSION", 100, self.title, self.cyan)
        lines = [
            "This study explores emotion-aware AI dialogue in games.",
            "A research session will be randomly assigned to one of two dialogue conditions.",
            "Both conditions use the same environment and interaction tasks.",
            "After the activity, you will answer five short experience questions.",
            "",
            "Participation is voluntary. Do not enter your name or identifying details.",
            "Continue only after reading the approved study information and consent materials."
        ]
        for i, line in enumerate(lines):
            self.draw_text(line, 210 + i * 43, self.font if line else self.small,
                           self.white if line else self.grey)
        self.draw_text("ENTER: BEGIN RESEARCH SESSION     ESC: RETURN", self.height - 75,
                       self.heading, self.green)

    def draw_questionnaire(self):
        self.screen.fill(self.background)
        self.draw_text("POST-GAME QUESTIONNAIRE", 75, self.title, self.cyan)
        self.draw_text(f"Question {self.index + 1} of {len(self.QUESTIONS)}",
                       145, self.small, self.grey)
        key, question = self.QUESTIONS[self.index]
        self.draw_text(question, 245, self.heading, self.white)
        spacing = 112
        start = self.width // 2 - 2 * spacing
        for rating in range(1, 6):
            x, y = start + (rating - 1) * spacing, 355
            selected = self.ratings[key] == rating
            pygame.draw.circle(self.screen, self.cyan if selected else (75, 100, 125),
                               (x, y), 24, 0 if selected else 2)
            num = self.heading.render(str(rating), True,
                                      (5, 9, 25) if selected else self.white)
            self.screen.blit(num, num.get_rect(center=(x, y)))
            label = self.small.render(self.LABELS[rating], True, self.grey)
            self.screen.blit(label, label.get_rect(center=(x, y + 48)))
        self.draw_text("LEFT / RIGHT: select rating     UP / DOWN: change question",
                       495, self.small, self.grey)
        action = "ENTER: NEXT QUESTION" if self.index < 4 else "ENTER: SUBMIT ANSWERS"
        self.draw_text(action, 555, self.heading, self.green)
        self.draw_text("BACKSPACE resets this answer to 3     ESC leaves without saving",
                       self.height - 55, self.small, self.grey)

    def draw_saved(self):
        self.screen.fill(self.background)
        self.draw_text("RESEARCH RESPONSE SAVED", 180, self.title, self.green)
        self.draw_text(f"Anonymous session code: {self.session_code}", 270,
                       self.heading, self.white)
        self.draw_text("CSV file:", 340, self.font, self.white)
        self.draw_text(self.export_message, 385, self.small, self.cyan)
        self.draw_text("No participant names or raw chat messages are exported.",
                       450, self.small, self.grey)
        self.draw_text("ENTER OR ESC: RETURN TO MAIN MENU", self.height - 75,
                       self.heading, self.green)
