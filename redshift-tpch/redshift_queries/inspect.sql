select query, elapsed, substring
from svl_qlog
order by query
desc limit 20;

select *
from svl_query_summary
where is_diskbased='t'