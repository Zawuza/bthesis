import random

import numpy as np

from core.voting_rules import CompleteProfileBordaSolver, borda_name, IncompleteProfileBordaSolver
from core.queries import CompareQuery
from core.profile_helpers import IncompleteToCompleteProfileConverter


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


class MatrixFactorizationElicitationProtocol(ElicitationProtocol):

    def stochastic_gradient(self, matrix, feature_count, learning_rate):
        m, n = matrix.shape
        voter_matrix = np.random.rand(m, feature_count)
        alternative_matrix = np.random.rand(feature_count, n)
        for _ in range(m*n*1000):
            i = np.random.randint(m)
            j = np.random.randint(n)
            if np.isnan(matrix[i][j]):
                continue
            approximate = 0
            for k in range(feature_count):
                approximate += voter_matrix[i][k] * alternative_matrix[k][j]
            error = matrix[i][j] - approximate
            for k in range(feature_count):
                voter_matrix[i][k] = voter_matrix[i][k] + 2 * \
                    learning_rate*alternative_matrix[k][j]*error
                alternative_matrix[k][j] = alternative_matrix[k][j] + \
                    2*learning_rate*voter_matrix[i][k]*error

        return voter_matrix, alternative_matrix

    def reconstruct_profile(self, voter_matrix, alternative_matrix, alternatives):
        complete_matrix = np.dot(voter_matrix, alternative_matrix)
        complete_profile = []
        for row in complete_matrix:
            indices = np.argsort(row)
            vote = []
            for i in indices:
                vote.insert(0, alternatives[i])
            complete_profile.append(vote)
        return complete_profile

    def find_best_query(self, full_matrix, voter_matrix, alt_matrix, alt_list):
        max_i = -1
        max_count = -1
        for i in range(len(full_matrix)):
            row = full_matrix[i]
            count = row.count(np.nan)
            if max_count < count:
                max_i = i
                max_count = count
        voter = max_i

        voter_preferences = self.elicitation_situation["P"][max_i]
        possible_pairs = []
        for a in self.elicitation_situation["A"]:
            for b in self.elicitation_situation["A"]:
                if a == b:
                    continue
                if ((a,b) not in voter_preferences) and ((a,b) not in voter_preferences):
                    possible_pairs.append((a,b))

        scores = [] 
        for pair in possible_pairs:
            max_diff = -1
            for dimension in range(len(alt_matrix)):
                a,b = pair
                index_a = alt_list.index(a)
                index_b = alt_list.index(b)
                diff = abs(alt_matrix[dimension][index_a] - alt_matrix[dimension][index_b])
                if diff > max_diff:
                    max_diff = diff
            scores.append((max_diff, pair))
        best = max(scores)
        best_pair = best[1]
        best_a, best_b = best_pair

        return CompareQuery(best_a, best_b), max_i

    def underlying_function(self):
        alternatives_list = list(self.elicitation_situation["A"])
        n = len(alternatives_list)
        m = len(self.elicitation_situation["P"])
        matrix = np.zeros((m, n))
        for i in range(len(self.elicitation_situation["P"])):
            voter = self.elicitation_situation["P"][i]
            for (a, b) in voter:
                j = alternatives_list.index(a)
                if np.isnan(matrix[i, j]):
                    matrix[i, j] = 1
                else:
                    matrix[i, j] += 1
                if np.isnan(matrix[i, j]):
                    matrix[i, alternatives_list.index(b)] = 0
        voter_matrix, alternative_matrix = self.stochastic_gradient(
            matrix, 1, 0.01)
        complete_profile = self.reconstruct_profile(
            voter_matrix, alternative_matrix, alternatives_list)
        maybe_winner = IncompleteProfileBordaSolver.find_necessary_winner_if_exists(
            self.elicitation_situation["A"], self.elicitation_situation["P"])
        if maybe_winner == None:
            winner = CompleteProfileBordaSolver.find_winner(
                self.elicitation_situation["A"], complete_profile)
            query, voter = self.find_best_query(matrix, voter_matrix, alternative_matrix, alternatives_list)
            stop = False
        else:
            winner = maybe_winner
            stop = True
        return query, voter, stop, winner


elicitation_protocols_global_dict = {}
elicitation_protocols_global_dict["random_pairwise"] = RandomPairwiseElicitationProtocol
elicitation_protocols_global_dict["current_solution_heuristic"] = CurrentSolutionHeuristicProtocol
elicitation_protocols_global_dict["matrix_factorization"] = MatrixFactorizationElicitationProtocol
