from core.voting_rules import borda_name
from core.experiment import Experiment
from core.elicitation_protocols import RandomPairwiseElicitationProtocol
from core.output_writers import save_result_to_file


profile1 = [["a", "h"], ["h", "a"], ["h", "a"]]
alternatives1 = {"a", "h"}

profile2 = [["a", "b", "c"], ["a", "b", "c"], ["a", "c", "b"]]
alternatives2 = {"a", "b", "c"}

profile3 = [["a", "b", "c"], ["c", "b", "a"], ["b", "a", "c"], ["a", "b", "c"]]
alternatives3 = {"a", "b", "c"}

profile4 = [["lol", "kek"]]
alternatives4 = {"lol", "kek"}

profile5 = [["knowledge_graph", "ship", "satellite", "image_recognition", "wine_quality", "wikipedia_visualisation"],
            ["satellite", "wine_quality", "image_recognition",
                "ship", "knowledge_graph", "wikipedia_visualisation"],
            ["knowledge_graph", "wikipedia_visualisation", "ship", "satellite", "wine_quality", "image_recognition"]]
alternatives5 = {"knowledge_graph", "wikipedia_visualisation",
                 "ship", "satellite", "wine_quality", "image_recognition"}

profile6 = [["train", "bus", "airplane", "walk"],
            ["bus", "airplane", "train", "walk"],
            ["airplane", "train", "bus", "walk"]]
alternatives6 = {"train", "bus", "airplane", "walk"}

profile7 = [["ios", "windows", "android"],
            ["android", "windows", "ios"],
            ["windows", "ios", "android"]]
alternatives7 = {"ios", "windows", "android"}

# Build dataset
alternatives = [alternatives1, alternatives2, alternatives3,
                alternatives4, alternatives5, alternatives6, alternatives7]
profiles = [(1, profile1), (2, profile2), (3, profile3),
            (4, profile4), (5, profile5), (6, profile6), (7, profile7)]

random_pairwise = RandomPairwiseElicitationProtocol()
test_experiment = Experiment(
    alternatives, profiles, borda_name, random_pairwise, save_result_to_file)
test_experiment.execute()
