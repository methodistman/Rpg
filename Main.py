import pypim
import random
import json
import os

# Initialize PyPIM
pypim.init()

# Initialize building dimensions
BUILDING_WIDTH = 5
BUILDING_HEIGHT = 5
BUILDING_FLOORS = 3

# Initialize the building as a 3D array in PyPIM
building_memory = pypim.alloc(BUILDING_WIDTH * BUILDING_HEIGHT * BUILDING_FLOORS)
building = [[[' ' for _ in range(BUILDING_WIDTH)] for _ in range(BUILDING_HEIGHT)] for _ in range(BUILDING_FLOORS)]

# Initialize the afterlife array
afterlife = []

# Define a Character class for Player and Goblin with unique stats
class Character:
    def __init__(self, name, anxiety, despair, morality, intellect, hope, courage, empathy, stamina):
        self.name = name
        self.stats = [anxiety, despair, morality, intellect, hope, courage, empathy, stamina]
        self.position = [0, 0, 0]  # Starting position in the building (x, y, floor)
        self.memory = pypim.alloc(len(self.stats))
        pypim.write(self.memory, self.stats)

    def move(self, direction):
        if direction == 'up' and self.position[1] > 0:
            self.position[1] -= 1
        elif direction == 'down' and self.position[1] < BUILDING_HEIGHT - 1:
            self.position[1] += 1
        elif direction == 'left' and self.position[0] > 0:
            self.position[0] -= 1
        elif direction == 'right' and self.position[0] < BUILDING_WIDTH - 1:
            self.position[0] += 1
        elif direction == 'upstairs' and self.position[2] < BUILDING_FLOORS - 1:
            self.position[2] += 1
        elif direction == 'downstairs' and self.position[2] > 0:
            self.position[2] -= 1

    def update_stat(self, index, new_value):
        self.stats[index] = new_value
        pypim.write(self.memory, self.stats)

    def read_stat(self, index):
        return pypim.read(self.memory, len(self.stats))[index]

    def calculate_cross_stat(self, formula):
        stats = pypim.read(self.memory, len(self.stats))
        return eval(formula.format(*stats))

    def is_alive(self):
        return self.read_stat(4) > 0  # Check if 'Hope' is above 0

    def to_dict(self):
        return {
            'name': self.name,
            'stats': self.stats,
            'position': self.position
        }

    def from_dict(self, data):
        self.name = data['name']
        self.stats = data['stats']
        self.position = data['position']
        pypim.write(self.memory, self.stats)

class Player(Character):
    def __init__(self, name, anxiety, despair, morality, intellect, hope, courage, empathy, stamina):
        super().__init__(name, anxiety, despair, morality, intellect, hope, courage, empathy, stamina)
        self.inventory = []

class Goblin(Character):
    def __init__(self, name, anxiety, despair, morality, intellect, hope, courage, empathy, stamina):
        super().__init__(name, anxiety, despair, morality, intellect, hope, courage, empathy, stamina)

def print_building(building, player, goblin):
    for z in range(BUILDING_FLOORS):
        print(f"Floor {z + 1}")
        for y in range(BUILDING_HEIGHT):
            for x in range(BUILDING_WIDTH):
                if player.position == [x, y, z]:
                    print('P', end=' ')
                elif goblin.position == [x, y, z]:
                    print('G', end=' ')
                else:
                    print(building[z][y][x], end=' ')
            print()
        print()

def combat(player, goblin):
    while player.is_alive() and goblin.is_alive():
        psychosis_dmg = player.calculate_cross_stat("{0} + {1} - {5}")  # Psychosis: Anxiety + Despair - Courage
        goblin.update_stat(0, goblin.read_stat(0) + psychosis_dmg)
        print(f"{player.name}'s attack increases {goblin.name}'s psychosis by {psychosis_dmg}!")

        if not goblin.is_alive():
            print(f"{goblin.name} has been driven to despair!")
            afterlife.append(goblin.to_dict())  # Move goblin to afterlife
            break

        paranoia_dmg = goblin.calculate_cross_stat("{0} + {3} - {4}")  # Paranoia: Anxiety + Intellect - Hope
        player.update_stat(0, player.read_stat(0) + paranoia_dmg)
        print(f"{goblin.name}'s attack increases {player.name}'s paranoia by {paranoia_dmg}!")
        
        if not player.is_alive():
            print(f"{player.name} has been overcome by paranoia!")
            afterlife.append(player.to_dict())  # Move player to afterlife
            break

    print(f"Final Stats -> {player.name} Hope: {player.read_stat(4)}, {goblin.name} Hope: {goblin.read_stat(4)}")

def save_game(player, goblin):
    game_state = {
        'player': player.to_dict(),
        'goblin': goblin.to_dict(),
        'afterlife': afterlife
    }
    with open('savegame.json', 'w') as f:
        json.dump(game_state, f)
    print("Game saved successfully.")

def load_game():
    if not os.path.exists('savegame.json'):
        print("No saved game found.")
        return None, None

    with open('savegame.json', 'r') as f:
        game_state = json.load(f)

    player_data = game_state['player']
    goblin_data = game_state['goblin']
    global afterlife
    afterlife = game_state.get('afterlife', [])

    player = Player(
        player_data['name'], *player_data['stats']
    )
    player.from_dict(player_data)

    goblin = Goblin(
        goblin_data['name'], *goblin_data['stats']
    )
    goblin.from_dict(goblin_data)

    return player, goblin

def start_menu():
    print("Welcome to the High-Rise Apartment Building RPG!")
    print("1. Start New Game")
    print("2. Load Game")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice

def introduction():
    print("\nYou find yourself in a high-rise apartment building...")
    print("You must navigate through the rooms and floors, encountering monsters and collecting items.")
    print("Use your unique skills and attributes to survive and find your way out!\n")

def encounter_monsters(player):
    psychosis = player.calculate_cross_stat("{0} + {1} - {5}")
    encounter_probability = min(100, max(0, psychosis))  # Probability between 0 and 100
    return random.randint(0, 100) < encounter_probability

# Main program
def main():
    choice = start_menu()
    if choice == '1':
        introduction()
        # Initialize the player and a goblin with unique stats
        player = Player(name="Hero", anxiety=5, despair=3, morality=8, intellect=7, hope=10, courage=4, empathy=6, stamina=9)
        goblin = Goblin(name="Goblin", anxiety=6, despair=5, morality=3, intellect=4, hope=8, courage=2, empathy=1, stamina=7)
        goblin.position = [random.randint(0, BUILDING_WIDTH-1), random.randint(0, BUILDING_HEIGHT-1), random.randint(0, BUILDING_FLOORS-1)]
    elif choice == '2':
        player, goblin = load_game()
        if not player or not goblin:
            return
    elif choice == '3':
        print("Exiting the game.")
        return
    else:
        print("Invalid choice.")
        return

    # Game loop
    while player.is_alive():
        print_building(building, player, goblin)
        move = input("Move (up/down/left/right/upstairs/downstairs) or save: ")
        if move == 'save':
            save_game(player, goblin)
            continue
        player.move(move)

        # Check for encounters with monsters based on psychosis
        if encounter_monsters(player):
            goblin.position = player.position  # Move goblin to player's position for encounter
            print("You've encountered a goblin! Combat starts!")
            combat(player, goblin)
            if not player.is_alive():
                break

    if not player.is_alive():
        print("Game Over. You were defeated in the building.")
    else:
        print("Congratulations! You survived the high-rise apartment building.")

    # Free PyPIM memory
    pypim.free(player.memory)
    pypim.free(goblin.memory)
    pypim.free(building_memory)

if __name__ == "__main__":
    main()
