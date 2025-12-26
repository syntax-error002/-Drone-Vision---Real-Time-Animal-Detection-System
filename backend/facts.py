ANIMAL_FACTS = {
    "zebra": {
        "title": "Zebra",
        "fact": "Zebras have unique stripe patterns, like human fingerprints!",
        "habitat": "African Savannas",
        "emoji": "🦓",
        "diet": "Herbivore",
        "lifespan": "25 years",
        "speed": "65 km/h",
        "weight": "300-400 kg",
        "collective_noun": "A dazzle of zebras"
    },
    "elephant": {
        "title": "Elephant",
        "fact": "Elephants are the largest land animals and have amazing memory.",
        "habitat": "Forests & Savannas",
        "emoji": "🐘",
        "diet": "Herbivore",
        "lifespan": "60-70 years",
        "speed": "40 km/h",
        "weight": "6,000 kg",
        "collective_noun": "A parade of elephants"
    },
    "cat": {
        "title": "Cat",
        "fact": "Cats can jump up to six times their length.",
        "habitat": "Domestic",
        "emoji": "🐱",
        "diet": "Carnivore",
        "lifespan": "12-18 years",
        "speed": "48 km/h",
        "weight": "4-5 kg",
        "collective_noun": "A clowder of cats"
    },
    "dog": {
        "title": "Dog",
        "fact": "Dogs are known as 'man's best friend' for their loyalty.",
        "habitat": "Domestic",
        "emoji": "🐶",
        "diet": "Omnivore",
        "lifespan": "10-13 years",
        "speed": "30-70 km/h",
        "weight": "10-40 kg",
        "collective_noun": "A pack of dogs"
    },
    "bird": {
        "title": "Bird",
        "fact": " Some birds, like crows, are incredibly intelligent and can use tools.",
        "habitat": "Worldwide",
        "emoji": "🐦",
        "diet": "Varied",
        "lifespan": "2-100 years",
        "speed": "Varied",
        "weight": "Varied",
        "collective_noun": "A flock of birds"
    },
    "horse": {
        "title": "Horse",
        "fact": "Horses can sleep both lying down and standing up.",
        "habitat": "Plains & Fields",
        "emoji": "🐴",
        "diet": "Herbivore",
        "lifespan": "25-30 years",
        "speed": "88 km/h",
        "weight": "380-1,000 kg",
        "collective_noun": "A herd of horses"
    },
    "sheep": {
        "title": "Sheep",
        "fact": "Sheep have specialized rectangular pupils for panoramic vision.",
        "habitat": "Grasslands",
        "emoji": "🐑",
        "diet": "Herbivore",
        "lifespan": "10-12 years",
        "speed": "40 km/h",
        "weight": "45-160 kg",
        "collective_noun": "A flock of sheep"
    },
    "cow": {
        "title": "Cow",
        "fact": "Cows are social animals and make friends with each other.",
        "habitat": "Farms & Grasslands",
        "emoji": "🐮",
        "diet": "Herbivore",
        "lifespan": "15-20 years",
        "speed": "40 km/h",
        "weight": "720 kg",
        "collective_noun": "A herd of cows"
    },
    "bear": {
        "title": "Bear",
        "fact": "Bears have an excellent sense of smell, arguably better than dogs.",
        "habitat": "Forests & Mountains",
        "emoji": "🐻",
        "diet": "Omnivore",
        "lifespan": "20-30 years",
        "speed": "55 km/h",
        "weight": "100-600 kg",
        "collective_noun": "A sloth of bears"
    },
    "giraffe": {
        "title": "Giraffe",
        "fact": "A giraffe's neck is too short to reach the ground.",
        "habitat": "African Savannas",
        "emoji": "🦒",
        "diet": "Herbivore",
        "lifespan": "25 years",
        "speed": "60 km/h",
        "weight": "800-1,200 kg",
        "collective_noun": "A tower of giraffes"
    }
}

def get_fact(label):
    return ANIMAL_FACTS.get(label.lower(), {
        "title": label.capitalize(),
        "fact": "An interesting creature detected by the drone!",
        "habitat": "Unknown",
        "emoji": "🐾"
    })
