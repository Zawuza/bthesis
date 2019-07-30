import random

alternatives = [str(i) for i in range(25)]

for i in range(200):
    profile = []
    for j in range(25):
        random.shuffle(alternatives)
        v = alternatives.copy()
        profile.append(v)
    print('("' + str(profile) + '"),')