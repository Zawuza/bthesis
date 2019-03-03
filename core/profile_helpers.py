class IncompleteToCompleteProfileConverter:
    @classmethod
    def convert(cls, alternatives, incomplete_profile):
        complete_profile = []
        for voter in incomplete_profile:
            places = dict.fromkeys(alternatives, 0)
            for (a1, a2) in voter:
                places[a1] = places[a1] + 1
            complete_voter = [""] * len(alternatives)
            for key in places:
                complete_voter[len(complete_voter) - places[key] - 1] = key
            complete_profile.append(complete_voter)
        return complete_profile
