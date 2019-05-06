import sqlite3

def save_result_to_db(result):
    winner = result[0]
    query_voter_list = result[1]
    elicitation_situation_profile = result[2]
    return

conn = sqlite3.connect(".\db\data.db")
create_experiment_table = """
                          CREATE TABLE experiment_1_results(
                              profile_id INTEGER,
                              winner TEXT,
                              query_count INTEGER,
                              query_list TEXT,
                              elicitated_profile TEXT
                          );  
                          """

c = conn.cursor()
c.execute(create_experiment_table)
conn.close()