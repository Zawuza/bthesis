import sqlite3
from queue import Queue
from core.dataset_reader import read_dataset
from core.voting_rules import rules_global_dict

DB_PATH = ".\\db\\data.db"
DATASET = "l_dataset_uniform_3x3"
RULE_NAME = "Plurality"


def find_optimal_count(alternatives, complete_p):
    rule = rules_global_dict[RULE_NAME]
    queue = Queue()
    queue.put(([set()] * len(complete_p), 0))
    while True:
        knowledge, depth = queue.get()
        if rule.find_single_necessary_winner_if_exists(alternatives, knowledge) != None:
            return depth
        query_voter_pairs = []
        for i in range(len(knowledge)):
            inc_vote = knowledge[i]
            for a in alternatives:
                for b in alternatives:
                    if a == b:
                        continue
                    if not ((a, b) in inc_vote) and not ((b, a) in inc_vote) \
                            and not (((a, b), i) in query_voter_pairs) and not (((b, a),i) in query_voter_pairs):
                        query_voter_pairs.append(((a, b), i))
        for query, voter in query_voter_pairs:
            inc_vote = knowledge[voter]
            a,b = query
            index_a = complete_p[voter].index(a)
            index_b = complete_p[voter].index(b)
            if index_a > index_b:
                inc_vote = inc_vote.union({(a,b)})
            else:
                inc_vote = inc_vote.union({(b,a)})
            new_knowledge = knowledge.copy()
            new_knowledge[voter] = inc_vote
            for x in alternatives:
                for y in alternatives:
                    for z in alternatives:
                        if ((x, y) in new_knowledge[voter]) and \
                            ((y, z) in new_knowledge[voter]) and \
                                (not (x, z) in new_knowledge[voter]):
                            comparison = set()
                            comparison.add((x, z))
                            new_knowledge[voter] = new_knowledge[voter].union(
                                comparison)
            queue.put((new_knowledge, depth + 1))


dataset = read_dataset(DATASET, DB_PATH)
all_alternatives = dataset[0]
profiles = dataset[1]
optimal_sum = 0
for i in range(len(profiles)):
    index, profile = profiles[i]
    alternatives = all_alternatives[i]
    print("Next profile " + str(i) + " , current sum: " + str(optimal_sum))
    optimal_sum += find_optimal_count(alternatives, profile)
print("Optimal overall sum: " + str(optimal_sum))
