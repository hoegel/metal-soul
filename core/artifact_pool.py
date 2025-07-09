import random
from core.artifact import *
from core.elemental import Delay, Overdrive, Fuzz, Wah, Tremolo, Distortion

ARTIFACT_POOL = []

# Пул возможных артефактов (включает оружейные, эффектные и базовые)
def create_artifact_pool():
    global ARTIFACT_POOL
    ARTIFACT_POOL = [
        SpeedBoost(),
        MaxHealthUp(),
        WeaponDamageUp(1, 4),
        WeaponDamageUp(1, 6),
        WeaponDamageUp(2, 4),
        WeaponDamageUp(2, 6),
        WeaponDamageUp(3, 5),
        WeaponDamageUp(3, 7),
        CooldownReducer(1, 0.8),
        CooldownReducer(1, 0.8),
        CooldownReducer(2, 0.8),
        CooldownReducer(2, 0.8),
        CooldownReducer(3, 0.8),
        CooldownReducer(3, 0.8),
        RangeUp(1, 1.2),
        RangeUp(1, 1.2),
        RangeUp(2, 1.2),
        RangeUp(2, 1.2),
        RangeUp(3, 1.2),
        RangeUp(3, 1.2),
        AddEffectArtifact(1, Delay),
        AddEffectArtifact(1, Overdrive),
        AddEffectArtifact(1, Fuzz),
        AddEffectArtifact(1, Wah),
        AddEffectArtifact(1, Tremolo),
        AddEffectArtifact(1, Distortion),
        AddEffectArtifact(2, Delay),
        AddEffectArtifact(2, Overdrive),
        AddEffectArtifact(2, Fuzz),
        AddEffectArtifact(2, Wah),
        AddEffectArtifact(2, Tremolo),
        AddEffectArtifact(2, Distortion),
        AddEffectArtifact(3, Delay),
        AddEffectArtifact(3, Overdrive),
        AddEffectArtifact(3, Fuzz),
        AddEffectArtifact(3, Wah),
        AddEffectArtifact(3, Tremolo),
        AddEffectArtifact(3, Distortion)
    ]

    random.shuffle(ARTIFACT_POOL)

def get_random_artifact():
    global ARTIFACT_POOL
    ARTIFACT_POOL.append(MaxHealthUp())
    return ARTIFACT_POOL.pop(0)
