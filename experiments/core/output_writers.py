import sqlite3
from functools import partial


def save_result_to_file(result, index):
    winner = result[0]
    query_voter_list = result[1]
    elicitation_situation_profile = result[2]

    with open("results.txt", "a") as f:
        print("-------------NEXT EXPERIMENT---------------------------------------------", file=f)
        print("Profile index:", index, file=f)
        print("Winner:", winner, file=f)
        print("", file=f)
        print("Queries count:", str(len(query_voter_list)), file=f)
        print("", file=f)
        print("Queries:", file=f)
        for query_voter_pair in query_voter_list:
            print("    ", query_voter_pair, file=f)
        print("", file=f)
        print("Partial profile from the last elicitation situation:", file=f)
        for preferences in elicitation_situation_profile:
            print("    ", preferences, file=f)


def __save_result_to_db(db_path, table_name, result, index):
    winner = result[0]
    query_voter_list = result[1]
    elicitation_situation_profile = result[2]
    conn = sqlite3.connect(db_path)
    query1 = "INSERT INTO " + table_name + \
        "(profile_id, winner, query_count, query_list, partial_profile) VALUES"
    query2 = "(" + str(index) + ",\"" + winner + "\",\"" + str(len(query_voter_list)) + "\",\"" + \
        str(query_voter_list) + "\",\"" + str(elicitation_situation_profile) + "\")"
    query = query1 + query2
    conn.execute(query)
    conn.commit()
    conn.close()
    return


def save_result_to_db(db_path, results_table_name):
    return partial(__save_result_to_db, db_path, results_table_name)


def create_results_table_with_name(db_path, table_name, dataset_name):
    query1 = "CREATE TABLE " + table_name + \
        " ( profile_id INTEGER REFERENCES " + dataset_name + "(id),"
    query2 = """
                winner TEXT,
                query_count INTEGER,
                query_list TEXT,
                partial_profile TEXT
                );
                """
    query = query1 + query2
    conn = sqlite3.connect(db_path)
    conn.execute(query)
    conn.commit()
    conn.close()
    return
