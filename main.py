import pygame
import random
from station import StationEnvironment
from research import ResearchManager

class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()

        self.title_font = pygame.font.SysFont("arial", 68, bold=True)
        self.subtitle_font = pygame.font.SysFont("arial", 21)
        self.button_font = pygame.font.SysFont("arial", 25, bold=True)
        self.small_font = pygame.font.SysFont("arial", 17)

        self.background = (5, 9, 25)
        self.white = (235, 240, 255)
        self.cyan = (60, 220, 255)
        self.button_colour = (18, 35, 65)
        self.hover_colour = (25, 75, 105)

        self.selected = 0
        self.show_instructions = False

        self.options = [
            "START GAME",
            "RESEARCH MODE",
            "HOW TO PLAY",
            "QUIT"
        ]

        self.buttons = []

        button_width = 300
        button_height = 55
        spacing = 17

        start_y = self.height // 2 - 5

        for i, option in enumerate(self.options):
            rect = pygame.Rect(
                self.width // 2 - button_width // 2,
                start_y + i * (button_height + spacing),
                button_width,
                button_height
            )
            self.buttons.append(rect)

        random.seed(10)
        self.stars = [
            (
                random.randint(0, self.width),
                random.randint(0, self.height),
                random.choice([1, 2, 3])
            )
            for _ in range(100)
        ]

    def draw_background(self):
        self.screen.fill(self.background)

        # Starfield
        for x, y, radius in self.stars:
            pygame.draw.circle(
                self.screen,
                (130, 160, 200),
                (x, y),
                radius
            )

        # Decorative horizontal lines
        pygame.draw.line(
            self.screen,
            (20, 75, 105),
            (0, 120),
            (self.width, 120),
            1
        )

        pygame.draw.line(
            self.screen,
            (20, 75, 105),
            (0, self.height - 65),
            (self.width, self.height - 65),
            1
        )

    def draw(self):
        self.draw_background()

        if self.show_instructions:
            self.draw_instructions()
            return

        # Game title
        title = self.title_font.render(
            "THE LAST SIGNAL",
            True,
            self.white
        )

        title_rect = title.get_rect(
            center=(self.width // 2, 155)
        )

        self.screen.blit(title, title_rect)

        # Cyan underline
        pygame.draw.line(
            self.screen,
            self.cyan,
            (self.width // 2 - 180, 205),
            (self.width // 2 + 180, 205),
            3
        )

        subtitle = self.subtitle_font.render(
            "AN EMOTION-AWARE AI EXPERIENCE",
            True,
            self.cyan
        )

        self.screen.blit(
            subtitle,
            subtitle.get_rect(
                center=(self.width // 2, 235)
            )
        )

        # Buttons
        mouse_position = pygame.mouse.get_pos()

        for i, (option, rect) in enumerate(
            zip(self.options, self.buttons)
        ):
            hovered = rect.collidepoint(mouse_position)
            selected = i == self.selected

            colour = (
                self.hover_colour
                if hovered or selected
                else self.button_colour
            )

            pygame.draw.rect(
                self.screen,
                colour,
                rect,
                border_radius=8
            )

            border_colour = (
                self.cyan
                if hovered or selected
                else (50, 90, 125)
            )

            pygame.draw.rect(
                self.screen,
                border_colour,
                rect,
                width=2,
                border_radius=8
            )

            text = self.button_font.render(
                option,
                True,
                self.white
            )

            self.screen.blit(
                text,
                text.get_rect(center=rect.center)
            )

        # Footer
        footer = self.small_font.render(
            "A JOURNEY THROUGH HUMAN EMOTION AND ARTIFICIAL INTELLIGENCE",
            True,
            (120, 145, 175)
        )

        self.screen.blit(
            footer,
            footer.get_rect(
                center=(self.width // 2, self.height - 32)
            )
        )

    def draw_instructions(self):
        heading = self.title_font.render(
            "HOW TO PLAY",
            True,
            self.cyan
        )

        self.screen.blit(
            heading,
            heading.get_rect(
                center=(self.width // 2, 150)
            )
        )

        instructions = [
            "You are exploring an abandoned space station.",
            "Interact with E.L.I., the station's AI companion.",
            "Your dialogue choices influence the conversation.",
            "Explore the station and complete your mission.",
            "",
            "Use your mouse to select dialogue options.",
            "Follow the on-screen instructions to progress."
        ]

        y = 250

        for line in instructions:
            text = self.subtitle_font.render(
                line,
                True,
                self.white
            )

            self.screen.blit(
                text,
                text.get_rect(
                    center=(self.width // 2, y)
                )
            )

            y += 38

        back_text = self.button_font.render(
            "PRESS ESC TO RETURN",
            True,
            self.cyan
        )

        self.screen.blit(
            back_text,
            back_text.get_rect(
                center=(self.width // 2, self.height - 100)
            )
        )

    def handle_event(self, event):
        if self.show_instructions:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.show_instructions = False
            return None

        if event.type == pygame.MOUSEMOTION:
            for i, rect in enumerate(self.buttons):
                if rect.collidepoint(event.pos):
                    self.selected = i

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, rect in enumerate(self.buttons):
                    if rect.collidepoint(event.pos):
                        return self.select_option(i)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (
                    self.selected - 1
                ) % len(self.options)

            elif event.key == pygame.K_DOWN:
                self.selected = (
                    self.selected + 1
                ) % len(self.options)

            elif event.key == pygame.K_RETURN:
                return self.select_option(self.selected)

        return None

    def select_option(self, index):
        if index == 0:
            return "start"

        elif index == 1:
            return "research"

        elif index == 2:
            self.show_instructions = True

        elif index == 3:
            return "quit"

        return None

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Last Signal")
clock = pygame.time.Clock()

main_menu = MainMenu(screen)
research = ResearchManager(screen)
station = None
game_state = "menu"
running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            continue

        if game_state == "menu":
            result = main_menu.handle_event(event)
            if result == "start":
                # A normal playthrough must not inherit a previous research condition.
                research = ResearchManager(screen)
                station = StationEnvironment(screen, condition="adaptive")
                game_state = "game"
            elif result == "research":
                game_state = "research_intro"
            elif result == "quit":
                running = False

        elif game_state == "research_intro":
            result = research.handle_intro_event(event)
            if result == "begin":
                condition = research.start_session()
                station = StationEnvironment(screen, condition=condition)
                game_state = "game"
            elif result == "menu":
                game_state = "menu"

        elif game_state == "game":
            result = station.handle_event(event)
            if result == "menu":
                if research.condition is not None:
                    research = ResearchManager(screen)
                game_state = "menu"
            elif result == "completed" and research.condition is not None:
                game_state = "questionnaire"

        elif game_state == "questionnaire":
            result = research.handle_questionnaire_event(event)
            if result == "submitted":
                try:
                    research.save_results(station)
                except OSError as error:
                    research.export_message = f"CSV save failed: {error}"
                game_state = "research_saved"
            elif result == "menu":
                game_state = "menu"

        elif game_state == "research_saved":
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE
            ):
                station = None
                research = ResearchManager(screen)
                game_state = "menu"

    if game_state == "menu":
        main_menu.draw()
    elif game_state == "research_intro":
        research.draw_intro()
    elif game_state == "game":
        station.update(dt)
        station.draw()
    elif game_state == "questionnaire":
        research.draw_questionnaire()
    elif game_state == "research_saved":
        research.draw_saved()

    pygame.display.flip()

pygame.quit()
