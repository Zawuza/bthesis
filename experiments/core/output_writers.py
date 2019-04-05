def save_result_to_file(result):
    winner = result[0]
    query_voter_list = result[1]
    elicitation_situation_profile = result[2]

    with open("results.txt", "a") as f:
        print("-------------NEXT EXPERIMENT---------------------------------------------", file=f)
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