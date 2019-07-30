import random

alternatives = [str(i) for i in range(25)]

output = ""
for i in range(200):
    profile = []
    for j in range(25):
        random.shuffle(alternatives)
        v = alternatives.copy()
        profile.append(v)
    output += '("' + str(profile) + '"),'
with open("data_gen\\l_25x25_uniform\\25x25uniform.sql", "w") as text_file:
    text_file.write(output)