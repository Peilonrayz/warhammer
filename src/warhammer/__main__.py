from . import WarhammerData

csm = WarhammerData('chaos.csm')

chaos_lord = csm.model.ChaosLord()

havocs = (
    csm.model.HavocChampion(
        csm.weapon.Boltgun,
        csm.weapon.Chainsword,
    )
    + 4*csm.model.Havoc(csm.weapon.Lascannon)
)

chaos_sm = 20*csm.model.ChaosSpaceMarine(
    csm.weapon.Boltgun,
    csm.effect.HiddenInPlainSight(),
)

print(chaos_lord)
print(havocs)
print(chaos_sm)

results = (
    chaos_sm
        .auras(chaos_lord)
        .weapons()
            .attack(havocs, distance=9)
)

results.sanitize().graph()
