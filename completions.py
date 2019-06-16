class CompletionsGenerator:

    def listize(self, setvote):
        scores = {}
        for (a,b) in setvote:
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

    def next_bit_vector(self, prev_bit_vector):
        if prev_bit_vector == []:
            return None
        next_bv = prev_bit_vector
        if prev_bit_vector[len(prev_bit_vector)-1] == False:
            next_bv[len(next_bv)-1] = True
        else:
            next_bv = self.next_bit_vector(next_bv[0:len(next_bv)-1])
            if next_bv == None:
                return None
            next_bv.append(False)
        return next_bv

    def generate_vote_completions(self, partial_vote, alternatives):
        unknown_pairs = []
        for a in alternatives:
            for b in alternatives:
                if a==b:
                    continue
                if ((a, b) not in partial_vote) and ((b, a) not in partial_vote) and ((b, a) not in unknown_pairs):
                    unknown_pairs.append((a, b))
        swap_flags = [False] * len(unknown_pairs)
        vote_completions = []
        while True:
            new_completion = partial_vote.copy()
            for i in range(len(unknown_pairs)):
                if swap_flags[i]:
                    new_completion.add((unknown_pairs[i][1],unknown_pairs[i][0]))  
                else:
                    new_completion.add((unknown_pairs[i][0],unknown_pairs[i][1]))
            listvote = self.listize(new_completion)
            if listvote != None:
                vote_completions.append(listvote)   
            swap_flags = self.next_bit_vector(swap_flags)
            if swap_flags == None:
                break 

        return vote_completions

    def internal_generate_completions(self, index, votewise_completions, completions):
        if index >= len(votewise_completions):
            return completions
        next_completions = []
        for completion in completions:
            for vote_completion in votewise_completions[index]:
                new_completion = completion.copy()
                new_completion.append(vote_completion)
                next_completions.append(new_completion)
        return self.internal_generate_completions(index+1, votewise_completions, next_completions)

    def generate_completions(self, partial_profile, alternatives):
        votewise_completions = []
        for voter in partial_profile:
            voter_completions = self.generate_vote_completions(
                voter, alternatives)
            votewise_completions.append(voter_completions)
        completions = self.internal_generate_completions(
            0, votewise_completions, [[]])
        return completions


gen = CompletionsGenerator()
alts = {"a", "b", "c"}
profile = [{("a","b"),("b","c")}, {("a","b")}]
print(gen.generate_completions(profile, alts))
