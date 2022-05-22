
{% macro synapse__get_columns_in_relation(relation) -%}
  {# hack because tempdb has no infoschema see: #}
  {# https://stackoverflow.com/questions/63800841/get-column-names-of-temp-table-in-azure-synapse-dw #}
  {% if relation.identifier.startswith("#") %}
    {% set tmp_tbl_hack = relation.incorporate(
      path={"identifier": relation.identifier.replace("#", "") ~ '_tmp_tbl_hack'},
      type='table')-%}

    {% do  drop_relation(tmp_tbl_hack) %}
    {% set sql_create %}
        CREATE TABLE {{ tmp_tbl_hack }}
        WITH(
          -- Always use a round-robin heap, since columns with types like varbinaries
          -- cannot be part of a clustered column store, which is the default index
          DISTRIBUTION = ROUND_ROBIN,
          HEAP
        )
        AS
        SELECT TOP(1) *
        FROM {{relation}}
    {% endset %}
    {% call statement() -%} {{ sql_create }} {%- endcall %}

    {% set output = get_columns_in_relation(tmp_tbl_hack) %}
    {% do  drop_relation(tmp_tbl_hack) %}
    {{ return(output) }}
  {% endif %}

  {% call statement('get_columns_in_relation', fetch_result=True) %}
    select
        column_name,
        data_type,
        character_maximum_length,
        numeric_precision,
        numeric_scale
    from INFORMATION_SCHEMA.COLUMNS
    where table_name = '{{ relation.identifier }}'
      and table_schema = '{{ relation.schema }}'
  {% endcall %}
  {% set table = load_result('get_columns_in_relation').table %}
  {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}

{% macro synapse__get_columns_in_query(select_sql) %}
    {% call statement('get_columns_in_query', fetch_result=True, auto_begin=False) -%}
        select TOP 0 * from (
            {{ select_sql }}
        ) as __dbt_sbq
    {% endcall %}
    {{ return(load_result('get_columns_in_query').table.columns | map(attribute='name') | list) }}
{% endmacro %}
