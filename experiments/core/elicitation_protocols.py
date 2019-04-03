from core.voting_rules import CompleteProfileBordaSolver, borda_name, IncompleteProfileBordaSolver
from core.queries import CompareQuery
from core.profile_helpers import IncompleteToCompleteProfileConverter
import random


class ElicitationProtocol:
    def find_winner(self):
        return "None"

    def underlying_function(self):
        return None, 0, True

    def infer_transitivity(self):
        for voter_index in range(len(self.elicitation_situation["P"])):
            voter = self.elicitation_situation["P"][voter_index]
            for x in self.elicitation_situation["A"]:
                for y in self.elicitation_situation["A"]:
                    for z in self.elicitation_situation["A"]:
                        if ((x, y) in voter) and ((y, z) in voter) and (not (x,z) in voter):
                            comparison = set()
                            comparison.add((x, z))
                            self.elicitation_situation["P"][voter_index] = voter.union(
                                comparison)

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
            self.infer_transitivity()
            query_count = query_count + 1

        return winner, query_voter_list, self.elicitation_situation["P"]


class RandomPairwiseElicitationProtocol(ElicitationProtocol):
    def find_winner(self):
        if self.elicitation_situation["S"] == borda_name:
            return IncompleteProfileBordaSolver.find_necessary_winner_if_exists(self.elicitation_situation["A"], self.elicitation_situation["P"])

    def underlying_function(self):
        maybe_winner = IncompleteProfileBordaSolver.find_necessary_winner_if_exists(self.elicitation_situation["A"], self.elicitation_situation["P"])
        if maybe_winner == None:   
            alternatives_list = list(self.elicitation_situation["A"]).copy()
            random.shuffle(alternatives_list)
            for alternative1 in alternatives_list:
                for alternative2 in alternatives_list:
                    indexes = list(range(len(self.elicitation_situation["P"])))
                    random.shuffle(indexes)
                    for voter_index in indexes:
                        voter_preferences = self.elicitation_situation["P"][voter_index]
                        if alternative1 != alternative2:
                            if not (((alternative1, alternative2) in voter_preferences) or ((alternative2, alternative1) in voter_preferences)):
                                compare_query = CompareQuery(
                                    alternative1, alternative2)
                                return compare_query, voter_index, False

        return None, 0, True
