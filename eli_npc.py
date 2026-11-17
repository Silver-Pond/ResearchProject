import pygame
import math

from sentiment_analyzer import SentimentAnalyzer

class ELINPC:

    def __init__(
        self,
        position=(820, 430),
        condition="adaptive",
        sentiment_analyzer=None
    ):

        # Validate research condition
        condition = condition.lower()

        if condition not in ("adaptive", "control"):
            raise ValueError(
                "Condition must be 'adaptive' or 'control'."
            )

        self.position = position
        self.condition = condition

        # -----------------------------------------
        # NPC APPEARANCE
        # -----------------------------------------

        self.size = 42

        self.cyan = (60, 220, 255)
        self.white = (235, 242, 255)
        self.dark = (7, 17, 31)
        self.green = (80, 230, 160)
        self.grey = (145, 170, 190)

        self.font = pygame.font.SysFont(
            "arial", 18
        )

        self.title_font = pygame.font.SysFont(
            "arial", 25, bold=True
        )

        self.small_font = pygame.font.SysFont(
            "arial", 14
        )

        # -----------------------------------------
        # DIALOGUE STATE
        # -----------------------------------------

        self.active = False
        self.phase = "closed"

        self.dialogue = ""
        self.dialogue_title = "E.L.I."

        # -----------------------------------------
        # PLAYER MODELLING
        # -----------------------------------------

        self.detected_emotion = "neutral"

        self.player_style = {
            "curious": 0,
            "cooperative": 0,
            "cautious": 0,
            "direct": 0
        }

        self.interaction_count = 0

        # -----------------------------------------
        # RESEARCH INFORMATION
        # -----------------------------------------

        self.last_player_message = ""
        self.last_response = ""

        self.conversation_history = []

        # -----------------------------------------
        # MACHINE LEARNING
        # -----------------------------------------

        # Allow an existing analyzer to be passed in.
        # This avoids loading the model repeatedly.
        if sentiment_analyzer is not None:
            self.sentiment_analyzer = sentiment_analyzer
        else:
            self.sentiment_analyzer = SentimentAnalyzer()

        self.emotion_confidence = 0.0
        self.emotion_result = "neutral"

        # -----------------------------------------
        # TYPED INPUT
        # -----------------------------------------

        self.input_text = ""
        self.max_input_length = 250

        self.input_active = False

        # -----------------------------------------
        # INITIAL DIALOGUE
        # -----------------------------------------

        self.setup_initial_dialogue()

    # =============================================
    # INITIAL DIALOGUE
    # =============================================

    def setup_initial_dialogue(self):

        self.dialogue_title = "E.L.I."

        self.dialogue = (
            "Welcome back, researcher. I am E.L.I., "
            "the station's artificial intelligence. "
            "It has been a long time since someone "
            "visited this facility."
        )

    # =============================================
    # START INTERACTION
    # =============================================

    def interact(self):

        if self.active:
            return

        self.active = True
        self.phase = "choice"

        self.input_text = ""
        self.input_active = True

        self.dialogue_title = "E.L.I."

        self.dialogue = (
            "Hello, researcher. I am E.L.I. "
            "You can type a message and I will "
            "try to understand its emotional tone."
        )

        pygame.key.start_text_input()

    # =============================================
    # MACHINE-LEARNING RESPONSES
    # =============================================

    def generate_ml_response(self, emotion):

        responses = {

            "joy":
                "Your positive attitude is encouraging. "
                "I believe we can work together to uncover "
                "the station's research.",

            "sadness":
                "This situation may feel difficult. "
                "We can take things one step at a time. "
                "I am here to assist.",

            "fear":
                "It is understandable to have concerns "
                "about an unfamiliar environment. "
                "I can help you investigate the station.",

            "anger":
                "I recognise that something may be "
                "frustrating you. I will do my best to "
                "provide clear information and help "
                "resolve your concerns.",

            "disgust":
                "I understand that you may have "
                "reservations about what you have "
                "discovered. Would you like me to "
                "explain the research records?",

            "surprise":
                "That is an interesting reaction. "
                "There is still much about this station "
                "that we have yet to discover.",

            "neutral":
                "I am ready to assist. We can explore "
                "the research records and investigate "
                "what happened here.",

            "uncertain":
                "I am not entirely sure how to interpret "
                "your message, but I am listening. "
                "Could you tell me a little more?"
        }

        return responses.get(
            emotion,
            responses["neutral"]
        )

    # =============================================
    # FIXED CONTROL RESPONSE
    # =============================================

    def generate_control_response(self):

        return (
            "Thank you for sharing that information. "
            "The station contains several research "
            "records that may help answer your questions. "
            "You can investigate the available terminals "
            "to learn more about the project."
        )

    # =============================================
    # PROCESS TYPED MESSAGE
    # =============================================

    def process_typed_message(self, message):

        message = message.strip()

        if not message:
            return

        # Analyse the player's typed message.
        result = self.sentiment_analyzer.analyse(
            message
        )

        emotion = result["emotion"]
        confidence = result["confidence"]

        # Store prediction information.
        self.detected_emotion = emotion
        self.emotion_result = emotion
        self.emotion_confidence = confidence

        self.last_player_message = message

        self.interaction_count += 1

        # Update interaction-style information.
        self.update_player_style(message)

        # -----------------------------------------
        # ADAPTIVE OR CONTROL CONDITION
        # -----------------------------------------

        if self.condition == "adaptive":

            # Adaptive condition uses predicted emotion.
            response = self.generate_ml_response(
                emotion
            )

        else:

            # Control condition uses a fixed response.
            # Emotion prediction does not influence it.
            response = self.generate_control_response()

        self.last_response = response

        # -----------------------------------------
        # RECORD RESEARCH DATA
        # -----------------------------------------

        self.conversation_history.append({

            "player_message": message,

            "detected_emotion": emotion,

            "confidence": confidence,

            "npc_response": response,

            "condition": self.condition

        })

        # -----------------------------------------
        # DISPLAY NPC RESPONSE
        # -----------------------------------------

        self.dialogue_title = "E.L.I. - AI RESPONSE"

        self.dialogue = response

        self.input_text = ""

        self.phase = "reply"

        self.input_active = False

        pygame.key.stop_text_input()

    # =============================================
    # PLAYER INTERACTION STYLE
    # =============================================

    def update_player_style(self, message):

        text = message.lower()

        if any(word in text for word in [
            "curious",
            "why",
            "how",
            "discover",
            "research"
        ]):

            self.player_style["curious"] += 1

        if any(word in text for word in [
            "thank",
            "help",
            "together",
            "trust",
            "appreciate"
        ]):

            self.player_style["cooperative"] += 1

        if any(word in text for word in [
            "worried",
            "afraid",
            "scared",
            "trust"
        ]):

            self.player_style["cautious"] += 1

        if any(word in text for word in [
            "tell me",
            "explain",
            "what happened",
            "answer"
        ]):

            self.player_style["direct"] += 1

    # =============================================
    # EVENT HANDLING
    # =============================================

    def handle_event(self, event):

        if not self.active:
            return None

        # -----------------------------------------
        # TYPED TEXT
        # -----------------------------------------

        if self.phase == "choice":

            if event.type == pygame.TEXTINPUT:

                if len(self.input_text) < self.max_input_length:

                    remaining = (
                        self.max_input_length
                        - len(self.input_text)
                    )

                    self.input_text += event.text[:remaining]

                return None

            # -------------------------------------
            # KEYBOARD INPUT
            # -------------------------------------

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.close()

                    return "closed"

                elif event.key == pygame.K_BACKSPACE:

                    self.input_text = self.input_text[:-1]

                elif event.key == pygame.K_RETURN:

                    if self.input_text.strip():

                        self.process_typed_message(
                            self.input_text
                        )

                return None

        # -----------------------------------------
        # NPC RESPONSE
        # -----------------------------------------

        elif self.phase == "reply":

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    self.close()

                    return "closed"

                elif event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE
                ):

                    self.continue_conversation()

        return None

    # =============================================
    # CONTINUE CONVERSATION
    # =============================================

    def continue_conversation(self):

        self.dialogue_title = "E.L.I."

        self.dialogue = (
            "What would you like to discuss next? "
            "Type another message below."
        )

        self.input_text = ""

        self.phase = "choice"

        self.input_active = True

        pygame.key.start_text_input()

    # =============================================
    # CLOSE CONVERSATION
    # =============================================

    def close(self):

        self.active = False
        self.phase = "closed"

        self.input_active = False
        self.input_text = ""

        pygame.key.stop_text_input()

    # =============================================
    # DRAW NPC IN THE WORLD
    # =============================================

    def draw(self, screen, camera_x=0, camera_y=0):

        x = int(self.position[0] - camera_x)
        y = int(self.position[1] - camera_y)

        pulse = abs(
            math.sin(pygame.time.get_ticks() / 500)
        )

        glow = int(27 + pulse * 7)

        # Glow effect
        pygame.draw.circle(
            screen,
            (15, 65, 90),
            (x + 21, y + 21),
            glow
        )

        # Robot body
        body = pygame.Rect(
            x,
            y,
            self.size,
            self.size
        )

        pygame.draw.rect(
            screen,
            (35, 170, 190),
            body,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            self.cyan,
            body,
            2,
            border_radius=10
        )

        # Robot eyes
        pygame.draw.circle(
            screen,
            self.white,
            (x + 12, y + 14),
            4
        )

        pygame.draw.circle(
            screen,
            self.white,
            (x + 29, y + 14),
            4
        )

        # NPC name
        label = self.small_font.render(
            "E.L.I.",
            True,
            self.cyan
        )

        screen.blit(
            label,
            (x - 2, y + self.size + 5)
        )

    # =============================================
    # TEXT WRAPPING
    # =============================================

    def draw_wrapped_text(
        self,
        screen,
        text,
        x,
        y,
        max_width,
        max_lines=3
    ):

        words = text.split()

        line = ""
        line_y = y
        lines_drawn = 0

        for word in words:

            test = (
                line + word + " "
            )

            if self.font.size(test)[0] > max_width and line:

                rendered = self.font.render(
                    line.rstrip(),
                    True,
                    self.white
                )

                screen.blit(
                    rendered,
                    (x, line_y)
                )

                lines_drawn += 1

                if lines_drawn >= max_lines:
                    return

                line = word + " "
                line_y += 23

            else:

                line = test

        if line and lines_drawn < max_lines:

            rendered = self.font.render(
                line.rstrip(),
                True,
                self.white
            )

            screen.blit(
                rendered,
                (x, line_y)
            )

    # =============================================
    # DRAW DIALOGUE INTERFACE
    # =============================================

    def draw_dialogue(self, screen):

        if not self.active:
            return

        width, height = screen.get_size()

        panel = pygame.Rect(
            35,
            height - 265,
            width - 70,
            235
        )

        # Panel background
        pygame.draw.rect(
            screen,
            self.dark,
            panel,
            border_radius=12
        )

        pygame.draw.rect(
            screen,
            self.cyan,
            panel,
            2,
            border_radius=12
        )

        # -----------------------------------------
        # HEADING
        # -----------------------------------------

        heading = self.title_font.render(
            self.dialogue_title,
            True,
            self.cyan
        )

        screen.blit(
            heading,
            (panel.x + 20, panel.y + 12)
        )

        # -----------------------------------------
        # DIALOGUE TEXT
        # -----------------------------------------

        self.draw_wrapped_text(
            screen,
            self.dialogue,
            panel.x + 20,
            panel.y + 52,
            panel.width - 40,
            max_lines=3
        )

        # -----------------------------------------
        # PLAYER INPUT
        # -----------------------------------------

        if self.phase == "choice":

            input_box = pygame.Rect(
                panel.x + 20,
                panel.y + 135,
                panel.width - 40,
                40
            )

            pygame.draw.rect(
                screen,
                (18, 35, 55),
                input_box,
                border_radius=6
            )

            pygame.draw.rect(
                screen,
                self.cyan,
                input_box,
                2,
                border_radius=6
            )

            # Keep the end of long input visible.
            placeholder = "Type your message here..."

            if self.input_text:

                visible_text = self.input_text

                available_width = input_box.width - 20

                while (
                    visible_text
                    and self.font.size(visible_text)[0] > available_width
                ):

                    visible_text = visible_text[1:]

                input_colour = self.white

            else:

                visible_text = placeholder
                input_colour = (120, 145, 165)

            typed_message = self.font.render(
                visible_text,
                True,
                input_colour
            )

            screen.blit(
                typed_message,
                (input_box.x + 10, input_box.y + 10)
            )

            # Character counter
            counter = self.small_font.render(
                f"{len(self.input_text)}/{self.max_input_length}",
                True,
                self.grey
            )

            screen.blit(
                counter,
                (input_box.right - 55, input_box.y - 20)
            )

            instruction = self.small_font.render(
                "TYPE YOUR MESSAGE AND PRESS ENTER TO SEND",
                True,
                self.green
            )

            screen.blit(
                instruction,
                (panel.x + 20, panel.bottom - 25)
            )

        # -----------------------------------------
        # NPC RESPONSE INFORMATION
        # -----------------------------------------

        else:

            # Only show the emotion prediction in the
            # adaptive condition. This avoids exposing
            # the prediction to the control condition.
            if self.condition == "adaptive":

                emotion_text = (
                    f"Estimated tone: {self.emotion_result} "
                    f"({self.emotion_confidence * 100:.1f}%)"
                )

                emotion_surface = self.small_font.render(
                    emotion_text,
                    True,
                    self.cyan
                )

                screen.blit(
                    emotion_surface,
                    (panel.x + 20, panel.y + 145)
                )

            instruction = self.font.render(
                "Press ENTER to continue",
                True,
                self.green
            )

            screen.blit(
                instruction,
                (panel.x + 20, panel.bottom - 35)
            )

        # -----------------------------------------
        # CLOSE INSTRUCTION
        # -----------------------------------------

        close_text = self.small_font.render(
            "ESC - Close conversation",
            True,
            self.grey
        )

        screen.blit(
            close_text,
            (
                panel.right - 190,
                panel.bottom - 25
            )
        )
