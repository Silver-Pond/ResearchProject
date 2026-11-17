import pygame
import math
from eli_npc import ELINPC

class StationEnvironment:

    def __init__(self, screen, condition="adaptive"):

        self.screen = screen
        self.width, self.height = screen.get_size()

        self.world_width = 1600
        self.world_height = 1100

        # Colours
        self.background = (9, 15, 25)
        self.floor_colour = (23, 32, 46)
        self.floor_grid = (31, 44, 59)
        self.wall_colour = (49, 64, 82)
        self.wall_edge = (75, 103, 125)
        self.cyan = (60, 220, 255)
        self.white = (235, 242, 255)
        self.green = (80, 230, 160)
        self.red = (230, 80, 90)

        # Fonts
        self.title_font = pygame.font.SysFont(
            "arial", 25, bold=True
        )

        self.font = pygame.font.SysFont(
            "arial", 18
        )

        self.small_font = pygame.font.SysFont(
            "arial", 14
        )

        # Player
        self.player = pygame.Rect(
            125, 160, 30, 38
        )

        self.player_speed = 220
        self.player_direction = "down"

        # Camera
        self.camera_x = 0
        self.camera_y = 0

        # Station walls and obstacles
        self.walls = []

        self.create_station()

        # AI companion
        # Experimental is the default research condition.
        self.research_condition = condition
        self.research_complete = False

        self.eli = ELINPC(
            position=(820, 430),
            condition=condition
        )

        # Research terminals
        self.terminals = [
            {
                "rect": pygame.Rect(350, 270, 40, 40),
                "name": "Medical Research Terminal",
                "description": (
                    "MEDICAL LOG: Researchers were studying "
                    "the relationship between human emotions "
                    "and artificial intelligence."
                ),
                "completed": False
            },
            {
                "rect": pygame.Rect(1150, 270, 40, 40),
                "name": "AI Development Terminal",
                "description": (
                    "AI LOG: E.L.I. was designed to recognise "
                    "human emotional responses and adapt its "
                    "conversations accordingly."
                ),
                "completed": False
            },
            {
                "rect": pygame.Rect(1120, 800, 40, 40),
                "name": "Experiment Records",
                "description": (
                    "FINAL LOG: The research team was investigating "
                    "whether adaptive AI conversations could "
                    "improve human interaction."
                ),
                "completed": False
            }
        ]

        self.dialogue = ""
        self.dialogue_title = ""
        self.show_dialogue = False

        self.objective = "Find the AI companion, E.L.I."

        self.game_completed = False

        self.elapsed_time = 0

    # -------------------------------------------------
    # CREATE STATION
    # -------------------------------------------------

    def create_station(self):

        # Outer boundaries
        self.walls.extend([
            pygame.Rect(0, 0, 1600, 30),
            pygame.Rect(0, 1070, 1600, 30),
            pygame.Rect(0, 0, 30, 1100),
            pygame.Rect(1570, 0, 30, 1100)
        ])

        # Internal partitions with openings for corridors
        self.walls.extend([

            # Upper laboratory
            pygame.Rect(30, 390, 250, 30),
            pygame.Rect(420, 390, 330, 30),

            # Central laboratory
            pygame.Rect(930, 390, 300, 30),
            pygame.Rect(1450, 390, 120, 30),

            # Lower corridor
            pygame.Rect(30, 690, 300, 30),
            pygame.Rect(480, 690, 500, 30),
            pygame.Rect(1150, 690, 420, 30),

            # Vertical partitions
            pygame.Rect(600, 30, 30, 170),
            pygame.Rect(600, 300, 30, 90),

            pygame.Rect(970, 420, 30, 220),
            pygame.Rect(970, 740, 30, 330),

            pygame.Rect(300, 720, 30, 180),
            pygame.Rect(300, 990, 30, 80)
        ])

        # Furniture and equipment
        self.walls.extend([

            pygame.Rect(150, 170, 100, 55),
            pygame.Rect(450, 150, 120, 60),

            pygame.Rect(1050, 150, 120, 60),
            pygame.Rect(1320, 180, 100, 65),

            pygame.Rect(430, 820, 100, 65),
            pygame.Rect(700, 850, 120, 65),

            pygame.Rect(1250, 850, 100, 65)
        ])

    # -------------------------------------------------
    # PLAYER MOVEMENT
    # -------------------------------------------------

    def update(self, dt):

        if self.show_dialogue or self.eli.active or self.game_completed:
            return

        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
            self.player_direction = "up"

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
            self.player_direction = "down"

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
            self.player_direction = "left"

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
            self.player_direction = "right"

        # Prevent faster diagonal movement
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        move_x = dx * self.player_speed * dt
        move_y = dy * self.player_speed * dt

        self.move_player(move_x, move_y)

        self.update_camera()

        self.elapsed_time += dt

    def move_player(self, dx, dy):

        # Horizontal movement
        self.player.x += round(dx)

        for wall in self.walls:
            if self.player.colliderect(wall):

                if dx > 0:
                    self.player.right = wall.left

                elif dx < 0:
                    self.player.left = wall.right

        # Vertical movement
        self.player.y += round(dy)

        for wall in self.walls:
            if self.player.colliderect(wall):

                if dy > 0:
                    self.player.bottom = wall.top

                elif dy < 0:
                    self.player.top = wall.bottom

    # -------------------------------------------------
    # CAMERA
    # -------------------------------------------------

    def update_camera(self):

        self.camera_x = (
            self.player.centerx - self.width // 2
        )

        self.camera_y = (
            self.player.centery - self.height // 2
        )

        self.camera_x = max(
            0,
            min(
                self.camera_x,
                self.world_width - self.width
            )
        )

        self.camera_y = max(
            0,
            min(
                self.camera_y,
                self.world_height - self.height
            )
        )

    def world_to_screen(self, rect):

        return pygame.Rect(
            rect.x - self.camera_x,
            rect.y - self.camera_y,
            rect.width,
            rect.height
        )

    # -------------------------------------------------
    # INTERACTIONS
    # -------------------------------------------------

    def handle_event(self, event):

        if self.eli.active:
            self.eli.handle_event(event)
            if not self.eli.active:
                self.check_research_completion()
                if self.research_complete:
                    return "completed"
            return None

        if self.show_dialogue:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e, pygame.K_RETURN, pygame.K_SPACE):
                    self.show_dialogue = False
                    self.check_research_completion()
                    if self.research_complete:
                        return "completed"
                elif event.key == pygame.K_ESCAPE:
                    self.show_dialogue = False
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_e:
                self.interact()
                if self.research_complete:
                    return "completed"
        return None

    def check_research_completion(self):
        all_records_read = all(item["completed"] for item in self.terminals)
        has_eli_interaction = self.eli.interaction_count > 0
        self.research_complete = all_records_read and has_eli_interaction

    def interact(self):

        if self.eli.active or self.show_dialogue:
            return

        player_center = self.player.center
        eli_center = (self.eli.position[0] + 21, self.eli.position[1] + 21)
        distance = pygame.Vector2(player_center).distance_to(
            pygame.Vector2(eli_center)
        )

        if distance < 100:
            self.eli.interact()
            return

        for terminal in self.terminals:
            terminal_distance = pygame.Vector2(player_center).distance_to(
                pygame.Vector2(terminal["rect"].center)
            )
            if terminal_distance < 100:
                if not terminal["completed"]:
                    terminal["completed"] = True
                    self.open_dialogue(terminal["name"], terminal["description"])
                else:
                    self.open_dialogue(
                        terminal["name"],
                        "This research record has already been reviewed."
                    )
                self.check_research_completion()
                return

    def open_dialogue(self, title, message):

        self.dialogue_title = title
        self.dialogue = message
        self.show_dialogue = True

    # -------------------------------------------------
    # DRAW FLOOR
    # -------------------------------------------------

    def draw_floor(self):

        self.screen.fill(self.background)

        floor = pygame.Rect(
            30 - self.camera_x,
            30 - self.camera_y,
            self.world_width - 60,
            self.world_height - 60
        )

        pygame.draw.rect(
            self.screen,
            self.floor_colour,
            floor
        )

        # Floor grid
        for x in range(30, self.world_width, 60):

            screen_x = x - self.camera_x

            pygame.draw.line(
                self.screen,
                self.floor_grid,
                (screen_x, 0),
                (screen_x, self.height),
                1
            )

        for y in range(30, self.world_height, 60):

            screen_y = y - self.camera_y

            pygame.draw.line(
                self.screen,
                self.floor_grid,
                (0, screen_y),
                (self.width, screen_y),
                1
            )

    # -------------------------------------------------
    # DRAW WALLS
    # -------------------------------------------------

    def draw_walls(self):

        for wall in self.walls:

            screen_rect = self.world_to_screen(wall)

            pygame.draw.rect(
                self.screen,
                self.wall_colour,
                screen_rect
            )

            pygame.draw.rect(
                self.screen,
                self.wall_edge,
                screen_rect,
                2
            )

    # -------------------------------------------------
    # DRAW ROOM LABELS
    # -------------------------------------------------

    def draw_room_labels(self):

        rooms = [
            ("MEDICAL LAB", 160, 85),
            ("AI DEVELOPMENT", 1050, 85),
            ("CONTROL ROOM", 750, 500),
            ("RESEARCH ARCHIVE", 1080, 760),
            ("STORAGE", 150, 790)
        ]

        for name, x, y in rooms:

            screen_position = (
                x - self.camera_x,
                y - self.camera_y
            )

            label = self.small_font.render(
                name,
                True,
                (100, 140, 165)
            )

            self.screen.blit(
                label,
                screen_position
            )

    # -------------------------------------------------
    # DRAW PLAYER
    # -------------------------------------------------

    def draw_player(self):

        player_screen = self.world_to_screen(
            self.player
        )

        # Shadow
        shadow = pygame.Rect(
            player_screen.x + 4,
            player_screen.bottom - 5,
            player_screen.width,
            9
        )

        pygame.draw.ellipse(
            self.screen,
            (5, 8, 15),
            shadow
        )

        # Player body
        pygame.draw.rect(
            self.screen,
            (65, 150, 220),
            player_screen,
            border_radius=7
        )

        pygame.draw.rect(
            self.screen,
            self.white,
            player_screen,
            2,
            border_radius=7
        )

        # Visor
        visor = pygame.Rect(
            player_screen.x + 6,
            player_screen.y + 7,
            player_screen.width - 12,
            9
        )

        pygame.draw.rect(
            self.screen,
            self.cyan,
            visor,
            border_radius=3
        )

    # -------------------------------------------------
    # DRAW E.L.I.
    # -------------------------------------------------

    def draw_eli(self):

        self.eli.draw(
            self.screen,
            self.camera_x,
            self.camera_y
        )

    # -------------------------------------------------
    # DRAW RESEARCH TERMINALS
    # -------------------------------------------------

    def draw_terminals(self):

        for terminal in self.terminals:

            rect = self.world_to_screen(
                terminal["rect"]
            )

            colour = (
                self.green
                if terminal["completed"]
                else self.cyan
            )

            pygame.draw.rect(
                self.screen,
                (20, 50, 70),
                rect,
                border_radius=5
            )

            pygame.draw.rect(
                self.screen,
                colour,
                rect,
                2,
                border_radius=5
            )

            pygame.draw.circle(
                self.screen,
                colour,
                rect.center,
                5
            )

    # -------------------------------------------------
    # DRAW HUD
    # -------------------------------------------------

    def draw_hud(self):

        hud = pygame.Rect(
            15, 15, self.width - 30, 100
        )

        pygame.draw.rect(
            self.screen,
            (8, 18, 32),
            hud,
            border_radius=8
        )

        pygame.draw.rect(
            self.screen,
            (40, 110, 140),
            hud,
            2,
            border_radius=8
        )

        title = self.title_font.render(
            "THE LAST SIGNAL",
            True,
            self.cyan
        )

        self.screen.blit(title, (32, 25))

        objective = self.font.render(
            "OBJECTIVE: " + self.objective,
            True,
            self.white
        )

        self.screen.blit(
            objective,
            (32, 70)
        )

        completed = sum(
            1 for item in self.terminals
            if item["completed"]
        )

        records = self.font.render(
            f"RESEARCH RECORDS: {completed}/3",
            True,
            self.green
        )

        self.screen.blit(
            records,
            (self.width - 280, 42)
        )

    # -------------------------------------------------
    # INTERACTION PROMPT
    # -------------------------------------------------

    def draw_interaction_prompt(self):

        nearby = False

        eli_center = (
            self.eli.position[0] + 21,
            self.eli.position[1] + 21
        )

        if math.dist(
                self.player.center,
                eli_center
        ) <= 85:
            nearby = True

        for terminal in self.terminals:

            if math.dist(
                self.player.center,
                terminal["rect"].center
            ) <= 85:
                nearby = True

        if nearby and not self.show_dialogue:

            prompt = self.font.render(
                "PRESS E TO INTERACT",
                True,
                self.cyan
            )

            rect = prompt.get_rect(
                center=(self.width // 2, self.height - 55)
            )

            self.screen.blit(prompt, rect)

    # -------------------------------------------------
    # DRAW DIALOGUE
    # -------------------------------------------------

    def draw_dialogue(self):

        if not self.show_dialogue:
            return

        panel = pygame.Rect(
            40,
            self.height - 190,
            self.width - 80,
            155
        )

        pygame.draw.rect(
            self.screen,
            (7, 17, 31),
            panel,
            border_radius=10
        )

        pygame.draw.rect(
            self.screen,
            self.cyan,
            panel,
            2,
            border_radius=10
        )

        heading = self.title_font.render(
            self.dialogue_title,
            True,
            self.cyan
        )

        self.screen.blit(
            heading,
            (panel.x + 20, panel.y + 15)
        )

        # Wrap dialogue text
        words = self.dialogue.split()
        lines = []
        current_line = ""

        for word in words:

            test_line = current_line + word + " "

            if self.font.size(test_line)[0] > panel.width - 45:

                lines.append(current_line)
                current_line = word + " "

            else:
                current_line = test_line

        lines.append(current_line)

        for i, line in enumerate(lines[:3]):

            text = self.font.render(
                line,
                True,
                self.white
            )

            self.screen.blit(
                text,
                (panel.x + 20, panel.y + 55 + i * 25)
            )

        instruction = self.small_font.render(
            "PRESS E OR ENTER TO CONTINUE",
            True,
            self.green
        )

        self.screen.blit(
            instruction,
            (panel.right - 260, panel.bottom - 25)
        )

    # -------------------------------------------------
    # MAIN DRAW METHOD
    # -------------------------------------------------

    def draw(self):

        self.draw_floor()
        self.draw_room_labels()
        self.draw_walls()
        self.draw_terminals()
        # Draw E.L.I. in the station
        self.eli.draw(
            self.screen,
            self.camera_x,
            self.camera_y
        )

        self.draw_player()

        self.draw_hud()
        self.draw_interaction_prompt()
        self.draw_dialogue()

        self.eli.draw_dialogue(self.screen)
