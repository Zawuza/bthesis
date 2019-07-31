import sqlite3
import statistics
from core.voting_rules import rules_global_dict, VotingRule

DB_PATH = ".\\db\\data.db"
DATASET_SIZE = 200
DATASET = "l_dataset_uniform_3x3"
TABLES = [
    "l_results_cs_veto_uniform3x3_1",
    "l_results_cs_veto_uniform3x3_2",
    "l_results_cs_veto_uniform3x3_3",
    "l_results_cs_veto_uniform3x3_4"
]
MAX_QUERY_COUNT = 20
RULE_NAME = "Veto"

for i in range(MAX_QUERY_COUNT+1):
    sql_query = ""
    for table in TABLES:
        if sql_query != "":
            sql_query += " UNION ALL "
        sql_query += " SELECT * FROM " + table +\
            " INNER JOIN " + DATASET + " ON profile_id=Id " +\
            "WHERE query_index = " + str(i) + " "

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rule = rules_global_dict[RULE_NAME]
    losses = []
    for row in c.execute(sql_query):
        profile = eval(row[7].replace("(","[").replace(")","]"))
        alternatives = set(profile[0])
        elicitation_winner = row[2]
        winner = rule.find_single_winner(alternatives, profile)
        winner_score = rule.get_score(alternatives, profile, winner)
        elicitation_winner_score = rule.get_score(alternatives, profile, elicitation_winner)
        loss = winner_score - elicitation_winner_score
        losses.append(loss)
    for j in range(len(losses), DATASET_SIZE):
        losses.append(0)
    avg_loss = statistics.mean(losses)
    print("Loss after query " + str(i) + " is " + str(avg_loss))


