import json, os
from core.elemental import Delay, Fuzz, Overdrive, Wah, Tremolo, Distortion

EFFECT_CLASSES = {
    "Delay": Delay,
    "Fuzz": Fuzz,
    "Overdrive": Overdrive,
    "Wah": Wah,
    "Tremolo": Tremolo,
    "Distortion": Distortion,
}

UNLOCK_PATH = "resources/data/unlocked_effects.json"

def load_unlocked_effects(path=UNLOCK_PATH):
    global EFFECT_CLASSES
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        data = json.load(f)
    return [EFFECT_CLASSES[name] for name in data.get("unlocked", []) if name in EFFECT_CLASSES]


def unlock_effect(name, path=UNLOCK_PATH):
    global EFFECT_CLASSES
    if name not in EFFECT_CLASSES:
        return

    if os.path.exists(path):
        with open(path, "r") as f:
            data = json.load(f)
    else:
        data = {"unlocked": []}

    if name not in data["unlocked"]:
        data["unlocked"].append(name)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Effect '{name}' unlocked!")