SELECT COUNT(*), count FROM (
SELECT COUNT(*)-1 AS count FROM l_results_rm_veto_uniform3x3_1 GROUP BY profile_id
UNION ALL
SELECT COUNT(*)-1 AS count FROM l_results_rm_veto_uniform3x3_2 GROUP BY profile_id
UNION ALL
SELECT COUNT(*)-1 AS count FROM l_results_rm_veto_uniform3x3_3 GROUP BY profile_id
UNION ALL
SELECT COUNT(*)-1 AS count FROM l_results_rm_veto_uniform3x3_4 GROUP BY profile_id
) GROUP BY count;