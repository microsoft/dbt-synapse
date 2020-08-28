{% macro sqlserver__post_snapshot(staging_relation) %}
  -- Clean up the snapshot temp table
  {% do drop_relation(staging_relation) %}
{% endmacro %}


{% macro sqlserver__snapshot_merge_sql(target, source, insert_cols) -%}
    {%- set insert_cols_csv = insert_cols | join(', ') -%}

    update {{ target }}
    set dbt_valid_to = TMP.dbt_valid_to
    from {{ source }} TMP
    where {{ target }}.dbt_scd_id = TMP.dbt_scd_id
        and TMP.dbt_change_type = 'update'
        and {{ target }}.dbt_valid_to is null;

    insert into {{ target }}
    select *
    from {{ source }} TMP
        left join {{ target }} Dest on Dest.dbt_scd_id = TMP.dbt_scd_id
    where Dest.dbt_scd_id is null
        and TMP.dbt_change_type = 'insert';
{% endmacro %}


