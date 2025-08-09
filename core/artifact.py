from abc import ABC, abstractmethod
from core.elemental import Delay, Overdrive, Fuzz, Wah, Tremolo, Distortion

class Artifact(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @abstractmethod
    def apply(self, player):
        pass

class SpeedBoost(Artifact):
    def __init__(self):
        super().__init__("Speed Boost", "Increases movement speed by 1.")

    def apply(self, player):
        player.speed += 1

class MaxHealthUp(Artifact):
    def __init__(self):
        super().__init__("Vital Crystal", "Increases max health by 20.")

    def apply(self, player):
        player.max_hp += 20
        player.hp += 20


class WeaponDamageUp(Artifact):
    def __init__(self, weapon_id, amount):
        super().__init__("Sharpened Edge", f"Increases weapon damage of {weapon_id} by {amount}.")
        self.weapon_id = weapon_id
        self.amount = amount

    def apply(self, player):
        weapon = player.weapons.get(self.weapon_id)
        if weapon:
            weapon.damage += self.amount


class CooldownReducer(Artifact):
    def __init__(self, weapon_id, factor=0.8):
        super().__init__("Tempo Modulator", f"Reduces the reload time of weapon {weapon_id} by 20%.")
        self.weapon_id = weapon_id
        self.factor = factor

    def apply(self, player):
        weapon = player.weapons.get(self.weapon_id)
        if weapon:
            weapon.cooldown *= self.factor

class RangeUp(Artifact):
    def __init__(self, weapon_id, factor=1.2):
        super().__init__("Snipe Modulator", f"Increases the range(radius) of {weapon_id} by 20%.")
        self.weapon_id = weapon_id
        self.factor = factor

    def apply(self, player):
        weapon = player.weapons.get(self.weapon_id)
        if weapon:
            weapon.radius *= self.factor


class AddEffectArtifact(Artifact):
    def __init__(self, weapon_id, effect_cls):
        super().__init__(f"{effect_cls.__name__} Module", f"Adds effect {effect_cls.__name__} to weapon {weapon_id}.")
        self.weapon_id = weapon_id
        self.effect_cls = effect_cls

    def apply(self, player):
        weapon = player.weapons.get(self.weapon_id)
        if weapon:
            if issubclass(self.effect_cls, Tremolo):
                return weapon.add_effect(self.effect_cls(player.enemies))
            elif issubclass(self.effect_cls, Wah):
                return weapon.add_effect(self.effect_cls(player))
            else:
                return weapon.add_effect(self.effect_cls())