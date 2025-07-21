import tkinter as tk
import random

# ---------- Constants ----------
ROWS = 20
COLUMNS = 20
TILE_SIZE = 20
WINDOW_WIDTH = TILE_SIZE * COLUMNS
WINDOW_HEIGHT = TILE_SIZE * ROWS
INITIAL_SPEED = 200
HIGHSCORE_FILE = "highscore.txt"

# ---------- Utility: Center Window ----------
class WindowCenter:
    @staticmethod
    def center(root, width, height):
        root.update_idletasks()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")

# ---------- Tile (base class for snake/food) ----------
class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# ------- Food --------
class Food(Tile):
    def __init__(self):
        self.relocate()

    def relocate(self):
        self.x = random.randint(0, COLUMNS - 1) * TILE_SIZE
        self.y = random.randint(0, ROWS - 1) * TILE_SIZE

# ---------- Snake Movement ----------
class Movement:
    def __init__(self):
        self.head = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)
        self.body = []
        self.velocity_x = 0
        self.velocity_y = 0

    def change_direction(self, key):
        if key == "Up" and self.velocity_y != 1:
            self.velocity_x, self.velocity_y = 0, -1
        elif key == "Down" and self.velocity_y != -1:
            self.velocity_x, self.velocity_y = 0, 1
        elif key == "Right" and self.velocity_x != -1:
            self.velocity_x, self.velocity_y = 1, 0
        elif key == "Left" and self.velocity_x != 1:
            self.velocity_x, self.velocity_y = -1, 0

    def move(self):
        if self.body:
            self.body = [Tile(self.head.x, self.head.y)] + self.body[:-1]
        self.head.x += self.velocity_x * TILE_SIZE
        self.head.y += self.velocity_y * TILE_SIZE

    def grow(self):
        self.body.append(Tile(self.head.x, self.head.y))

    def self_collision(self):
        return any(self.head.x == part.x and self.head.y == part.y for part in self.body)

# --------- Score Manager ----------
class ScoreManager:
    def __init__(self, file_path):
        self.file_path = file_path
        self.highscore = self.load_highscore()

    def load_highscore(self):
        try:
            with open(self.file_path, "r") as f:
                return int(f.read())
        except:
            return 0

    def save_highscore(self, score):
        if score > self.highscore:
            self.highscore = score
            with open(self.file_path, "w") as f:
                f.write(str(score))

# ----------- Base Game Class -----------
class SnakeGame:
    def __init__(self, root):
        self.window = root
        self.canvas = tk.Canvas(root, bg="black", height=WINDOW_HEIGHT, width=WINDOW_WIDTH, highlightthickness=0)
        self.canvas.pack()

        # Game state
        self.snake = Movement()
        self.food = Food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.game_over = False
        self.score_manager = ScoreManager(HIGHSCORE_FILE)

        # Button
        self.play_again_btn = tk.Button(root, text="Play Again", font=("Arial", 12), command=self.restart)
        self.play_again_btn.place_forget()

        # Setup
        WindowCenter.center(self.window, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.window.bind("<KeyRelease>", self.on_key)
        self.draw()

    def on_key(self, event):
        if not self.game_over:
            self.snake.change_direction(event.keysym)

    def update_speed(self):
        self.speed = max(30, INITIAL_SPEED - (self.score * 2))

    def restart(self):
        self.snake = Movement()
        self.food = Food()
        self.score = 0
        self.speed = INITIAL_SPEED
        self.game_over = False
        self.play_again_btn.place_forget()

# --------- Draw Game Class ----------
class Draw(SnakeGame):
    def draw(self):
        self.update_game()
        self.canvas.delete("all")

        # Draw food
        self.canvas.create_rectangle(self.food.x, self.food.y,
                                     self.food.x + TILE_SIZE, self.food.y + TILE_SIZE, fill="red")

        # Draw snake head
        self.canvas.create_rectangle(self.snake.head.x, self.snake.head.y,
                                     self.snake.head.x + TILE_SIZE, self.snake.head.y + TILE_SIZE, fill="sky blue")
        # Draw body
        for part in self.snake.body:
            self.canvas.create_rectangle(part.x, part.y,
                                         part.x + TILE_SIZE, part.y + TILE_SIZE, fill="sky blue")

        # Draw score and game status
        if self.game_over:
            # Centered Game Over Text
            self.canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 40,
                                    font="Arial 20", text=f"Game Over", fill="white")
            # Display current score
            self.canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                    font="Arial 16", text=f"Score: {self.score}", fill="white")
            # Display high score
            self.canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20,
                        font="Arial 16", text=f"High Score: {self.score_manager.highscore}",
                        fill="white", anchor="center")

            # Play Again Button
            self.play_again_btn.place(x=WINDOW_WIDTH // 2 - 50, y=WINDOW_HEIGHT // 2 + 40)
        else:
            # Display current score at top-left
            self.canvas.create_text(10, 10, font="Arial 10",
                        text=f"Score: {self.score}", fill="white", anchor="nw")

            # Display high score just below current score
            self.canvas.create_text(10, 30, font="Arial 10",
                        text=f"High Score: {self.score_manager.highscore}", fill="white", anchor="nw")


        self.window.after(self.speed, self.draw)

    def update_game(self):
        if self.game_over:
            return

        self.snake.move()

        # Wall collision
        if (self.snake.head.x < 0 or self.snake.head.x >= WINDOW_WIDTH or
            self.snake.head.y < 0 or self.snake.head.y >= WINDOW_HEIGHT):
            self.game_over = True
            self.score_manager.save_highscore(self.score)
            return

        # Self collision
        if self.snake.self_collision():
            self.game_over = True
            self.score_manager.save_highscore(self.score)
            return

        # Eat food
        if self.snake.head.x == self.food.x and self.snake.head.y == self.food.y:
            self.snake.grow()
            self.food.relocate()
            self.score += 1
            self.update_speed()


# ------------ Main Menu --------
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide early blank window
    root.title("Snake Game")
    root.resizable(False, False)

    WindowCenter.center(root, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Menu
    menu_frame = tk.Frame(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
    menu_frame.pack_propagate(False)
    menu_frame.pack()
    root.deiconify()  # Show menu after layout is ready

    title = tk.Label(menu_frame, text="🐍 SNAKE GAME 🐍", font=("Arial", 24), fg="white", bg="black")
    title.pack(pady=50)

    def start_game():
        menu_frame.pack_forget()
        Draw(root)

    start_btn = tk.Button(menu_frame, text="Start Game", font=("Arial", 16), command=start_game)
    start_btn.pack()

    root.mainloop()
