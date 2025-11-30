import tkinter as tk
import random

# ---------- SETTINGS ----------
SIZE = 4
TILE_SIZE = 100
PADDING = 10

BG_COLOR = "#0b121a"

COLORS = {
    0: "#ffffff",
    2: "#c7dfff",
    4: "#9fc4ff",
    8: "#7aa8ff",
    16: "#6cd3ff",
    32: "#6dffcf",
    64: "#8cff6a",
    128: "#d8ff6a",
    256: "#ffd36a",
    512: "#ff9b5f",
    1024: "#ff6a6a",
    2048: "#b46cff",
}

# ---------- TILE ----------
class Tile:
    def __init__(self, canvas, x, y, value):
        self.canvas = canvas

        canvas.create_rectangle(
            x, y, x + TILE_SIZE, y + TILE_SIZE,
            fill=COLORS[value], outline=""
        )

        if value != 0:
            canvas.create_text(
                x + TILE_SIZE / 2,
                y + TILE_SIZE / 2,
                text=str(value),
                font=("Arial", 24, "bold"),
                fill="#0b121a" if value <= 8 else "#ffffff"
            )

# ---------- GAME ----------
class Game2048:
    def __init__(self, root):
        self.root = root
        self.root.title("2048")
        self.root.configure(bg=BG_COLOR)

        self.score = 0
        self.running = False

        self.container = tk.Frame(root, bg=BG_COLOR)
        self.container.pack(expand=True)

    # ---------- START SCREEN ----------
    def start_screen(self):
        self.clear_ui()

        tk.Label(
            self.container,
            text="2048",
            font=("Arial", 42, "bold"),
            fg="white",
            bg=BG_COLOR
        ).pack(pady=40)

        tk.Button(
            self.container,
            text="Start Game",
            font=("Arial", 18, "bold"),
            width=15,
            command=self.start_game
        ).pack()

    # ---------- GAME SETUP ----------
    def start_game(self):
        self.clear_ui()
        self.running = True
        self.score = 0

        self.score_label = tk.Label(
            self.container,
            text="Score: 0",
            font=("Arial", 18, "bold"),
            fg="white",
            bg=BG_COLOR
        )
        self.score_label.pack(pady=(10, 0))

        size_px = SIZE * TILE_SIZE + (SIZE + 1) * PADDING
        self.canvas = tk.Canvas(
            self.container,
            width=size_px,
            height=size_px,
            bg=BG_COLOR,
            highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)

        self.board = [[0]*SIZE for _ in range(SIZE)]
        self.spawn()
        self.spawn()
        self.draw()

        self.root.bind("<Key>", self.handle_key)

    # ---------- GAME OVER ----------
    def game_over_screen(self):
        self.running = False
        self.clear_ui()

        tk.Label(
            self.container,
            text="Game Over",
            font=("Arial", 36, "bold"),
            fg="white",
            bg=BG_COLOR
        ).pack(pady=30)

        tk.Label(
            self.container,
            text=f"Score: {self.score}",
            font=("Arial", 20),
            fg="white",
            bg=BG_COLOR
        ).pack(pady=10)

        tk.Button(
            self.container,
            text="Restart",
            font=("Arial", 16),
            width=14,
            command=self.start_game
        ).pack(pady=10)

        tk.Button(
            self.container,
            text="Exit",
            font=("Arial", 16),
            width=14,
            command=self.root.destroy
        ).pack()

    # ---------- INPUT ----------
    def handle_key(self, e):
        if not self.running:
            return

        keys = {
            "Left":  (-1, 0),
            "Right": (1, 0),
            "Up":    (0, -1),
            "Down":  (0, 1),
        }
        if e.keysym in keys:
            self.move(*keys[e.keysym])

    # ---------- LOGIC ----------
    def spawn(self):
        empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if self.board[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.board[r][c] = 4 if random.random() < 0.1 else 2

    def compress_merge(self, line):
        new, score = [], 0
        for v in line:
            if v:
                if new and new[-1] == v:
                    new[-1] *= 2
                    score += new[-1]
                    new.append(0)
                else:
                    new.append(v)
        new = [v for v in new if v]
        return new + [0]*(SIZE-len(new)), score

    def move(self, dx, dy):
        moved = False
        total_gain = 0
        new_board = [[0]*SIZE for _ in range(SIZE)]

        for i in range(SIZE):
            line = []
            for j in range(SIZE):
                r = i if dy == 0 else (j if dy < 0 else SIZE - 1 - j)
                c = j if dx == 0 else (j if dx < 0 else SIZE - 1 - j)
                if dx != 0: r = i
                if dy != 0: c = i
                line.append(self.board[r][c])

            merged, gain = self.compress_merge(line)
            total_gain += gain

            for j in range(SIZE):
                r = i if dy == 0 else (j if dy < 0 else SIZE - 1 - j)
                c = j if dx == 0 else (j if dx < 0 else SIZE - 1 - j)
                if dx != 0: r = i
                if dy != 0: c = i

                new_board[r][c] = merged[j]
                if new_board[r][c] != self.board[r][c]:
                    moved = True

        if moved:
            self.board = new_board
            self.score += total_gain
            self.score_label.config(text=f"Score: {self.score}")
            self.spawn()
            self.draw()

            if not self.can_move():
                self.game_over_screen()

    def can_move(self):
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == 0:
                    return True
                for dr, dc in [(1,0), (0,1)]:
                    nr, nc = r + dr, c + dc
                    if nr < SIZE and nc < SIZE and self.board[nr][nc] == self.board[r][c]:
                        return True
        return False

    # ---------- DRAW ----------
    def draw(self):
        self.canvas.delete("all")
        for r in range(SIZE):
            for c in range(SIZE):
                x = PADDING + c * (TILE_SIZE + PADDING)
                y = PADDING + r * (TILE_SIZE + PADDING)
                Tile(self.canvas, x, y, self.board[r][c])

    def clear_ui(self):
        for w in self.container.winfo_children():
            w.destroy()

# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    game.start_screen()
    root.mainloop()