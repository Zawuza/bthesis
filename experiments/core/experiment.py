class Experiment:
    def __init__(self, alternatives_for_profiles, complete_profiles, voting_rule_name, elicitation_protocol, postprocessingfunc):
        self.complete_profiles = complete_profiles
        self.voting_rule_name = voting_rule_name
        self.elicitation_protocol = elicitation_protocol
        self.alternatives_for_profiles = alternatives_for_profiles
        self.postprocessingfunc = postprocessingfunc

    def execute(self):
        for i in range(len(self.complete_profiles)):
            complete_profile = self.complete_profiles[i]
            alternatives = self.alternatives_for_profiles[i]
            result = self.elicitation_protocol.elicit_preferences(alternatives, complete_profile, self.voting_rule_name)
            self.postprocessingfunc(result)
