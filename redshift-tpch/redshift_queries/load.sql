copy customer from 's3://uwdb/tpch/uniform/10GB/customer.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

copy orders from 's3://uwdb/tpch/uniform/10GB/order.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

copy lineitem from 's3://uwdb/tpch/uniform/10GB/lineitem.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

copy nation from 's3://uwdb/tpch/uniform/10GB/nation.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

copy part from 's3://uwdb/tpch/uniform/10GB/part.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

copy partsupp from 's3://uwdb/tpch/uniform/10GB/partsupp.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

copy region from 's3://uwdb/tpch/uniform/10GB/region.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

copy supplier from 's3://uwdb/tpch/uniform/10GB/supplier.tbl'
credentials 'aws_access_key_id=___;aws_secret_access_key=___'
delimiter '|';

vacuum;
analyze;
