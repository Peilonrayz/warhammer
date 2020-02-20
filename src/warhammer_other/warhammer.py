# -*- coding: utf-8 -*-
import collections
import functools
import itertools
import operator
from fractions import Fraction
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd


def tail(n, iterable):
    "Return an iterator over the last n items"
    # tail(3, 'ABCDEFG') --> E F G
    return iter(collections.deque(iterable, maxlen=n))


class DisplayMeta(type):
    def __repr__(self):
        return f'{self.__name__}'


class Buff(metaclass=DisplayMeta):
    SINGLE = False


class ValueBuff(Buff):
    value: int
    UP: bool = True

    def __init__(self, value: int):
        self.value = value
        if self.UP:
            self.values = range(value, 100)
        else:
            self.values = range(1, value + 1)

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

    def __lt__(self, other):
        return self.value < other.value

    def __le__(self, other):
        return self.value <= other.value

    def __gt__(self, other):
        return self.value > other.value

    def __ge__(self, other):
        return self.value >= other.value


class JoinableBuff:
    def __add__(self, other):
        raise NotImplementedError()


class Attacks(ValueBuff):
    SINGLE = True


class Damage(ValueBuff, JoinableBuff):
    def __add__(self, other):
        return Damage(self.value + other.value)


class Dice(Buff):
    def __init__(self, *, amount=1, sides=6):
        self.amount = amount
        self.sides = sides

    @property
    def chances(self):
        return self.amount * [{
            i: Fraction(1, self.sides)
            for i in range(1, self.sides + 1)
        }]


class Score(ValueBuff):
    SINGLE = True


class BonusAttack(ValueBuff):
    pass


class MortalWound(ValueBuff):
    pass


class SelfWound(ValueBuff):
    UP = False


class SkipNext(ValueBuff, JoinableBuff):
    def __add__(self, other):
        return min(self, other)


class Modifier(ValueBuff, JoinableBuff):
    UP = None

    def __add__(self, other):
        return Modifier(self.value + other.value)


class Reroll(ValueBuff, JoinableBuff):
    UP = False
    value: Optional[int]

    def __init__(self, value: Optional[int]):
        self.value = value
        if value is None:
            self.values = None
        elif self.UP:
            self.values = range(value, 7)
        else:
            self.values = range(1, value + 1)

    def __add__(self, other):
        if self.value is None:
            return self
        if other.value is None:
            return other
        return max(self, other)


class Skip(Buff, JoinableBuff):
    def __add__(self, other):
        return self


def read_buffs(buffs):
    buffs_ = {}
    for buff in buffs:
        buffs_.setdefault(type(buff), []).append(buff)
    for key, buffs in buffs_.items():
        if key.SINGLE:
            if len(buffs) > 1:
                raise ValueError(f'There can only be one buff of type {key}')
            buffs_[key] = buffs[0]
        if issubclass(key, JoinableBuff):
            buffs = iter(buffs)
            buff = next(buffs)
            for b in buffs:
                buff += b
            buffs_[key] = buff
    return buffs_


def phase(*buffs):
    buffs_ = read_buffs(buffs)
    if Skip in buffs_:
        return {Score: Fraction(1, 1)}
    score = buffs_.pop(Score).value
    reroll = buffs_.pop(Reroll, Reroll(0))
    if reroll.value is None:
        reroll = Reroll(score - 1)
    modifier = buffs_.pop(Modifier, Modifier(0)).value
    skip_next = buffs_.get(SkipNext, None)
    if skip_next is not None:
        scores = range(score, skip_next.value)
    else:
        scores = range(score, 100)
    misses = range(1, score)

    buffs = [b for bs in buffs_.values() for b in (bs if isinstance(bs, list) else [bs])]
    totals = collections.defaultdict(lambda: Fraction(0, 1))
    for reroll_chance, rerolls in ((Fraction(1, 1), reroll.values), (Fraction(reroll.value, 6), ())):
        for i in range(1, 7):
            raw = i
            if i in rerolls:
                continue
            i = max(i + modifier, 1)
            for buff in buffs:
                if i in buff.values:
                    totals[type(buff)] += reroll_chance * Fraction(1, 6)
            if raw == 1 or i in misses:
                totals['misses'] += reroll_chance * Fraction(1, 6)
            elif i in scores:
                totals[Score] += reroll_chance * Fraction(1, 6)
    return dict(totals)


def additive_damage(*damages):
    totals = collections.defaultdict(int)
    totals[0] = Fraction(1, 1)
    yield totals
    for damage in damages:
        new_totals = collections.defaultdict(int)
        for d1, c1 in damage.items():
            for d2, c2 in totals.items():
                new_totals[d1 + d2] += c1 * c2
        totals = new_totals
        yield totals


def damage(*buffs):
    buffs_ = read_buffs(buffs)
    damage = {
        buffs_.pop(Damage, Damage(0)).value: Fraction(1, 1)
    }
    dice = [c for d in buffs_.get(Dice, []) for c in d.chances]
    damages = additive_damage(damage, *dice)
    return {
        Attacks: buffs_.get(Attacks, Attacks(1)).value,
        'damage': next(tail(1, damages))
    }


def binomial(n, k):
    a, b = sorted((k, n - k))
    return int(
        functools.reduce(operator.mul, range(b + 1, n + 1), 1) / functools.reduce(operator.mul, range(1, a + 1), 1))


def _attack_(phase, hit):
    hits = hit.pop(Score)
    phase = {k: hits * v for k, v in phase.items()}
    phase[Score] += hit.pop(SkipNext, 0)
    for k, v in phase.items():
        hit[k] = hit.get(k, 0) + v


def _multiply(bonus, dict):
    return {k: bonus * v + v for k, v in dict.items()}


def chances(hit, miss, size):
    for i in range(size + 1):
        bin = binomial(size, i)
        yield (hit ** i * miss ** (size - i)) * bin


def attack_(*phases):
    hit, wound, save, damage, fnp, *_ = (*phases, None, None, None, None)
    hit['misses'] = {
        'hit': hit['misses']
    }

    if wound is not None:
        hit['misses']['wound'] = wound.pop('misses') * hit[Score]
        _attack_(wound, hit)

    if save is not None:
        hit['misses']['save'] = save.pop(Score) * hit[Score]
        save[Score] = save.pop('misses')
        _attack_(save, hit)

    if damage is not None:
        hit_chance = hit.pop(Score)
        miss_chance = sum(hit['misses'].values())
        attacks = damage.pop(Attacks, 1)
        total_damage = collections.defaultdict(int)
        damages = additive_damage(*[damage['damage']] * (attacks + 1))
        values = zip(chances(hit_chance, miss_chance, attacks), damages)
        next(values, None)
        for chance, damage in values:
            for k, v in damage.items():
                total_damage[k] += chance * v
        hit['damage'] = total_damage

    if fnp is not None:
        pass
        # fnp[Score], fnp['misses'] = fnp['misses'], fnp[Score]
        # _attack_(save, hit)

    bonus_attacks = hit.pop(BonusAttack, 0)
    misses = hit.pop('misses')
    damage = hit.pop('damage', None)
    hit = _multiply(bonus_attacks, hit)
    hit['misses'] = _multiply(bonus_attacks, misses)
    if damage is not None:
        hit['damage'] = _multiply(bonus_attacks, damage)
    return hit


def plot(value):
    fig, axes = plt.subplots(2, 2, figsize=(20, 20))
    df = pd.DataFrame(
        [float(value['misses'].get(k, 0)) for k in 'hit wound save'.split()],
        columns=['Score'],
        index=['Failed Hit', 'Failed Wound', 'Failed Save']
    )
    df.plot.bar(stacked=True, ax=axes[0][0]).set_ylim(0, 0.5)

    top = max(value['damage'].keys())
    data = [value['damage'].get(i, 0) for i in range(1, top + 1)]
    df = pd.DataFrame(
        [float(i) for i in data],
        columns=['Score'],
        index=list(range(1, top + 1))
    )
    df.plot.bar(stacked=True, ax=axes[0][1]).set_ylim(0, 0.5)

    df = pd.DataFrame(
        [float(i) for i in itertools.accumulate(data)],
        columns=['Score'],
        index=list(range(1, top + 1))
    )
    df.plot.bar(stacked=True, ax=axes[1][0]).set_ylim(0, 1)

    df = pd.DataFrame(
        [float(i) for i in reversed(list(itertools.accumulate(reversed(data))))],
        columns=['Score'],
        index=list(range(1, top + 1))
    )
    df.plot.bar(stacked=True, ax=axes[1][1]).set_ylim(0, 1)


class Unit:
    pass


class Weapon:
    pass


if __name__ == '__main__':
    lemon = attack_(
        phase(Score(2), Reroll(1)),
        phase(Score(4)),
        phase(Score(4)),
        damage(Attacks(32 // 2), Damage(2))
    )
    # plot(lemon)
    lemon = attack_(
        phase(Score(3), Reroll(1)),
        phase(Score(4)),
        phase(Score(4)),
        damage(Attacks(8), Damage(2))
    )
    # plot(lemon)
    lemon = attack_(
        phase(Score(3), Reroll(1)),
        phase(Score(3)),
        phase(Score(5)),
        damage(Attacks(8), Dice())
    )
    # plot(lemon)
    lemon = attack_(
        phase(Score(3), BonusAttack(6)),
        phase(Score(5)),
        phase(Score(3)),
        damage(Attacks(151), Damage(1))
    )
    plot(lemon)

    # Mortarion
    mortarion = attack_(
        phase(Score(2), Reroll(1), Modifier(1), BonusAttack(6)),
        phase(Score(3), Reroll(1), Modifier(1), MortalWound(7)),
        phase(Score(3), Modifier(-3)),
        damage(Attacks(6), Dice())
    )
    # plot(mortarion)
    print()
    # Tzangor
    print(
        'Tzangor',
        attack_(
            phase(Score(3), Reroll(1), Modifier(1), Modifier(1), SkipNext(6)),
            phase(Score(3))
        )
    )
    print()
    # Plasma
    print('Plasma', attack_(phase(Score(3), SelfWound(1)), phase(Score(3))))
    print('Plasma save', attack_(phase(Score(3), SelfWound(1)), phase(Score(3)), phase(Score(3))))
    print('Plasma damage', attack_(phase(Score(3), SelfWound(1)), phase(Score(3)), phase(Score(3)), damage(Damage(2))))
    print('Plasma fnp', attack_(phase(Score(3), SelfWound(1)), phase(Score(3)), phase(Score(3)), damage(Damage(2)),
                                phase(Score(5), Reroll(1))))
