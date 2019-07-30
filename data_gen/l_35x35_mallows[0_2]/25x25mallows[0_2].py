import random

VOTES_AND_ALTERNATIVES_COUNT = 25
PROFILES_COUNT = 200
PARAM_F = 0.2

alternatives = [str(i) for i in range(VOTES_AND_ALTERNATIVES_COUNT)]

def main():
    output = ""
    for i in range(PROFILES_COUNT):
        profile=[]
        base_rank = alternatives.copy()
        random.shuffle(base_rank)
        for j in range(VOTES_AND_ALTERNATIVES_COUNT):
            vote=mallows_get(base_rank, PARAM_F)
            profile.append(vote)
        output += '("' + str(profile) + '"),'
    with open("data_gen\\l_35x35_mallows[0_1]\\25x25mallows[0_1].sql", "w") as text_file:
        text_file.write(output)

def mallows_get(base_rank, Ф):
    result=[]
    for i in range(len(base_rank)):
        randfloat=random.random()
        probability=0
        for k in range(i+1):
            probability += calc_prob(i, k, Ф)
            if randfloat <= probability:
                result.insert(k, base_rank[i])
                break
    return result

def calc_prob(i, k, Ф):
    up=Ф ** (i-k)
    down=0
    for j in range(i+1):
        down += Ф ** j
    return up/down

main()
