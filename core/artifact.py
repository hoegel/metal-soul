class Artifact:
    def __init__(self, name, effect_func, conflicts=None):
        self.name = name
        self.effect_func = effect_func
        self.conflicts = conflicts or []
