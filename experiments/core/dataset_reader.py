import sqlite3

retrieve_dataset_query = "SELECT * FROM "

def read_dataset(dataset_name, db_path):
    profiles, alternatives = [], []
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    query = retrieve_dataset_query + dataset_name
    for row in c.execute(query):
        index = row[0]
        profile = eval(row[1].replace("(","[").replace(")","]"))
        alternativs = set(profile[0])
        alternatives.append(alternativs)
        profiles.append((index,profile))
    conn.close()
    return alternatives, profiles
