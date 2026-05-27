from flask import Flask

app = Flask(__name__)


class Player:
    def __init__(self, player_id, name, hp):
        self._id = player_id
        self._name = name.strip().title()
        self._hp = hp if hp >= 0 else 0

    def __str__(self):
        return f"Player(id={self._id}, name='{self._name}', hp={self._hp})"

    def __del__(self):
        print(f"Player {self._name} удалён")


@app.route("/")
def home():
    p = Player(1, " john ", 120)
    return f"""
    <h1>AI Dungeon Game Log System</h1>
    <p>{p}</p>
    """
