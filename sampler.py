import math
import random


class CompletionSampler:
    def __init__(self, error_rate, answer_probability):
        self.e = error_rate
        self.b = answer_probability

    def listize(self, setvote):
        scores = {}
        for (a, b) in setvote:
            if a in scores:
                scores[a] += 1
            else:
                scores[a] = 1
            if b not in scores:
                scores[b] = 0
        for a in scores:
            for b in scores:
                if a == b:
                    continue
                else:
                    if scores[a] == scores[b]:
                        return None
        listvote = []
        for alternative, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True):
            listvote.append(alternative)
        return listvote

    def infer_transitivity(self, partial_vote, alternatives):
        for x in alternatives:
            for y in alternatives:
                for z in alternatives:
                    if ((x, y) in partial_vote) and ((y, z) in partial_vote) and (not (x, z) in partial_vote):
                        comparison = set()
                        comparison.add((x, z))
                        partial_vote = partial_vote.union(comparison)
        
        return partial_vote

    def linearize_voter(self, partial_profile, alternatives):
        pv = self.infer_transitivity(partial_profile.copy(), alternatives)
        for a in alternatives:
            for b in alternatives:
                if a == b:
                    continue
                if not (((a, b) in pv) or ((b, a) in pv)):
                    pv.add((a, b))
                    pv = self.infer_transitivity(pv, alternatives)

        return self.listize(pv)

    def sample_voter_uniformly(self, partial_voter, alternatives):
        complete_voter = self.linearize_voter(partial_voter, alternatives)
        m = len(alternatives)
        T = m ** 6
        i = 0
        for i in range(T):
            k = random.randint(1, (2 * m) - 2)
            if k <= m-1:
                index = k - 1
                if not (complete_voter[index], complete_voter[index+1]) in partial_voter:
                    complete_voter[index], complete_voter[index + 1] = \
                        complete_voter[index+1], complete_voter[index]

        return complete_voter

    def next_completion(self, partial_profile, alternatives):
        result = []
        for i in range(len(partial_profile)):
            voter = partial_profile[i]
            complete_voter = self.sample_voter_uniformly(voter, alternatives)
            result.append(complete_voter)

        return result

    def sample_completions(self, partial_profile, alternatives):
        r = math.trunc(math.log(2/self.b)/(2*(self.e ** 2) * 2))
        completion_count = r + 2
        completions = []
        print("Generate " + str(completion_count) + " completions")
        for i in range(completion_count):
            completions.append(self.next_completion(
                partial_profile, alternatives))
        return completions


sampler = CompletionSampler(0.1, 0.01)
alts = {"a", "b", "c"}
profile = [{("a", "b")}, {("b", "c")}, {("a", "c")}, {
    ("b", "a")}, {("c", "a")}, {("b", "c")}, set()]
completions = sampler.sample_completions(profile, alts)
for completion in completions:
    assert(completion[0].index("a") < completion[0].index("b"))
    assert(completion[1].index("b") < completion[1].index("c"))
    assert(completion[2].index("a") < completion[2].index("c"))
    assert(completion[3].index("b") < completion[3].index("a"))
    assert(completion[4].index("c") < completion[4].index("a"))
    assert(completion[5].index("b") < completion[5].index("c"))
    print(completion)
