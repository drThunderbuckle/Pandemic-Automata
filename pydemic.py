import json
import random
import time
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.widgets import Button, RadioButtons, Slider

MAX_STATE = 32
POPULATION = 20  # population in percent from 0-100
BOARD_SIZE = 16
SHOWING_SYMPTOMS = (1.0 - 1e-8, "#C6FC60")
COLOR_GRADIENT = [(0.0, "black"), (1e-8, "#FFD9C2"), SHOWING_SYMPTOMS, (1.0, "#819073")]
zombie_map = LinearSegmentedColormap.from_list("zombies", COLOR_GRADIENT, N=MAX_STATE)
mpl.colormaps.register(zombie_map)

# Infection parameters:
TICK_RATE = 0.1  # Simulation speed
ZOMBIE_INFECTION_CHANCE = 0.3  # Chance of infection per zombie neighbor per tick
INFECTED_INFECTION_CHANCE = ZOMBIE_INFECTION_CHANCE / 4  # Chance of infection per infected neighbor per tick,
# (1/4 of the chance of a zombie neighbor).
INCUBATION_RATE = 1  # Rate at which infected people progress towards becoming zombies per tick,
# multiplied by the number of infected neighbors.
QUARANTINE_THRESHOLD = 0.5  # Infected Level at which cured cells begin treating infected as a zombie and infected isolate themselves

# Cell states:
EMPTY = 0  # Board cell.
CLEAN = 1  # Healthy person.
QUARANTINE = int(MAX_STATE * QUARANTINE_THRESHOLD)
ZOMBIE = MAX_STATE  # Completely infected person, who cannot be cured.

class Board:
    def __init__(self, num_rows, num_cols):
        print("board created")
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.board = np.zeros((self.num_rows, self.num_cols), dtype=int)

    def update_board(self, board):
        self.board = board

    def print_board(self):
        print(self.board)

    def get_board(self):
        return self.board

class Gui:
    SLIDERS = [
        # attr, label, min, max, step, format
        ("tick_rate", "Speed", 0.01, 1.0, 0.01, "%.2f"),
        ("zombie_infection_chance", "Infection chance", 0.0, 1.0, 0.01, "%.2f"),
        ("incubation_rate", "Infection rate", 0.0, 5.0, 0.1, "%.1f"),
        ("quarantine_threshold", "Quarantine threshold", 0.0, 1.0, 0.01, "%.2f"),
        ("population_percent", "Population", 1, 100, 1, "%d"),
        ("board_size", "Size", 8, 64, 1, "%d"),
        ("search_radius", "Search radius", 1, 7, 1, "%d"),
        ("initial_patients", "Initial infected", 1, 100, 1, "%d"),
    ]

    def __init__(self, game):
        print("gui started")
        plt.ion()
        self.open = True
        self.game = game
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_position([0.1, 0.31, 0.8, 0.56])
        self.fig.canvas.mpl_connect('close_event', self.on_close)
        # Create text line for load/save
        self.status = self.fig.text(0.5, 0.895, "", ha="center", va="center", fontsize=9)

        self.buttons = {}
        self.sliders = {}

        #Create Buttons
        for name, label, x in [
            ("play", "Pause", 0.1),
            ("save", "Save", 0.265),
            ("load", "Load", 0.43),
            ("clear", "Clear", 0.595),
            ("reset", "Reset", 0.76)
        ]:
            ax = self.fig.add_axes([x, 0.92, 0.14, 0.05])
            self.buttons[name] = Button(ax, label)

        # Button Click Events
        self.buttons["play"].on_clicked(self.toggle_play)
        self.buttons["save"].on_clicked(self.on_save)
        self.buttons["load"].on_clicked(self.on_load)
        self.buttons["clear"].on_clicked(self.on_clear)
        self.buttons["reset"].on_clicked(self.on_reset)

        # Create sliders from slider list
        for index, (name, label, minimum, maximum, step, value_format) in enumerate(self.SLIDERS):
            slider_ax = self.fig.add_axes([0.2, 0.28 - index * 0.032, 0.7, 0.025])
            slider = Slider(
                slider_ax,
                label,
                minimum,
                maximum,
                valinit=getattr(game, name),
                valstep=step,
                valfmt=value_format,
            )
            slider.on_changed(lambda value, setting=name: game.set_setting(setting, value))
            self.sliders[name] = slider

        # Paint tool
        self.tool_values = {"Empty": EMPTY, "Clean": CLEAN, "Infected": 2, "Zombie": ZOMBIE}
        radio_ax = self.fig.add_axes([0.02, 0.55, 0.17, 0.2])
        radio_ax.set_title("Paint", fontsize=10)
        self.radio = RadioButtons(radio_ax, list(self.tool_values), active=1)
        self.painting = False
        self.fig.canvas.mpl_connect("button_press_event", self.on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.fig.canvas.mpl_connect("button_release_event", self.on_release)

    # Painting Cells
    def _cell_from_event(self, event):
        if event.inaxes is not self.ax or event.xdata is None or event.ydata is None:
            return None
        # Set center to whole number
        col = int(np.floor(event.xdata + 0.5))
        row = int(np.floor(event.ydata + 0.5))
        rows, cols = self.game.board.get_board().shape
        if 0 <= row < rows and 0 <= col < cols:
            return row, col
        return None

    def paint(self, event):
        cell = self._cell_from_event(event)
        if cell is None:
            return
        value = self.tool_values[self.radio.value_selected]
        # Edit the board
        board = self.game.board.get_board()
        if board[cell] != value:
            board[cell] = value
            self.game.board_edited = True
            self.update_display(board)

    def on_press(self, event):
        toolbar = getattr(self.fig.canvas, "toolbar", None)
        if toolbar is not None and getattr(toolbar, "mode", "") != "":
            return
        if event.button == 1 and event.inaxes is self.ax:
            self.painting = True
            self.paint(event)

    def on_motion(self, event):
        if self.painting:
            self.paint(event)

    def on_release(self, event):
        self.painting = False

    def update_display(self, board):
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.imshow(board, cmap="zombies", vmin=0, vmax=MAX_STATE)
        self.fig.canvas.draw_idle()

    def toggle_play(self, event):
        self.game.paused = not self.game.paused
        self.buttons["play"].label.set_text("Resume" if self.game.paused else "Pause")

    def on_save(self, event):
        self.game.save_requested = True

    def on_load(self, event):
        self.game.load_requested = True

    def set_status(self, text):
        self.status.set_text(text)
        self.fig.canvas.draw_idle()

    def sync_sliders(self):
        """Move every slider to the game's current value without firing its callback
        (the callbacks for size/population/patients would otherwise reseed the board)."""
        for name, slider in self.sliders.items():
            slider.eventson = False
            slider.set_val(getattr(self.game, name))
            slider.eventson = True

    def on_clear(self, event):
        self.game.clear_requested = True

    def on_reset(self, event):
        # Fresh board built from the current slider values.
        self.game.reset_requested = True

    def on_close(self, event):
        print("Stopping")
        self.open = False


class Pandemic:
    # Settings stored as whole numbers in save files.
    INT_SETTINGS = {"population_percent", "board_size", "search_radius", "initial_patients"}

    def __init__(self):
        print("hello world")
        self.num_rows = BOARD_SIZE
        self.num_cols = BOARD_SIZE
        self.board_size = BOARD_SIZE
        self.population_percent = POPULATION
        self.initial_patients = 1
        self.search_radius = 3
        self.tick_rate = TICK_RATE
        self.zombie_infection_chance = ZOMBIE_INFECTION_CHANCE
        self.incubation_rate = INCUBATION_RATE
        self.quarantine_threshold = QUARANTINE_THRESHOLD
        self.quarantine_state = QUARANTINE
        self.paused = False
        self.reset_requested = False
        self.clear_requested = False
        self.board_edited = False
        self.load_requested = False
        self.save_requested = False

        self.board = Board(self.num_rows, self.num_cols)
        self.gui = Gui(self)

    def set_setting(self, name, value):
        if name == "board_size":
            self.board_size = int(value)
            self.num_rows = self.num_cols = self.board_size
            self.board = Board(self.num_rows, self.num_cols)
            self.reset_requested = True
        elif name == "population_percent":
            self.population_percent = int(value)
            self.reset_requested = True
        elif name == "initial_patients":
            self.initial_patients = int(value)
            self.reset_requested = True
        else:
            setattr(self, name, value)
            if name == "quarantine_threshold":
                self.quarantine_state = int(MAX_STATE * value)

    def choose_file(self):
        """Ask the user for a save file. Returns a path or None if cancelled."""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.askopenfilename(
                title="Load saved board",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            root.destroy()
        except Exception:
            path = input("Path to saved board file (blank to cancel): ").strip()
        return path or None

    def choose_save_file(self):
        """Ask where to save. Returns a path or None if cancelled."""
        try:
            import tkinter as tk
            from tkinter import filedialog

            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            path = filedialog.asksaveasfilename(
                title="Save board",
                defaultextension=".json",
                initialfile="pandemic_save.json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            root.destroy()
        except Exception:
            path = input("Path to save board to (blank to cancel): ").strip()
        return path or None

    def save_to_file(self, path, board=None):
        """Save the board and all slider values in the format load_from_file reads.

        Returns True on success.
        """
        if board is None:
            board = self.board.get_board()
        settings = {}
        for name, _, _, _, _, _ in Gui.SLIDERS:
            value = getattr(self, name)
            settings[name] = int(value) if name in self.INT_SETTINGS else float(value)

        # Settings indented, board one row per line so the file is easy to read and hand-edit.
        settings_text = json.dumps(settings, indent=2).replace("\n", "\n  ")
        rows_text = ",\n".join("    " + json.dumps(row) for row in np.asarray(board).tolist())
        text = f'{{\n  "settings": {settings_text},\n  "board": [\n{rows_text}\n  ]\n}}\n'
        try:
            with open(path, "w") as f:
                f.write(text)
        except OSError as err:
            print(f"Save failed: {err}")
            self.gui.set_status(f"Save failed: {err}")
            return False
        self.gui.set_status(f"Saved {Path(path).name}")
        return True

    def load_from_file(self, path):
        """Load a saved board and slider values from a JSON file.

        File format:
            {
              "settings": {"tick_rate": 0.1, "zombie_infection_chance": 0.3, ...},
              "board": [[0, 1, 0, ...], ...]
            }
        Every setting is optional (missing ones keep their current value). The board's shape
        decides the board size. On any problem nothing is changed and None is returned;
        otherwise the new board is returned.
        """
        int_settings = self.INT_SETTINGS
        try:
            with open(path) as f:
                data = json.load(f)
            if not isinstance(data, dict) or "board" not in data:
                raise ValueError("file has no 'board' matrix")
            board = np.array(data["board"], dtype=int)
            if board.ndim != 2 or board.size == 0:
                raise ValueError("'board' must be a non-empty 2D matrix")
            if board.min() < 0 or board.max() > MAX_STATE:
                raise ValueError(f"cell values must be between 0 and {MAX_STATE}")

            settings = data.get("settings", {})
            if not isinstance(settings, dict):
                raise ValueError("'settings' must be an object")

            # Validate everything first so a bad file can't half-apply
            cleaned = {}
            for name, _, minimum, maximum, _, _ in Gui.SLIDERS:
                if name in settings:
                    value = min(max(float(settings[name]), minimum), maximum)
                    cleaned[name] = int(round(value)) if name in int_settings else value
        except (OSError, ValueError, TypeError) as err:
            print(f"Load failed: {err}")
            self.gui.set_status(f"Load failed: {err}")
            return None

        for name, value in cleaned.items():
            setattr(self, name, value)
        self.quarantine_state = int(MAX_STATE * self.quarantine_threshold)

        self.num_rows, self.num_cols = board.shape
        if self.num_rows == self.num_cols:
            self.board_size = self.num_rows  # the matrix wins over a mismatching saved size
        self.board = Board(self.num_rows, self.num_cols)
        self.board.update_board(board)

        self.gui.sync_sliders()
        self.gui.set_status(f"Loaded {Path(path).name}")
        return board

    def create_first_board(self, patients=None):
        """Randomly places people, then infects 'patients' of them.

        If there are fewer people than 'patients', everyone is infected.
        """
        if patients is None:
            patients = self.initial_patients

        board = np.zeros((self.num_rows, self.num_cols), dtype=int)
        for i in range(self.board.num_rows):
            for j in range(self.board.num_cols):
                if random.randrange(0, 100) < self.population_percent:
                    board[i][j] = CLEAN

        people = np.argwhere(board != EMPTY)
        num_to_infect = min(patients, len(people))
        for y, x in random.sample(list(people), num_to_infect):
            board[y, x] = 2
        return board

    def move_people(self, board):
        """Each person tries one random step, wrapping at the edges.

        A blocked step means the person stays in place.
        """
        new_board = board.copy()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if board[i][j] != EMPTY:

                    # Cured Movement
                    if board[i][j] == CLEAN:

                        direction, _ = self.get_neighbors(
                            board, i, j, radius=self.search_radius, target=self.quarantine_state
                        )

                        step_y = -direction[0]
                        step_x = -direction[1]

                        # Take Random Step
                        if direction == [0, 0]:
                            dir1 = random.choice([0, 1])
                            dir2 = 1 - dir1
                            step_y = dir1 * random.choice([1, -1])
                            step_x = dir2 * random.choice([1, -1])

                        y_next = int((i + step_y) % self.num_rows)
                        x_next = int((j + step_x) % self.num_cols)

                        # If step is blocked it will try another random step and then stay still.
                        if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                            new_board[y_next, x_next] = board[i, j]
                            new_board[i, j] = EMPTY

                    # Infected Movement
                    elif CLEAN < board[i][j] < self.quarantine_state:

                        direction, _ = self.get_neighbors(
                            board, i, j, radius=self.search_radius, target=self.quarantine_state
                        )
                        step_y = -direction[0]
                        step_x = -direction[1]

                        # Take Random Step
                        if direction == [0, 0]:
                            dir1 = random.choice([0, 1])
                            dir2 = 1 - dir1
                            step_y = dir1 * random.choice([1, -1])
                            step_x = dir2 * random.choice([1, -1])

                        y_next = int((i + step_y) % self.num_rows)
                        x_next = int((j + step_x) % self.num_cols)

                        # If step is blocked it will try another random step and then stay still.
                        if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                            new_board[y_next, x_next] = board[i, j]
                            new_board[i, j] = EMPTY

                    # Quarantined Movement
                    elif self.quarantine_state <= board[i][j] < ZOMBIE:

                        direction, _ = self.get_neighbors(
                            board, i, j, radius=self.search_radius, target=CLEAN
                        )

                        step_y = -direction[0]
                        step_x = -direction[1]

                        # Take Random Step
                        if direction == [0, 0]:
                            dir1 = random.choice([0, 1])
                            dir2 = 1 - dir1
                            step_y = dir1 * random.choice([1, -1])
                            step_x = dir2 * random.choice([1, -1])

                        y_next = int((i + step_y) % self.num_rows)
                        x_next = int((j + step_x) % self.num_cols)

                        # If step is blocked it will try another random step and then stay still.
                        if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                            new_board[y_next, x_next] = board[i, j]
                            new_board[i, j] = EMPTY

                    # Zombie Movement
                    elif board[i][j] == ZOMBIE:
                        dir1 = random.choice([0, 1])
                        dir2 = 1 - dir1
                        step_y = dir1 * random.choice([1, -1])
                        step_x = dir2 * random.choice([1, -1])
                        y_next = (i + step_y) % self.num_rows
                        x_next = (j + step_x) % self.num_cols
                        # Take random step
                        # If step is blocked it will stay still.
                        if board[y_next, x_next] == EMPTY and new_board[y_next, x_next] == EMPTY:
                            new_board[y_next, x_next] = board[i, j]
                            new_board[i, j] = EMPTY

        return new_board

    def get_neighbors(self, board, i, j, radius=1, target=ZOMBIE):
        """Returns a cell's neighbors."""

        neighbors = []
        i1 = i
        j1 = j

        target_x = 0
        target_y = 0

        # Direction in [x,y]
        direction = [0, 0]

        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if (i != 0) or (j != 0):
                    check_i = (i1 + i) % self.num_rows
                    check_j = (j1 + j) % self.num_cols
                    neighbors.append(board[check_i, check_j])

                    if board[check_i, check_j] >= target:
                        target_x += i
                        target_y += j

        if (target_x != 0) and (target_y != 0):
            if abs(target_x) > abs(target_y):
                direction = [target_x / abs(target_x), 0]
            else:
                direction = [0, target_y / abs(target_y)]

        return direction, neighbors

    def spread_infection(self, board):
        """Clean people next to zombies or infected people may become infected.

        Incubating people tick one step closer to being zombies, and they
        progress faster the more infected neighbors they have.
        """
        new_board = board.copy()
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                # Read from the old board so infections don't
                # compound in a single tick.
                state = board[i, j]
                if state == CLEAN:
                    _, neighbors = self.get_neighbors(board, i, j)
                    zombie_neighbors = neighbors.count(ZOMBIE)
                    clean_neighbors = neighbors.count(CLEAN)
                    board_spots = neighbors.count(EMPTY)
                    infected_neighbors = len(neighbors) - zombie_neighbors - clean_neighbors - board_spots
                    if zombie_neighbors > 0:
                        # The chance of infection increases based off a
                        # persons number of zombie neighbors.
                        p_z = 1 - (1 - self.zombie_infection_chance) ** zombie_neighbors
                        if random.random() < p_z:
                            new_board[i, j] = 2
                    if infected_neighbors > 0:
                        # The chance of infection increases based off a
                        # persons number of infected neighbors.
                        infected_infection_chance = self.zombie_infection_chance / 4
                        p_i = 1 - (1 - infected_infection_chance) ** infected_neighbors
                        if random.random() < p_i:
                            new_board[i, j] = 2
                elif CLEAN < state < ZOMBIE:
                    _, neighbors = self.get_neighbors(board, i, j)
                    infected_neighbors = sum(n >= 2 for n in neighbors)
                    increase = 1 + self.incubation_rate * infected_neighbors
                    if (len(neighbors) - neighbors.count(EMPTY)) == 0:
                        increase = -1
                    new_board[i, j] = min(ZOMBIE, state + increase)
        return new_board

    def count_states(self, board):
        """Return (clean, infected, zombie) counts."""
        num_clean = np.count_nonzero(board == CLEAN)
        num_zombie = np.count_nonzero(board == ZOMBIE)
        num_infected = np.count_nonzero(board) - num_clean - num_zombie
        return num_clean, num_infected, num_zombie

    def start(self):
        print("game started")
        board = self.create_first_board()
        self.board.update_board(board)
        self.board.print_board()
        self.gui.update_display(board)
        plt.pause(0.5)

        # start game loop
        while self.gui.open:
            if self.reset_requested:
                board = self.create_first_board()
                self.reset_requested = False
                self.board.update_board(board)
                self.gui.update_display(board)

            if self.board_edited:
                self.board_edited = False

            if self.save_requested:
                self.save_requested = False
                path = self.choose_save_file()
                if path:
                    self.save_to_file(path, board)

            if self.load_requested:
                self.load_requested = False
                path = self.choose_file()
                loaded = self.load_from_file(path) if path else None
                if loaded is not None:
                    board = loaded
                    self.gui.update_display(board)

            if self.clear_requested:
                self.clear_requested = False
                board = np.zeros((self.num_rows, self.num_cols), dtype=int)
                self.board.update_board(board)
                self.gui.update_display(board)

            if self.paused:
                plt.pause(0.05)
                continue

            frame_start = time.perf_counter()
            board = self.move_people(board)
            board = self.spread_infection(board)

            self.board.update_board(board)
            self.gui.update_display(board)

            # Count Cell Types
            clean, infected, zombie = self.count_states(board)
            total = clean + infected + zombie
            print(f"Clean: {clean},  Infected: {infected}, Zombie: {zombie}, Total: {total}")

            elapsed = time.perf_counter() - frame_start
            plt.pause(max(0.001, self.tick_rate - elapsed))

        plt.ioff()
        plt.show()

if __name__ == "__main__":
    game = Pandemic()
    game.start()