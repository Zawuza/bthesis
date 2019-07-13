from ortools.sat.python import cp_model

borda_name = "Borda"
plurality_name = "Plurality"
veto_name = "Veto"

rules_global_dict = {}
rules_global_dict[borda_name] = borda_name


class BordaRule:

    @classmethod
    def find_single_winner(cls, alternatives, complete_profile):
        scores = dict.fromkeys(alternatives, 0)
        for voter in complete_profile:
            for i in range(len(voter)):
                scores[voter[i]] += len(voter) - i - 1
        return max(scores, key=scores.get)

    @classmethod
    def longest_chain(cls, a, b, partial_vote, alternatives):
        result_chain = [a]
        while True:
            last = result_chain[len(result_chain)-1]
            for c in alternatives:
                if ((last, c) in partial_vote) and ((c, b) in partial_vote):
                    result_chain.append(c)
            break
        return result_chain

    @classmethod
    def find_single_necessary_winner_if_exists(cls, alternatives, incomplete_profile):
        scores = list(reversed(range(len(alternatives))))
        # Compute up and down of each vote and alternative
        ups = {}
        downs = {}
        for a in alternatives:
            up = [set()] * len(incomplete_profile)
            down = [set()] * len(incomplete_profile)
            for i in range(len(incomplete_profile)):
                partial_vote = incomplete_profile[i]
                for (x, y) in partial_vote:
                    if x == a:
                        down_i = down[i].copy()
                        down_i.add(y)
                        down[i] = down_i
                    if y == a:
                        up_i = up[i].copy()
                        up_i.add(x)
                        up[i] = up_i
            ups[a] = up
            downs[a] = down
        # Compare scores of alternatives
        for a in alternatives:
            a_necessary_winner = True
            for w in alternatives:
                if a == w:
                    continue
                score_a = 0
                score_w = 0
                for i in range(len(incomplete_profile)):
                    partial_vote = incomplete_profile[i]
                    if not ((a, w) in partial_vote):  # includes "unknown"
                        score_a += scores[len(alternatives) -
                                          len(downs[a][i]) - 1]
                        score_w += scores[len(ups[w][i])]
                    else:
                        # Dirty hack!!! (for normal, see paper)
                        score_a += len(ups[w][i].intersection(downs[a][i])) + 1
                a_necessary_winner = (score_a >= score_w) & a_necessary_winner
            if not a_necessary_winner:
                continue
            else:
                return a

        return None

    @classmethod
    def is_possible_winner(cls, partial_profile, alternatives, a_star):
        model = cp_model.CpModel()
        variables = {}
        overall_score_costraints = {}

        for i in range(len(partial_profile)):

            # Model a preference
            voter_score_vars = []
            for a in alternatives:
                var_name = "score_" + a + "_" + str(i)
                var = model.NewIntVar(
                    0, len(alternatives)-1, var_name)
                variables[var_name] = var
                voter_score_vars.append(var)
            model.AddAllDifferent(voter_score_vars)

            # Add constraints for known comparisons
            voter = partial_profile[i]
            for (a, b) in voter:
                var_name1 = "score_" + a + "_" + str(i)
                var_name2 = "score_" + b + "_" + str(i)
                var1 = variables[var_name1]
                var2 = variables[var_name2]
                c = var1 - var2
                c = c > 0
                model.Add(c)

            # Add new terms to overall score constraints
            for a in alternatives:
                if a == a_star:
                    continue
                constraint_name = a + "_vs_" + a_star
                var_a_name = "score_" + a + "_" + str(i)
                var_a_star_name = "score_" + a_star + "_" + str(i)
                var_a = variables[var_a_name]
                var_a_star = variables[var_a_star_name]
                if constraint_name in overall_score_costraints:
                    ct = overall_score_costraints[constraint_name]
                    ct = ct + var_a_star - var_a
                    overall_score_costraints[constraint_name] = ct
                else:
                    overall_score_costraints[constraint_name] = var_a_star - var_a

        # Finish overall score constraints
        for name in overall_score_costraints:
            ct = overall_score_costraints[name]
            ct = ct >= 0
            model.Add(ct)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if (status == cp_model.FEASIBLE) or (status == cp_model.OPTIMAL):
            return True
        else:
            return False
