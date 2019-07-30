import random

import numpy as np

from core.voting_rules import BordaRule, rules_global_dict, borda_name, plurality_name, veto_name
from core.queries import CompareQuery
from core.profile_helpers import IncompleteToCompleteProfileConverter
from core.completiongen import CompletionsGenerator


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

    def find_all_possible_pairs(self):
        possible_pairs = []
        for i in range(len(self.elicitation_situation["P"])):
            voter = self.elicitation_situation["P"][i]
            for a in self.elicitation_situation["A"]:
                for b in self.elicitation_situation["A"]:
                    if a == b:
                        continue
                    if (not (a, b) in voter) and (not (b, a) in voter):
                        possible_pairs.append((i, (a, b)))
        return possible_pairs

    def elicit_preferences(self, alternatives, complete_profile, voting_rule):
        self.elicitation_situation = {"S": voting_rule,
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
        maybe_winner = self.elicitation_situation["S"].find_single_necessary_winner_if_exists(
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

            possible_winners = set()
            for a in self.elicitation_situation["A"]:
                if self.elicitation_situation["S"].is_possible_winner(
                        self.elicitation_situation["P"], self.elicitation_situation["A"], a):
                    possible_winners.add(a)
            return CompareQuery(a1, a2), voter, False, random.sample(possible_winners, 1)[0]
        else:
            return None, 0, True, maybe_winner


class AbstractCurrentSolutionHeuristicProtocol(ElicitationProtocol):

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

    def calculate_borda_pmr(self, a, w, incomplete_profile):
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

    def calculate_plurality_pmr(self, a, w, incomplete_profile):
        pmr = 0
        for vote in incomplete_profile:
            top = ""
            comparsions_count = dict.fromkeys(
                self.elicitation_situation["A"], 0)
            for (a1, a2) in vote:
                comparsions_count[a1] += 1
            for a1 in self.elicitation_situation["A"]:
                if comparsions_count[a1] == (len(self.elicitation_situation) - 1):
                    top = a1

            if top == a:
                pmr -= 1
            elif top == w:
                pmr += 1
            elif top == "":
                w_is_possible_top = True
                for a1 in self.elicitation_situation["A"]:
                    if (a1, w) in vote:
                        w_is_possible_top = False
                if w_is_possible_top:
                    pmr += 1

        return pmr

    def calculate_veto_pmr(self, a, w, incomplete_profile):
        pmr = 0
        for vote in incomplete_profile:
            bottom = ""
            beats_counts = dict.fromkeys(
                self.elicitation_situation["A"], 0)
            for (a1, a2) in vote:
                beats_counts[a2] += 1
            for a1 in self.elicitation_situation["A"]:
                if beats_counts[a1] == (len(self.elicitation_situation) - 1):
                    bottom = a1

            if bottom == w:
                pmr = - 1
            elif bottom == a:
                pmr += 1
            elif bottom == "":
                a_is_possible_bottom = True
                for a1 in self.elicitation_situation["A"]:
                    if (a, a1) in vote:
                        a_is_possible_bottom = False
                pmr += 1

        return pmr

    def calculate_pairwise_maximal_regret(self, a, w, incomplete_profile):
        if self.elicitation_situation["S"].name() == borda_name:
            pmr = self.calculate_borda_pmr(a, w, incomplete_profile)
        elif self.elicitation_situation["S"].name() == plurality_name:
            pmr = self.calculate_plurality_pmr(a, w, incomplete_profile)
        elif self.elicitation_situation["S"].name() == veto_name:
            pmr = self.calculate_veto_pmr(a, w, incomplete_profile)
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
        return 0, CompareQuery("a", "b")

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
            count = 0
            voter_preferences = voter_preferences = self.elicitation_situation["P"][i]
            for a in self.elicitation_situation["A"]:
                for b in self.elicitation_situation["A"]:
                    if a == b:
                        continue
                    if ((a, b) not in voter_preferences) and ((b, a) not in voter_preferences):
                        count += 1
            if count > max_count:
                max_count = count
                max_i = i
        voter = max_i

        voter_preferences = self.elicitation_situation["P"][max_i]
        possible_pairs = []
        for a in self.elicitation_situation["A"]:
            for b in self.elicitation_situation["A"]:
                if a == b:
                    continue
                if ((a, b) not in voter_preferences) and ((b, a) not in voter_preferences):
                    possible_pairs.append((a, b))

        scores = []
        for pair in possible_pairs:
            max_diff = -1
            for dimension in range(len(alt_matrix)):
                a, b = pair
                index_a = alt_list.index(a)
                index_b = alt_list.index(b)
                diff = abs(alt_matrix[dimension][index_a] -
                           alt_matrix[dimension][index_b])
                if diff > max_diff:
                    max_diff = diff
            scores.append((max_diff, pair))
        best = max(scores)
        best_pair = best[1]
        best_a, best_b = best_pair

        return CompareQuery(best_a, best_b), voter

    def underlying_function(self):
        alternatives_list = list(self.elicitation_situation["A"])
        n = len(alternatives_list)
        m = len(self.elicitation_situation["P"])
        matrix = np.full((m, n), np.nan)
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
            matrix, 1, 0.1)
        complete_profile = self.reconstruct_profile(
            voter_matrix, alternative_matrix, alternatives_list)
        maybe_winner = self.elicitation_situation["S"].find_single_necessary_winner_if_exists(
            self.elicitation_situation["A"], self.elicitation_situation["P"])
        if maybe_winner == None:
            winner = self.elicitation_situation["S"].find_single_winner(
                self.elicitation_situation["A"], complete_profile)
            query, voter = self.find_best_query(
                matrix, voter_matrix, alternative_matrix, alternatives_list)
            stop = False
        else:
            query = None
            voter = None
            winner = maybe_winner
            stop = True
        return query, voter, stop, winner


class CurrentSolutionHeuristicProtocol(AbstractCurrentSolutionHeuristicProtocol):

    def find_most_promising_query(self, a_star, w):
        query_score_pairs = []

        for voter_index, pair in self.find_all_possible_pairs():
            partial_profile = self.elicitation_situation["P"].copy()
            prefs = partial_profile[voter_index].copy()
            prefs.add(pair)
            partial_profile[voter_index] = prefs
            # Transitivity
            for x in self.elicitation_situation["A"]:
                for y in self.elicitation_situation["A"]:
                    for z in self.elicitation_situation["A"]:
                        if ((x, y) in partial_profile[voter_index]) and \
                            ((y, z) in partial_profile[voter_index]) and \
                                (not (x, z) in partial_profile[voter_index]):
                            comparison = set()
                            comparison.add((x, z))
                            partial_profile[voter_index] = partial_profile[voter_index].union(
                                comparison)

            pmr1, w = self.calculate_max_regret(a_star)

            partial_profile = self.elicitation_situation["P"].copy()
            prefs = partial_profile[voter_index].copy()
            pair = (pair[1], pair[0])
            prefs.add(pair)
            partial_profile[voter_index] = prefs
            # Transitivity
            for x in self.elicitation_situation["A"]:
                for y in self.elicitation_situation["A"]:
                    for z in self.elicitation_situation["A"]:
                        if ((x, y) in partial_profile[voter_index]) and \
                            ((y, z) in partial_profile[voter_index]) and \
                                (not (x, z) in partial_profile[voter_index]):
                            comparison = set()
                            comparison.add((x, z))
                            partial_profile[voter_index] = partial_profile[voter_index].union(
                                comparison)

            pmr2, w = self.calculate_max_regret(a_star)
            query_score_pairs.append(
                (voter_index, pair, max(pmr1, pmr2)))

        voter_i, pair, min_pmr = min(
            query_score_pairs, key=lambda pair: pair[2])
        a, b = pair
        return voter_i, a, b


class RegertMadness(AbstractCurrentSolutionHeuristicProtocol):

    def find_most_promising_query_for_borda(self, a_star, w):
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

    def find_most_promising_query_for_plurality(self, a_star, w):
        maxvote = 0
        maxpotential = 0
        maxpotential1 = ""
        maxpotential2 = ""
        for i in range(len(self.elicitation_situation["P"])):
            vote = self.elicitation_situation["P"][i]
            potential = 0
            potential1 = ""
            potential2 = ""
            # Find whether a and w are necessary/possible tops
            w_possible_top = True
            w_necessary_top = False
            w_comps = 0
            a_star_possible_top = True
            a_star_necessary_top = False
            a_star_comps = 0
            for (a, b) in vote:
                if b == a_star:
                    a_star_possible_top = False
                if b == w:
                    w_possible_top = False
                if a == a_star:
                    a_star_comps += 1
                if a == w:
                    w_comps += 1
            if a_star_comps == (len(self.elicitation_situation["A"])-1):
                a_star_necessary_top = True
            if w_comps == (len(self.elicitation_situation["A"])-1):
                w_necessary_top = True

            # If we can show that w is not necessary top, we can reduce regret
            if w_possible_top and not w_necessary_top:
                potential += 1
            # If we can show that a_star is necessary top, we can reduce regret
            if a_star_possible_top and not a_star_necessary_top:
                potential += 1

            # Find a query
            if (not (a_star, w) in vote) and (not (w, a_star) in vote):
                potential1 = a_star
                potential2 = w
            else:
                if a_star_possible_top:
                    for a in self.elicitation_situation["A"]:
                        if a == a_star:
                            continue
                        if not ((a_star, a) in vote):
                            potential1 = a_star
                            potential2 = a
                            break
                else:
                    for a in self.elicitation_situation["A"]:
                        if w == a:
                            continue
                        if (not ((a, w) in vote)) and (not ((w, a) in vote)):
                            potential1 = w
                            potential2 = a
                            break

            if potential > maxpotential:
                maxpotential = potential
                maxvote = i
                maxpotential1 = potential1
                maxpotential2 = potential2

        return maxvote, maxpotential1, maxpotential2

    def find_most_promising_query_for_veto(self, a_star, w):
        maxvote = 0
        maxpotential = 0
        maxpotential1 = ""
        maxpotential2 = ""

        for i in range(len(self.elicitation_situation["P"])):
            vote = self.elicitation_situation["P"][i]
            potential = 0
            potential1 = ""
            potential2 = ""

            # Find whether a and w are necessary/possible bottoms
            w_possible_bottom = True
            w_necessary_bottom = False
            w_beaten = 0
            a_star_possible_bottom = True
            a_star_necessary_bottom = False
            a_star_beaten = 0
            for (a, b) in vote:
                if a == a_star:
                    a_star_possible_bottom = False
                if a == w:
                    w_possible_bottom = False
                if b == a_star:
                    a_star_beaten += 1
                if b == w:
                    w_beaten += 1
            if a_star_beaten == (len(self.elicitation_situation["A"])-1):
                a_star_necessary_bottom = True
            if w_beaten == (len(self.elicitation_situation["A"])-1):
                w_necessary_bottom = True

            # If we can show later that a_star isn't necessary bottom, we can reduce regret
            if a_star_possible_bottom and not a_star_necessary_bottom:
                potential += 1
            # If we can show later that w is necessary bottom, we can reduce regret
            if w_possible_bottom and not w_necessary_bottom:
                potential += 1

            # Decide which query
            if (not (a_star, w) in vote) and (not (w, a_star) in vote):
                potential1 = a_star
                potential2 = w
            else:
                if w_possible_bottom:
                    for a in self.elicitation_situation["A"]:
                        if a == w:
                            continue
                        if not ((a, w) in vote):
                            potential1 = w
                            potential2 = a
                            break
                else:
                    for a in self.elicitation_situation["A"]:
                        if a == a_star:
                            continue
                        if (not ((a, a_star) in vote)) and (not ((a_star, a) in vote)):
                            potential1 = a_star
                            potential2 = a
                            break

            if potential > maxpotential:
                maxpotential = potential
                maxvote = i
                maxpotential1 = potential1
                maxpotential2 = potential2

        return maxvote, maxpotential1, maxpotential2

    def find_most_promising_query(self, a_star, w):
        if self.elicitation_situation["S"].name() == borda_name:
            return self.find_most_promising_query_for_borda(a_star, w)
        elif self.elicitation_situation["S"].name() == plurality_name:
            return self.find_most_promising_query_for_plurality(a_star, w)
        elif self.elicitation_situation["S"].name() == veto_name:
            return self.find_most_promising_query_for_veto(a_star, w)


class CompletionSamplingElicitationProtocol(ElicitationProtocol):

    def __init__(self):
        self.gen = CompletionsGenerator(0.14, 0.14)

    def calculate_distribution(self, partial_profile, alternative_list):
        completions = self.gen.generate_completions(
            partial_profile, self.elicitation_situation["A"])
        distribution = np.asarray([0] * len(alternative_list))
        for completion in completions:
            winner = self.elicitation_situation["S"].find_single_winner(
                self.elicitation_situation["A"], completion)
            distribution[alternative_list.index(winner)] += 1
        np.divide(distribution, len(completions))
        return distribution

    def calculate_kf_d(self, distribution1, distribution2):
        sum = 0
        distribution1[1] = 0
        for i in range(distribution1.size):
            d1_zero = np.isclose(distribution1[i], 0)
            d2_zero = np.isclose(distribution2[i], 0)
            if not d1_zero and not d2_zero:
                sum += distribution1[i] * \
                    np.log(distribution1[i]/distribution2[i])
            elif not d1_zero and d1_zero:
                sum += distribution1[i] * np.log(distribution1[i]/0.0001)
            elif d1_zero and not d2_zero:
                sum += distribution1[i] * np.log(0.0001/distribution2[i])
            elif d1_zero and d2_zero:
                sum += 0
        return sum

    def calculate_jsd(self, distribution1, distribution2):
        m_distribution = np.multiply(np.add(distribution1, distribution2), 0.5)
        jsd = 0.5 * self.calculate_kf_d(distribution1, m_distribution) + \
            0.5 * self.calculate_kf_d(distribution2, m_distribution)
        return jsd

    def find_best_query(self, current_distribution, alternative_list):
        query_score_pairs = []

        for voter_index, pair in self.find_all_possible_pairs():
            partial_profile = self.elicitation_situation["P"].copy()
            prefs = partial_profile[voter_index].copy()
            prefs.add(pair)
            partial_profile[voter_index] = prefs
            # Transitivity
            for x in self.elicitation_situation["A"]:
                for y in self.elicitation_situation["A"]:
                    for z in self.elicitation_situation["A"]:
                        if ((x, y) in partial_profile[voter_index]) and \
                            ((y, z) in partial_profile[voter_index]) and \
                                (not (x, z) in partial_profile[voter_index]):
                            comparison = set()
                            comparison.add((x, z))
                            partial_profile[voter_index] = partial_profile[voter_index].union(
                                comparison)

            new_distribution = self.calculate_distribution(
                partial_profile, alternative_list)
            jsd_distance = self.calculate_jsd(
                current_distribution, new_distribution)
            query_score_pairs.append((voter_index, pair, jsd_distance))

        voter_i, pair, jsd = max(
            query_score_pairs, key=lambda pair: pair[2])
        a, b = pair
        return CompareQuery(a, b), voter_i

    def underlying_function(self):
        nec_winner = self.elicitation_situation["S"] \
            .find_single_necessary_winner_if_exists(self.elicitation_situation["A"],
                                                    self.elicitation_situation["P"])
        if nec_winner == None:
            alternatives = list(self.elicitation_situation["A"])
            distribution = self.calculate_distribution(
                self.elicitation_situation["P"], alternatives)
            query, voter = self.find_best_query(
                distribution, alternatives)
            winner = alternatives[np.argmax(distribution)]
            return query, voter, False, winner
        else:
            return None, 0, True, nec_winner


class IterativeVotingElicitationProtocol(ElicitationProtocol):

    def __init__(self):
        self.state = (0, 1)

    def state_finished(self):
        voter, position = self.state
        required_comparsions = len(self.elicitation_situation["A"]) - position
        vote = self.elicitation_situation["P"][voter]
        comparsions = {}
        for (a, b) in vote:
            if a in comparsions:
                comparsions[a] += 1
            else:
                comparsions[a] = 1
        found = False
        for a in comparsions:
            found = found or (comparsions[a] == required_comparsions)
        return found

    def find_best_query(self):
        voter, position = self.state
        required_comparsions = len(self.elicitation_situation["A"]) - position
        vote = self.elicitation_situation["P"][voter]
        comparsions = {}
        for (a, b) in vote:
            if a in comparsions:
                comparsions[a] += 1
            else:
                comparsions[a] = 1
        max_count = -1
        max_a = ""
        for a in self.elicitation_situation["A"]:
            if a in comparsions:
                count = comparsions[a]
            else:
                count = 0
            if (count > max_count) and (count < required_comparsions):
                max_count = count
                max_a = a

        unknown = self.elicitation_situation["A"].copy()
        unknown.remove(max_a)
        for (a, b) in vote:
            if (a == max_a):
                unknown.remove(b)
            if (b == max_a):
                unknown.remove(a)

        return CompareQuery(max_a, random.sample(unknown, 1)[0]), voter

    def underlying_function(self):
        nec_winner = self.elicitation_situation["S"]. \
            find_single_necessary_winner_if_exists(self.elicitation_situation["A"],
                                                   self.elicitation_situation["P"])

        if nec_winner == None:
            while self.state_finished():
                voter, position = self.state
                voter += 1
                if voter > (len(self.elicitation_situation["P"])-1):
                    voter = 0
                    position += 1
                self.state = (voter, position)
            query, voter = self.find_best_query()

            possible_winners = set()
            for a in self.elicitation_situation["A"]:
                if self.elicitation_situation["S"].is_possible_winner(
                        self.elicitation_situation["P"], self.elicitation_situation["A"], a):
                    possible_winners.add(a)

            return query, voter, False, random.sample(possible_winners, 1)[0]
        else:
            self.state = (0, 1)
            return None, 0, True, nec_winner


elicitation_protocols_global_dict = {}
elicitation_protocols_global_dict["random_pairwise"] = RandomPairwiseElicitationProtocol
elicitation_protocols_global_dict["current_solution_heuristic"] = CurrentSolutionHeuristicProtocol
elicitation_protocols_global_dict["regret_madness"] = RegertMadness
elicitation_protocols_global_dict["matrix_factorization"] = MatrixFactorizationElicitationProtocol
elicitation_protocols_global_dict["completion_sampling"] = CompletionSamplingElicitationProtocol
elicitation_protocols_global_dict["iterative_voting"] = IterativeVotingElicitationProtocol
