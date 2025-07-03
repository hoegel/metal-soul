SKILLS = {
    "melee": "Ближка",
    "laser": "Луч",
    "bomb": "Бомба",
    "shield": "Щит"
}

ELEMENTS = ["fire", "shock", "slow", "vampire", "knockback"]
CONFLICTS = {
    ("vampire", "shock"): True,
    ("fire", "slow"): True
}
