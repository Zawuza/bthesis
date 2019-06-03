import sqlite3
from functools import partial


def save_result_to_file(result_list, index):
    with open("results.txt", "a") as f:
        print("-------------NEXT EXPERIMENT---------------------------------------------", file=f)
        print("Profile index:", index, file=f)
        print("Queries count:", str(len(result_list)), file=f)
        print("Queries:", file=f)
        for data in result_list:
            current_knowledge = data[0]
            current_winner = data[1]
            next_query = data[2]
            next_voter = data[3]
            print("    ", next_query, next_voter, file=f)
        print("Winner:", current_winner, file=f)
        print("", file=f)
        print("", file=f)
        print("", file=f)
        print("Partial profile from the last elicitation situation:", file=f)
        for preferences in current_knowledge:
            print("    ", preferences, file=f)


def __save_result_to_db(db_path, table_name, result_list, profile_id):
    conn = sqlite3.connect(db_path)
    query1 = "INSERT INTO " + table_name + \
        "(profile_id, query_index, current_winner, current_knowledge, next_query, next_voter) VALUES"
    query2 = ""
    for i in range(len(result_list)):
        if query2 != "":
            query2 += ","
        data = result_list[i]
        current_knowledge = data[0]
        current_winner = data[1]
        next_query = data[2]
        next_voter = data[3]
        query2 += "(" + str(profile_id) + ",\"" + str(i) + "\",\"" + current_winner + "\",\"" + current_knowledge + "\",\"" + \
            str(next_query) + "\",\"" + \
            str(next_voter) + "\")"
    query = query1 + query2 + ";"
    conn.execute(query)
    conn.commit()
    conn.close()
    return


def save_result_to_db(db_path, results_table_name):
    return partial(__save_result_to_db, db_path, results_table_name)


def create_results_table_with_name(db_path, table_name, dataset_name):
    query1 = "CREATE TABLE " + table_name + \
        " ( profile_id INTEGER REFERENCES " + dataset_name + "(Id),"
    query2 = """
                query_index INTEGER,
                current_winner TEXT,
                current_knowledge TEXT,
                next_query TEXT,
                next_voter INTEGER
                );
                """
    query = query1 + query2
    conn = sqlite3.connect(db_path)
    conn.execute(query)
    conn.commit()
    conn.close()
    return
