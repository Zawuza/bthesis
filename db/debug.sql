SELECT DISTINCT profile_id AS id FROM css_3x3_results
WHERE 
	(select count(*) from css_3x3_results WHERE profile_id = id)
	<
	(select count(*) from random_pairwise_3x3_results WHERE profile_id = id);