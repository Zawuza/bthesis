from ortools.sat.python import cp_model
import ortools as ort


class PossibleBordaWinnerFinder:

    @classmethod
    def is_possible_winner(cls, partial_profile, alternatives, a_star):
        model = cp_model.CpModel()
        variables = {}
        final_constraint = ''
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
                ct = c > 0
                model.Add(ct)

        return True


print(PossibleBordaWinnerFinder.is_possible_winner(
    [set(), set(), {("a", "b")}], {"a", "b"}, "b"))
