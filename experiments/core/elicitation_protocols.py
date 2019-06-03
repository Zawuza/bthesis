from core.voting_rules import CompleteProfileBordaSolver, borda_name, IncompleteProfileBordaSolver
from core.queries import CompareQuery
from core.profile_helpers import IncompleteToCompleteProfileConverter
import random


class ElicitationProtocol:
    def underlying_function(self):
        return None, 0, True, "None"

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
        query_voter_list = []

        while True:
            query, voter, stop, winner = self.underlying_function()
            query_voter_list.append(
                (str(self.elicitation_situation["P"]), str(winner), str(query), str(voter)))
            if stop:
                break
            voter_preferences = complete_profile[voter]
            response = query.elicit_from(voter_preferences)
            self.elicitation_situation["P"][voter] = self.elicitation_situation["P"][voter].union(
                response)
            self.infer_transitivity()
            query_count = query_count + 1

        return query_voter_list


class RandomPairwiseElicitationProtocol(ElicitationProtocol):
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
            return CompareQuery(a1, a2), voter, False, None
        else:
            return None, 0, True, maybe_winner


class CurrentSolutionHeuristicProtocol(ElicitationProtocol):

    def calculate_sets(self, parial_vote, a, w):
        A, B, C, D, E, F, G, U = set(), set(), set(), set(), set(), set(), set(), set()
        for alternative in self.elicitation_situation["A"]:
            if (alternative == a) or (alternative == w):
                continue
            above_a = (alternative, a) in parial_vote
            above_w = (alternative, w) in parial_vote
            under_a = (a, alternative) in parial_vote
            under_w = (w, alternative) in parial_vote
            if above_a and (not under_w) and (not above_w):
                A.add(alternative)
            if (under_a and above_w) or (above_a and under_w):
                B.add(alternative)
            if above_a and above_w:
                C.add(alternative)
            if above_w and (not above_a) and (not under_a):
                D.add(alternative)
            if under_a and (not under_w) and (not above_w):
                E.add(alternative)
            if under_a and under_w:
                F.add(alternative)
            if under_w and (not above_a) and (not under_a):
                G.add(alternative)
            if not (above_a or above_w or under_a or under_w):
                U.add(alternative)
        return A, B, C, D, E, F, G, U

    def calculate_pairwise_maximal_regret(self, a, w, incomplete_profile):
        pmr = 0
        for vote in incomplete_profile:
            A, B, C, D, E, F, G, U = self.calculate_sets(vote, a, w)
            if (a, w) in vote:
                pmr -= len(B) + 1
            elif (w, a) in vote:
                pmr += len(self.elicitation_situation["A"]) - \
                    1 - len(C) - len(D) - len(E) - len(F)
            else:
                pmr += len(A) + len(G) + len(U) + 1
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
            A, B, C, D, E, F, G, U = self.calculate_sets(vote, a_star, w)
            if (a_star, w) in vote:
                potential = 0
                for a in self.elicitation_situation["A"]:
                    if a in E:
                        potential += 1
                        potential_a1 = a
                        potential_a2 = w
                    elif a in D:
                        potential += 1
                        potential_a1 = a
                        potential_a2 = a_star
                    elif a in U:
                        potential += 1
                        if (potential_a1 == "") and (potential_a2 == ""):
                            potential_a1 = a
                            potential_a2 = a_star
            elif (w, a_star) in vote:
                potential = 0
                for a in self.elicitation_situation["A"]:
                    if a in G:
                        potential += 1
                        potential_a1 = a
                        potential_a2 = a_star
                    elif a in A:
                        potential += 1
                        potential_a1 = w
                        potential_a2 = a
                    elif a in U:
                        potential += 1
                        if (potential_a1 == "") and (potential_a2 == ""):
                            potential_a1 = a
                            potential_a2 = w
            else:
                potential = 1  # Unknowness between a_star and w
                for a in self.elicitation_situation["A"]:
                    if (a in A) or (a in G) or (a in U):
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
            return CompareQuery(a1, a2), v, False, a_star
        else:
            return None, 0, True, a_star


elicitation_protocols_global_dict = {}
elicitation_protocols_global_dict["random_pairwise"] = RandomPairwiseElicitationProtocol
elicitation_protocols_global_dict["current_solution_heuristic"] = CurrentSolutionHeuristicProtocol
