from core.voting_rules import CompleteProfileBordaSolver, borda_name
from core.queries import CompareQuery
from core.profile_helpers import IncompleteToCompleteProfileConverter
import random


class ElicitationProtocol:
    def find_winner(self):
        return "None"

    def underlying_function(self):
        return None, 0, True

    def elicit_preferences(self, alternatives, complete_profile, voting_rule_name):
        self.elicitation_situation = {"S": voting_rule_name,
                                      "A": alternatives, "P": [set()] * len(complete_profile)}

        query_count = 0
        winner_time = False
        query_voter_list = []

        while True:
            query, voter, winner_time = self.underlying_function()
            if winner_time:
                winner = self.find_winner()
                break
            voter_preferences = complete_profile[voter]
            query_voter_list.append((str(query), str(voter)))
            response = query.elicit_from(voter_preferences)
            self.elicitation_situation["P"][voter] = self.elicitation_situation["P"][voter].union(
                response)
            query_count = query_count + 1

        return winner, query_voter_list, self.elicitation_situation["P"]


class RandomPairwiseElicitationProtocol(ElicitationProtocol):
    def find_winner(self):
        complete_profile = IncompleteToCompleteProfileConverter.convert(self.elicitation_situation["A"],
                                                                        self.elicitation_situation["P"])
        if self.elicitation_situation["S"] == borda_name:
            return CompleteProfileBordaSolver.find_winner(self.elicitation_situation["A"], complete_profile)

    def underlying_function(self):
        for alternative1 in self.elicitation_situation["A"]:
            for alternative2 in self.elicitation_situation["A"]:
                for voter_preferences in self.elicitation_situation["P"]:
                    if alternative1 != alternative2:
                        if not (((alternative1, alternative2) in voter_preferences) or ((alternative2, alternative1) in voter_preferences)):
                            selected_alternative1 = random.choice(
                                tuple(self.elicitation_situation["A"]))
                            selected_alternative2 = random.choice(
                                tuple(self.elicitation_situation["A"].difference(selected_alternative1)))
                            compare_query = CompareQuery(
                                selected_alternative1, selected_alternative2)
                            voter = random.randint(
                                0, len(self.elicitation_situation["P"])-1)
                            return compare_query, voter, False

        return None, 0, True
