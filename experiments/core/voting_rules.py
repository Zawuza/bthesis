borda_name = "Borda"

class CompleteProfileBordaSolver:

    @classmethod
    def find_winner(cls,alternatives, complete_profile):
        scores = dict.fromkeys(alternatives, 0)
        for voter in complete_profile:
            for i in range(len(voter)):
                scores[voter[i]] += len(voter) - i - 1
        return max(scores, key=scores.get)