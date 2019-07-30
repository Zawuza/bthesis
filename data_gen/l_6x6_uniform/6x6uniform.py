import random

alternatives = [str(i) for i in range(6)]

output = ""
for i in range(200):
    profile = []
    for j in range(6):
        random.shuffle(alternatives)
        v = alternatives.copy()
        profile.append(v)
    output += '("' + str(profile) + '"),'
with open("data_gen\\l_6x6_uniform\\6x6uniform.sql", "w") as text_file:
    text_file.write(output)