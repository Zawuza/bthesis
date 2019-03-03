class Experiment:
    def __init__(self, alternatives, complete_profile, voting_rule_name, elicitation_protocol):
        self.complete_profile = complete_profile
        self.voting_rule_name = voting_rule_name
        self.elicitation_protocol = elicitation_protocol
        self.alternatives = alternatives

    def execute(self):
        self.result = self.elicitation_protocol.elicit_preferences(self.alternatives, self.complete_profile, self.voting_rule_name)

    def save(self, dbname):
        pass
