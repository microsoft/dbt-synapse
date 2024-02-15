if object_id ('{schema}.on_run_hook') is not null
    drop table {schema}.on_run_hook;

create table {schema}.on_run_hook
(
    test_state       VARCHAR(100), -- start|end
    target_dbname    VARCHAR(100),
    target_host      VARCHAR(100),
    target_name      VARCHAR(100),
    target_schema    VARCHAR(100),
    target_type      VARCHAR(100),
    target_user      VARCHAR(100),
    target_pass      VARCHAR(100),
    target_threads   INTEGER,
    run_started_at   VARCHAR(100),
    invocation_id    VARCHAR(100)
)
WITH(
    DISTRIBUTION = ROUND_ROBIN,
    HEAP
);
