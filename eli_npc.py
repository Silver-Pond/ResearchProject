"""
E.L.I. NPC for The Last Signal.

Adaptive mode uses text-emotion predictions and contextual response templates.
Control mode deliberately remains scripted for the research comparison.
"""

import math
import random
import pygame

from sentiment_analyzer import SentimentAnalyzer


class ELINPC:
    def __init__(self, position=(820, 430), condition="adaptive", sentiment_analyzer=None):
        condition = str(condition).lower()
        if condition not in ("adaptive", "control"):
            raise ValueError("Condition must be 'adaptive' or 'control'.")

        self.position = position
        self.condition = condition
        self.size = 42
        self.cyan = (60, 220, 255)
        self.white = (235, 242, 255)
        self.dark = (7, 17, 31)
        self.green = (80, 230, 160)
        self.grey = (145, 170, 190)
        self.font = pygame.font.SysFont("arial", 18)
        self.title_font = pygame.font.SysFont("arial", 25, bold=True)
        self.small_font = pygame.font.SysFont("arial", 14)

        self.active = False
        self.phase = "closed"
        self.dialogue = ""
        self.dialogue_title = "E.L.I."
        self.input_text = ""
        self.max_input_length = 250
        self.input_active = False

        self.detected_emotion = "uncertain"
        self.emotion_result = "uncertain"
        self.emotion_confidence = 0.0
        self.last_player_message = ""
        self.last_response = ""
        self.conversation_history = []
        self.interaction_count = 0
        self.player_style = {"curious": 0, "cooperative": 0, "cautious": 0, "direct": 0}
        self._response_index = 0

        # Do not load or run the emotion model in the control condition.
        if condition == "adaptive":
            self.sentiment_analyzer = sentiment_analyzer or SentimentAnalyzer()
        else:
            self.sentiment_analyzer = None

        self.setup_initial_dialogue()

    def setup_initial_dialogue(self):
        self.dialogue_title = "E.L.I."
        self.dialogue = (
            "You made it inside. I was beginning to think the station had "
            "finally lost its last visitor. I'm E.L.I. Ask me what you need, "
            "and I'll help you make sense of this place."
        )

    def interact(self):
        if self.active:
            return
        self.active = True
        self.phase = "choice"
        self.input_text = ""
        self.input_active = True
        if self.interaction_count == 0:
            self.dialogue = (
                "Before you start exploring, there's something you should know: "
                "the station's records don't tell the whole story. What would "
                "you like to ask me?"
            )
        else:
            self.dialogue = "I'm still here. What have you found since we last spoke?"
        self.dialogue_title = "E.L.I."
        pygame.key.start_text_input()

    def _contextual_topic(self, message):
        text = message.lower()
        topics = [
            (("safe", "danger", "security", "threat", "wrong", "unsafe"),
             "security", "The security logs may explain some of the strange behaviour. "
             "The control room is a good place to investigate next."),
            (("crew", "people", "team", "researcher", "staff", "missing"),
             "crew", "The personnel records are incomplete. I can only work with "
             "what the archive still contains, but the experiment records may help."),
            (("experiment", "project", "study", "emotion", "research"),
             "research", "The project examined how an AI could respond to human "
             "communication. The experiment records should give you more detail."),
            (("terminal", "computer", "record", "archive", "log", "data"),
             "records", "The terminals hold different parts of the investigation. "
             "The medical lab and AI development area are worth checking."),
            (("eli", "yourself", "who are you", "are you", "created you"),
             "identity", "I was built to assist the research team and interpret "
             "incoming messages. I suppose I have had rather a lot of time to "
             "think about what happened here."),
            (("why", "how", "what happened", "explain", "tell me"),
             "question", "I don't have every answer. The station's records are "
             "fragmented, so we'll need to piece the events together."),
        ]
        for keywords, topic, detail in topics:
            if any(word in text for word in keywords):
                return topic, detail
        return "general", "There are still gaps in the station records. If you " \
               "explore the terminals, we may be able to connect a few more pieces."

    def _emotion_opening(self, emotion):
        openings = {
            "joy": "That's good to hear.",
            "sadness": "That sounds like a difficult moment.",
            "fear": "I can understand why this place might feel unsettling.",
            "anger": "I hear the frustration in what you've written.",
            "disgust": "It sounds as though something here has put you off.",
            "surprise": "That sounds unexpected.",
            "neutral": "I see what you're asking.",
            "uncertain": "I may not be reading the tone correctly, so tell me if I've misunderstood.",
        }
        return openings.get(emotion, openings["uncertain"])

    def generate_ml_response(self, emotion, message=""):
        """Build a varied response from emotion and the message topic."""
        topic, detail = self._contextual_topic(message)
        opening = self._emotion_opening(emotion)
        if emotion == "fear":
            closing = "We can take this one step at a time."
        elif emotion == "anger":
            closing = "I'll keep the information clear and focus on what we can verify."
        elif emotion == "sadness":
            closing = "You don't have to work everything out at once."
        elif emotion == "joy":
            closing = "Let's use that momentum and see what else we can uncover."
        elif emotion == "uncertain":
            closing = "If I've misunderstood, you can rephrase it and I'll try again."
        else:
            closing = "What would you like to look into next?"

        # Avoid repeating an identical sentence pattern on consecutive turns.
        variants = [
            f"{opening} {detail} {closing}",
            f"{detail} {opening} {closing}",
        ]
        response = variants[self._response_index % len(variants)]
        self._response_index += 1
        return response

    def generate_control_response(self):
        # Intentionally fixed and independent of emotion or message content.
        return (
            "Thank you for sharing that information. The station contains "
            "several research records that may help answer your questions. "
            "You can investigate the available terminals to learn more about "
            "the project."
        )

    def process_typed_message(self, message):
        message = str(message).strip()
        if not message:
            return

        self.last_player_message = message
        self.interaction_count += 1
        self.update_player_style(message)

        if self.condition == "adaptive":
            result = self.sentiment_analyzer.analyse(message)
            emotion = result.get("emotion", "uncertain")
            confidence = float(result.get("confidence", 0.0))
            self.detected_emotion = emotion
            self.emotion_result = emotion
            self.emotion_confidence = confidence
            response = self.generate_ml_response(emotion, message)
        else:
            # Keep emotion analysis out of the control condition.
            emotion = "not_analysed"
            confidence = 0.0
            response = self.generate_control_response()

        self.last_response = response
        self.conversation_history.append({
            "player_message": message,
            "detected_emotion": emotion,
            "confidence": confidence,
            "npc_response": response,
            "condition": self.condition,
        })
        self.dialogue_title = "E.L.I."
        self.dialogue = response
        self.input_text = ""
        self.phase = "reply"
        self.input_active = False
        pygame.key.stop_text_input()

    def update_player_style(self, message):
        text = message.lower()
        if any(word in text for word in ("why", "how", "discover", "research", "curious")):
            self.player_style["curious"] += 1
        if any(word in text for word in ("thank", "help", "together", "trust", "appreciate")):
            self.player_style["cooperative"] += 1
        if any(word in text for word in ("worried", "afraid", "scared", "unsafe", "careful")):
            self.player_style["cautious"] += 1
        if any(word in text for word in ("tell me", "explain", "what happened", "answer")):
            self.player_style["direct"] += 1

    def handle_event(self, event):
        if not self.active:
            return None
        if self.phase == "choice":
            if event.type == pygame.TEXTINPUT:
                remaining = self.max_input_length - len(self.input_text)
                if remaining > 0:
                    self.input_text += event.text[:remaining]
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                    return "closed"
                if event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.key == pygame.K_RETURN and self.input_text.strip():
                    self.process_typed_message(self.input_text)
        elif self.phase == "reply" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return "closed"
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.continue_conversation()
        return None

    def continue_conversation(self):
        self.dialogue_title = "E.L.I."
        self.dialogue = "Go on. What else have you noticed?"
        self.input_text = ""
        self.phase = "choice"
        self.input_active = True
        pygame.key.start_text_input()

    def close(self):
        self.active = False
        self.phase = "closed"
        self.input_active = False
        self.input_text = ""
        pygame.key.stop_text_input()

    def draw(self, screen, camera_x=0, camera_y=0):
        x = int(self.position[0] - camera_x)
        y = int(self.position[1] - camera_y)
        pulse = abs(math.sin(pygame.time.get_ticks() / 500))
        glow = int(27 + pulse * 7)
        pygame.draw.circle(screen, (15, 65, 90), (x + 21, y + 21), glow)
        body = pygame.Rect(x, y, self.size, self.size)
        pygame.draw.rect(screen, (35, 170, 190), body, border_radius=10)
        pygame.draw.rect(screen, self.cyan, body, 2, border_radius=10)
        pygame.draw.circle(screen, self.white, (x + 12, y + 14), 4)
        pygame.draw.circle(screen, self.white, (x + 29, y + 14), 4)
        label = self.small_font.render("E.L.I.", True, self.cyan)
        screen.blit(label, (x - 2, y + self.size + 5))

    def draw_wrapped_text(self, screen, text, x, y, max_width, max_lines=3):
        words = text.split()
        line = ""
        line_y = y
        lines_drawn = 0
        for word in words:
            test = line + word + " "
            if self.font.size(test)[0] > max_width and line:
                screen.blit(self.font.render(line.rstrip(), True, self.white), (x, line_y))
                lines_drawn += 1
                if lines_drawn >= max_lines:
                    return
                line = word + " "
                line_y += 23
            else:
                line = test
        if line and lines_drawn < max_lines:
            screen.blit(self.font.render(line.rstrip(), True, self.white), (x, line_y))

    def draw_dialogue(self, screen):
        if not self.active:
            return
        width, height = screen.get_size()
        panel = pygame.Rect(35, height - 265, width - 70, 235)
        pygame.draw.rect(screen, self.dark, panel, border_radius=12)
        pygame.draw.rect(screen, self.cyan, panel, 2, border_radius=12)
        heading = self.title_font.render(self.dialogue_title, True, self.cyan)
        screen.blit(heading, (panel.x + 20, panel.y + 12))
        self.draw_wrapped_text(screen, self.dialogue, panel.x + 20, panel.y + 52,
                               panel.width - 40, max_lines=3)

        if self.phase == "choice":
            input_box = pygame.Rect(panel.x + 20, panel.y + 135, panel.width - 40, 40)
            pygame.draw.rect(screen, (18, 35, 55), input_box, border_radius=6)
            pygame.draw.rect(screen, self.cyan, input_box, 2, border_radius=6)
            visible_text = self.input_text or "Type your message here..."
            input_colour = self.white if self.input_text else (120, 145, 165)
            while visible_text and self.font.size(visible_text)[0] > input_box.width - 20:
                visible_text = visible_text[1:]
            screen.blit(self.font.render(visible_text, True, input_colour),
                        (input_box.x + 10, input_box.y + 10))
            counter = self.small_font.render(f"{len(self.input_text)}/{self.max_input_length}",
                                             True, self.grey)
            screen.blit(counter, (input_box.right - 55, input_box.y - 20))
            instruction = self.small_font.render("TYPE YOUR MESSAGE AND PRESS ENTER TO SEND",
                                                 True, self.green)
            screen.blit(instruction, (panel.x + 20, panel.bottom - 25))
        else:
            if self.condition == "adaptive":
                if self.emotion_result == "uncertain":
                    emotion_text = "Predicted emotion: Uncertain — the message was unclear"
                else:
                    emotion_text = (f"Predicted emotion: {self.emotion_result.title()} "
                                    f"(model confidence: {self.emotion_confidence * 100:.1f}%)")
                screen.blit(self.small_font.render(emotion_text, True, self.cyan),
                            (panel.x + 20, panel.y + 145))
            instruction = self.font.render("Press ENTER to continue", True, self.green)
            screen.blit(instruction, (panel.x + 20, panel.bottom - 35))

        close_text = self.small_font.render("ESC - Close conversation", True, self.grey)
        screen.blit(close_text, (panel.right - 190, panel.bottom - 25))
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