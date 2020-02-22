from .object import builder

if __name__ == "__main__":
    test = builder.load(
        {
            "_model": "Combination",
            "lhs": {"_model": "Relative", "stat": "strength",},
            "rhs": {
                "_model": "Combination",
                "lhs": {"_model": "Constant", "value": 6,},
                "rhs": {"_model": "Dice", "amount": 1, "range": 6,},
                "operator": "+",
            },
            "operator": "+",
        }
    )
    print(test)
    # print(test.values(TestModel(Constant(1))))
