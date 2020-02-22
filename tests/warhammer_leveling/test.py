from dataclasses import asdict
from pprint import pprint

from warhammer import ExtUpgrade

data = """[
  {
    "name": "Bike",
    "requirements": {
      "rank": 1,
      "upgrades": ["!ANY", "~Champion"]
    },
    "bonus": "14 ... +1 +1 ........",
    "equipment": {
      "this": [],
      "merge": {}
    },
    "abilities": ["6Adv"],
    "keywords": ["-INFANTRY", "+BIKER"]
  },
  {
    "name": "Champion",
    "requirements": {
      "rank": 1,
      "upgrades": []
    },
    "bonus": "...... +1 +1 ......",
    "equipment": {
      "this": ["Champion Equipment", "frag grenades", "krak grenades"],
      "merge": {}
    },
    "abilities": [],
    "keywords": []
  },
  {
    "name": "Heavy",
    "requirements": {
      "rank": 1,
      "upgrades": ["!ANY", "~Champion"]
    },
    "bonus": "..............",
    "equipment": {
      "this": [],
      "merge": {}
    },
    "abilities": [],
    "keywords": []
  },
  {
    "name": "Jump Pack",
    "requirements": {
      "rank": 1,
      "upgrades": ["!ANY", "~Champion"]
    },
    "bonus": "12 .............",
    "equipment": {
      "this": [],
      "merge": {}
    },
    "abilities": ["DS(Jump Pack)"],
    "keywords": ["-INFANTRY", "+JUMP PACK", "+FLY"]
  },
  {
    "name": "Psyker",
    "requirements": {
      "rank": 1,
      "upgrades": ["!ANY", "Champion", "~Terminator Armour"]
    },
    "bonus": "........... +1 +1 +1",
    "equipment": {
      "this": [],
      "merge": {}
    },
    "abilities": [],
    "keywords": ["+PSYKER"]
  },
  {
    "name": "Terminator Armour",
    "requirements": {
      "rank": 2,
      "upgrades": ["!ANY", "~Champion", "~Psyker"]
    },
    "bonus": "-1 .... +1 .. -1 5 ....",
    "equipment": {
      "this": [],
      "merge": {}
    },
    "abilities": ["DS(Teleport Strike)"],
    "keywords": ["+TERMINATOR"]
  }
]"""


if __name__ == "__main__":
    upgrades = [asdict(u.build()) for u in ExtUpgrade.schema().loads(data, many=True)]
    pprint(upgrades)
