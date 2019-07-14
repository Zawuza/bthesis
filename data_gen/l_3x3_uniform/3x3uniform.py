import random

alternatives = ["a","b","c"]

for i in range(200):
    random.shuffle(alternatives)
    v1 = alternatives.copy()
    random.shuffle(alternatives)
    v2 = alternatives.copy()
    random.shuffle(alternatives)
    v3 = alternatives.copy()
    profile = [v1,v2,v3]
    print('("' + str(profile) + '"),')