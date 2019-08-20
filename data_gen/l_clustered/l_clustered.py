import random

ALTERNATIVES_COUNT = 3
VOTES_COUNT = 12
PROFILES_COUNT = 200
SQL_FILE_NAME = "data_gen\\l_clustered\\clustered.sql"


def main():
    alternatives = [str(i) for i in range(ALTERNATIVES_COUNT)]
    output = ""
    for i in range(PROFILES_COUNT):
        cluster1 = alternatives.copy()
        cluster2 = alternatives.copy()
        cluster3 = alternatives.copy()
        random.shuffle(cluster1)
        random.shuffle(cluster2)
        random.shuffle(cluster3)
        profile = []
        for j in range(VOTES_COUNT):
            number = random.randint(1,3)
            if number == 1:
                profile.append(cluster1)
            elif number == 2:
                profile.append(cluster2)
            elif number == 3:
                profile.append(cluster3)
            else:
                print("AAAAAAAAAAAAAAAAAAAAAAAA, wrong number")
        output += '("' + str(profile) + '"),'
    with open(SQL_FILE_NAME, "w") as text_file:
        text_file.write(output)

main()
