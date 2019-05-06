import itertools

vote = ["a","b","c"]
all_permutations = list(itertools.permutations(vote))
for vote1 in all_permutations:
    for vote2 in all_permutations:
        for vote3 in all_permutations:
            profile = [vote1, vote2, vote3]
            print('("',profile,'")')