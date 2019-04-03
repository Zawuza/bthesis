borda_name = "Borda"


class CompleteProfileBordaSolver:

    @classmethod
    def find_winner(cls, alternatives, complete_profile):
        scores = dict.fromkeys(alternatives, 0)
        for voter in complete_profile:
            for i in range(len(voter)):
                scores[voter[i]] += len(voter) - i - 1
        return max(scores, key=scores.get)


class IncompleteProfileBordaSolver:

    @classmethod
    def longest_chain(cls,a,b,partial_vote, alternatives):
        result_chain = [a]
        while True:
            last = result_chain[len(result_chain)-1]
            for c in alternatives:
                if ((last,c) in partial_vote) and ((c,b) in partial_vote):
                    result_chain.append(c)
            break
        return result_chain

    @classmethod
    def find_necessary_winner_if_exists(cls, alternatives, incomplete_profile):
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
                    if not ((a, w) in partial_vote): #includes "unknown"
                        score_a += scores[len(alternatives) - len(downs[a][i]) - 1]
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