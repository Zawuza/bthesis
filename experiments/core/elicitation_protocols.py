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
                        if ((x, y) in voter) and ((y, z) in voter) and (not (x, z) in voter):
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
        maybe_winner = IncompleteProfileBordaSolver.find_necessary_winner_if_exists(
            self.elicitation_situation["A"], self.elicitation_situation["P"])
        if maybe_winner == None:
            unknown_pairs_list = []
            for voter_index in range(len(self.elicitation_situation["P"])):
                voter_preferences = self.elicitation_situation["P"][voter_index]
                for alternative1 in self.elicitation_situation["A"]:
                    for alternative2 in self.elicitation_situation["A"]:
                        if alternative1 == alternative2:
                            continue
                        if not (((alternative1, alternative2) in voter_preferences) or ((alternative2, alternative1) in voter_preferences)):
                            unknown_pairs_list.append(
                                (voter_index, alternative1, alternative2))
            random_triple = random.choice(unknown_pairs_list)
            voter, a1, a2 = random_triple
            return CompareQuery(a1, a2), voter, False
        else:
            return None, 0, True


class CurrentSolutionHeuristicProtocol(ElicitationProtocol):
    def find_winner(self):
        return self.winner

    def calculate_pairwise_maximal_regret(self, a, a_, incomplete_profile):
        pmr = 0
        for vote in incomplete_profile:
            if (a, a_) in vote:
                for alternative in self.elicitation_situation["A"]:
                    if (alternative == a) or (alternative == a_):
                        continue
                    if ((a, alternative) in vote) and ((alternative, a_) in vote):
                        pmr -= 1
                pmr -= 1
            elif (a_, a) in vote:
                pmr += len(self.elicitation_situation["A"]) - 1
                for alternative in self.elicitation_situation["A"]:
                    if (alternative == a) or (alternative == a_):
                        continue
                    if ((alternative, a_) in vote) or ((a, alternative) in vote):
                        pmr -= 1
            else:
                for alternative in self.elicitation_situation["A"]:
                    if (alternative == a) or (alternative == a_):
                        continue
                    if (((alternative, a) in vote) and (not ((alternative, a_) in vote))) or\
                        (((a_, alternative) in vote) and (not ((a, alternative) in vote))) or\
                            (not (((a, alternative) in vote) or ((a_, alternative) in vote) or ((alternative, a) in vote) or ((alternative, a_) in vote))):
                        pmr += 1
                pmr += 1
        return pmr

    def calculate_max_regret(self, alternative):
        maxpmr = 0
        witness = ""
        for a in self.elicitation_situation["A"]:
            if a == alternative:
                continue
            pmr = self.calculate_pairwise_maximal_regret(
                alternative, a, self.elicitation_situation["P"])
            if pmr > maxpmr:
                maxpmr = pmr
                witness = a
        return maxpmr, witness

    def find_most_promising_query(self, a_star, w):
        maxvote = 0
        maxpotential = 0
        potential_a1 = ""
        potential_a2 = ""
        maxpotentials = ("", "")
        for vote in self.elicitation_situation["P"]:
            if (a_star, w) in vote:
                potential = 0
                for a in self.elicitation_situation["A"]:
                    if (a == a_star) or (a == w):
                        continue
                    if (((a_star, a) in vote) and (not((a, w) in vote))):
                        potential += 1
                        potential_a1 = a
                        potential_a2 = w
                    elif (((a, w) in vote) and (not((a_star, a) in vote))):
                        potential += 1
                        potential_a1 = a
                        potential_a2 = a_star
                    elif ((not((a, w) in vote)) and (not((w, a)in vote)) and (not((a, a_star) in vote)) and (not((a_star, a) in vote))):
                        potential += 1
                        if (potential_a1 == "") and (potential_a2 == ""):
                            potential_a1 = a
                            potential_a2 = a_star
            elif (w, a_star) in vote:
                potential = 0
                for a in self.elicitation_situation["A"]:
                    if (a == a_star) or (a == w):
                        continue
                    if (((w, a) in vote) and (not((a, a_star) in vote))):
                        potential += 1
                        potential_a1 = a
                        potential_a2 = a_star
                    elif (((a, a_star) in vote) and (not((w, a) in vote))):
                        potential += 1
                        potential_a1 = w
                        potential_a2 = a
                    elif ((not((a, w) in vote)) and (not((w, a)in vote)) and (not((a, a_star) in vote)) and (not((a_star, a) in vote))):
                        potential += 1
                        if (potential_a1 == "") and (potential_a2 == ""):
                            potential_a1 = a
                            potential_a2 = w
            else:
                potential = 1
                for a in self.elicitation_situation["A"]:
                    if (a == a_star) or (a == w):
                        continue
                    if (((a, a_star) in vote) and (not((a, w) in vote))):
                        potential += 1
                    elif (((w, a) in vote) and (not((a_star, a) in vote))):
                        potential += 1
                    elif ((not((a, w) in vote)) and (not((w, a)in vote)) and (not((a, a_star) in vote)) and (not((a_star, a) in vote))):
                        potential += 1
                potential_a1 = a_star
                potential_a2 = w
            if potential > maxpotential:
                maxvote = self.elicitation_situation["P"].index(vote)
                maxpotential = potential
                maxpotentials = (potential_a1, potential_a2)

        return maxvote, maxpotentials[0], maxpotentials[1]

    def underlying_function(self):
        max_regret = {}
        witnesses = {}
        for a in self.elicitation_situation["A"]:
            max_regret[a], witnesses[a] = self.calculate_max_regret(a)
        a_star = min(max_regret, key=max_regret.get)
        if max_regret[a_star] > 0:
            w = witnesses[a_star]
            v, a1, a2 = self.find_most_promising_query(a_star, w)
            return CompareQuery(a1, a2), v, False
        else:
            self.winner = a_star
            return None, 0, True
