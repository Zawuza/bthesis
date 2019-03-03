class CompareQuery:
    def __init__(self, a, b):
        if a == b:
            raise Exception("CompareQuery with equal alternatives!")
        self.a = a
        self.b = b

    def __str__(self):
        return "compare{" + self.a + "," + self.b + "}"

    def elicit_from(self, voter_preferences):
        for alternative in voter_preferences:
            if alternative == self.a:
                return {(self.a, self.b)}
            if alternative == self.b:
                return {(self.b, self.a)}
        raise Exception(
            "Wrong preferences: no corresponding alternitave in a query")
