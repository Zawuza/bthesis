from bthesis.core.voting_rules import borda_name
from bthesis.core.experiment import Experiment
from bthesis.core.elicitation_protocols import RandomPairwiseElicitationProtocol

alternatives = {"a","b","c"}
profile = [["a","b","c"],["a","b","c"],["a","b","c"]]

random_pairwise = RandomPairwiseElicitationProtocol()
test_experiment = Experiment(alternatives, profile,borda_name,random_pairwise)
test_experiment.execute()
print("Result:", test_experiment.result)