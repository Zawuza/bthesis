class Experiment:
    def __init__(self, alternatives_for_profiles, complete_profiles, voting_rule, elicitation_protocol, postprocessingfunc):
        self.complete_profiles = complete_profiles
        self.voting_rule = voting_rule
        self.elicitation_protocol = elicitation_protocol
        self.alternatives_for_profiles = alternatives_for_profiles
        self.postprocessingfunc = postprocessingfunc

    def execute(self):
        print("Execute next experiment")
        for i in range(len(self.complete_profiles)):
            print("Process profile with index " + str(i))
            complete_profile = self.complete_profiles[i][1]
            profile_index = self.complete_profiles[i][0]
            alternatives = self.alternatives_for_profiles[i]
            result = self.elicitation_protocol.elicit_preferences(
                alternatives, complete_profile, self.voting_rule)
            self.postprocessingfunc(result, profile_index)
