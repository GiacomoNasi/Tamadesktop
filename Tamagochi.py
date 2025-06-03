class Tamagotchi:
    def __init__(self, name):
        self._name = name
        self._hunger = 50
        self._happiness = 50
        self._energy = 50
        self._hygiene = 50
        self._health = 100
        self._age = 0
        self._weight = 10
        self._discipline = 50
        self._sick = False
        self._needs_toilet = False

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def hunger(self):
        return self._hunger

    @property
    def happiness(self):
        return self._happiness

    @property
    def energy(self):
        return self._energy

    @property
    def hygiene(self):
        return self._hygiene

    @property
    def health(self):
        return self._health

    @property
    def age(self):
        return self._age

    @property
    def weight(self):
        return self._weight

    @property
    def discipline(self):
        return self._discipline

    @property
    def sick(self):
        return self._sick

    @property
    def needs_toilet(self):
        return self._needs_toilet

    # Main actions
    def feed(self, food_type="meal"):
        if food_type == "meal":
            self._hunger = max(0, self._hunger - 20)
            self._weight += 2
        elif food_type == "snack":
            self._hunger = max(0, self._hunger - 10)
            self._happiness = min(100, self._happiness + 10)
            self._weight += 1
        self._hunger = min(100, max(0, self._hunger))
        self._happiness = min(100, max(0, self._happiness))
        self._weight = min(100, max(0, self._weight))
        self._needs_toilet = True

    def play(self):
        self._happiness = min(100, self._happiness + 15)
        self._energy = max(0, self._energy - 10)
        self._hunger = min(100, self._hunger + 5)
        self._discipline = max(0, self._discipline - 2)
        self._happiness = min(100, max(0, self._happiness))
        self._energy = min(100, max(0, self._energy))
        self._hunger = min(100, max(0, self._hunger))
        self._discipline = min(100, max(0, self._discipline))

    def sleep(self):
        self._energy = min(100, self._energy + 30)
        self._hunger = min(100, self._hunger + 10)
        self._age += 1
        self._energy = min(100, max(0, self._energy))
        self._hunger = min(100, max(0, self._hunger))

    def clean(self):
        if self._needs_toilet:
            self._hygiene = min(100, self._hygiene + 30)
            self._needs_toilet = False
        else:
            self._discipline = max(0, self._discipline - 5)
        self._hygiene = min(100, max(0, self._hygiene))
        self._discipline = min(100, max(0, self._discipline))

    def heal(self):
        if self._sick:
            self._health = min(100, self._health + 40)
            self._sick = False
        else:
            self._discipline = max(0, self._discipline - 5)
        self._health = min(100, max(0, self._health))
        self._discipline = min(100, max(0, self._discipline))

    def scold(self):
        self._discipline = min(100, self._discipline + 10)
        self._happiness = max(0, self._happiness - 5)
        self._discipline = min(100, max(0, self._discipline))
        self._happiness = min(100, max(0, self._happiness))

    # Time simulation
    def tick(self):
        self._hunger = min(100, self._hunger + 2)
        self._energy = max(0, self._energy - 1)
        self._hygiene = max(0, self._hygiene - 1)
        self._happiness = max(0, self._happiness - 1)
        if self._hunger > 80 or self._hygiene < 20:
            self._health = max(0, self._health - 2)
        if self._health < 40:
            self._sick = True
        if self._hunger > 90 or self._energy < 10:
            self._happiness = max(0, self._happiness - 2)
        if self._happiness < 20:
            self._discipline = max(0, self._discipline - 1)
        if self._needs_toilet:
            self._hygiene = max(0, self._hygiene - 2)
        if self._health == 0:
            print(f"{self._name} didn't make it...")

        # Clamp all values between 0 and 100
        self._hunger = min(100, max(0, self._hunger))
        self._energy = min(100, max(0, self._energy))
        self._hygiene = min(100, max(0, self._hygiene))
        self._happiness = min(100, max(0, self._happiness))
        self._health = min(100, max(0, self._health))
        self._discipline = min(100, max(0, self._discipline))
        self._weight = min(100, max(0, self._weight))

    # Current state
    def status(self):
        return {
            "name": self._name,
            "hunger": self._hunger,
            "happiness": self._happiness,
            "energy": self._energy,
            "hygiene": self._hygiene,
            "health": self._health,
            "age": self._age,
            "weight": self._weight,
            "discipline": self._discipline,
            "sick": self._sick,
            "needs_toilet": self._needs_toilet
        }