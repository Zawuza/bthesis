from core.voting_rules import borda_name
from core.experiment import Experiment
from core.elicitation_protocols import RandomPairwiseElicitationProtocol



def save_result_to_file(result):
    winner = result[0]
    query_voter_list = result[1]
    elicitation_situation_profile = result[2]

    with open("results.txt", "a") as f:
        print("-------------NEXT EXPERIMENT---------------------------------------------", file=f)
        print("Winner:", winner, file=f)
        print("", file=f)
        print("Queries count:", str(len(query_voter_list)), file=f)
        print("", file=f)
        print("Queries:", file=f)
        for query_voter_pair in query_voter_list:
            print("    ", query_voter_pair, file=f)
        print("", file=f)
        print("Partial profile from the last elicitation situation:", file=f)
        for preferences in elicitation_situation_profile:
            print("    ", preferences, file=f)


profile1 = [["a", "h"], ["h", "a"], ["h", "a"]]
profile2 = [["a", "b", "c"], ["a", "b", "c"], ["a", "c", "b"]]
alternatives = [{"a","b","c"}]
profiles = [profile2]

random_pairwise = RandomPairwiseElicitationProtocol()
test_experiment = Experiment(
    alternatives, profiles, borda_name, random_pairwise, save_result_to_file)
test_experiment.execute()