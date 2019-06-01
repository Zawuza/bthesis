import sqlite3
from core.voting_rules import rules_global_dict
from core.elicitation_protocols import elicitation_protocols_global_dict
from core.dataset_reader import read_dataset
from core.experiment import Experiment
from core.output_writers import save_result_to_db, create_results_table_with_name

DB_PATH = ".\\db\\data.db"

retrieve_scheduled_experiments = """
                                 SELECT * FROM experiments
                                 WHERE Scheduled = 1
                                 """ 

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute(retrieve_scheduled_experiments)
scheduled_experiments = c.fetchall()
conn.close()

for experiment_row in scheduled_experiments:
    rule = rules_global_dict[experiment_row[1]]
    protocol = elicitation_protocols_global_dict[experiment_row[2]]()
    dataset_name = experiment_row[3]
    alternatives, profiles = read_dataset(dataset_name, DB_PATH)
    results_table = experiment_row[4]
    create_results_table_with_name(DB_PATH, results_table, dataset_name)
    experiment = Experiment(alternatives, profiles, rule, protocol, save_result_to_db(DB_PATH, results_table))
    experiment.execute()