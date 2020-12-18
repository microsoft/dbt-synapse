{% macro synapse__information_schema_name(database) -%}
  {{ return(sqlserver__information_schema_name(database)) }}
{%- endmacro %}

{% macro synapse__get_columns_in_query(select_sql) %}
    {% call statement('get_columns_in_query', fetch_result=True, auto_begin=False) -%}
        select TOP 0 * from (
            {{ select_sql }}
        ) as __dbt_sbq
    {% endcall %}
    {{ return(load_result('get_columns_in_query').table.columns | map(attribute='name') | list) }}
{% endmacro %}

{% macro synapse__list_relations_without_caching(schema_relation) %}
  {{ return(sqlserver__list_relations_without_caching(schema_relation)) }}
{% endmacro %}
 
{% macro synapse__list_schemas(database) %}
  {{ return(sqlserver__list_schemas(database)) }}
{% endmacro %}

{% macro synapse__create_schema(relation) -%}
  {% call statement('create_schema') -%}
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{{ relation.without_identifier().schema }}')
    BEGIN
    EXEC('CREATE SCHEMA {{ relation.without_identifier().schema }}')
    END
  {% endcall %}
{% endmacro %}

{% macro synapse__drop_schema(relation) -%}
  {{ return(sqlserver__drop_schema(relation)) }}
{% endmacro %}

{# TODO make this function just a wrapper of synapse__drop_relation_script #}
{% macro synapse__drop_relation(relation) -%}
  {{ return(sqlserver__drop_relation(relation)) }}
{% endmacro %}

{% macro synapse__drop_relation_script(relation) -%}
  {{ return(sqlserver__drop_relation_script(relation)) }}
{% endmacro %}

{% macro synapse__check_schema_exists(information_schema, schema) -%}
  {{ return(sqlserver__check_schema_exists(information_schema, schema)) }}
{% endmacro %}

{% macro synapse__create_view_as(relation, sql) -%}
  create view {{ relation.include(database=False) }} as
    {{ sql }}
{% endmacro %}

{# TODO Actually Implement the rename index piece #}
{# TODO instead of deleting it...  #}
{% macro synapse__rename_relation(from_relation, to_relation) -%}
  {% call statement('rename_relation') -%}
  
    rename object {{ from_relation.include(database=False) }} to {{ to_relation.identifier }}
  {%- endcall %}
{% endmacro %}

{% macro synapse__create_clustered_columnstore_index(relation) -%}
  {%- set cci_name = relation.schema ~ '_' ~ relation.identifier ~ '_cci' -%}
  {%- set relation_name = relation.schema ~ '_' ~ relation.identifier -%}
  {%- set full_relation = relation.schema ~ '.' ~ relation.identifier -%}
  if object_id ('{{relation_name}}.{{cci_name}}','U') is not null
      begin
      drop index {{relation_name}}.{{cci_name}}
      end

  CREATE CLUSTERED COLUMNSTORE INDEX {{cci_name}}
    ON {{full_relation}}
{% endmacro %}

{% macro synapse__create_table_as(temporary, relation, sql) -%}
   {%- set index = config.get('index', default="CLUSTERED COLUMNSTORE INDEX") -%}
   {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}
   {% set tmp_relation = relation.incorporate(
   path={"identifier": relation.identifier.replace("#", "") ~ '_temp_view'},
   type='view')-%}
   {%- set temp_view_sql = sql.replace("'", "''") -%}

   {{ synapse__drop_relation_script(tmp_relation) }}

   {{ synapse__drop_relation_script(relation) }}

   EXEC('create view {{ tmp_relation.schema }}.{{ tmp_relation.identifier }} as
    {{ temp_view_sql }}
    ');

  CREATE TABLE {{ relation.include(database=False) }}
    WITH(
      DISTRIBUTION = {{dist}},
      {{index}}
      )
    AS (SELECT * FROM {{ tmp_relation.schema }}.{{ tmp_relation.identifier }})

   {{ synapse__drop_relation_script(tmp_relation) }}

{% endmacro %}

{% macro synapse__insert_into_from(to_relation, from_relation) -%}
  {{ return(sqlserver__insert_into_from(to_relation, from_relation)) }}
{% endmacro %}

{% macro synapse__current_timestamp() -%}
  {{ return(sqlserver__current_timestamp()) }}
{%- endmacro %}

{% macro synapse__get_columns_in_relation(relation) -%}
  {% call statement('get_columns_in_relation', fetch_result=True) %}
      SELECT
          column_name,
          data_type,
          character_maximum_length,
          numeric_precision,
          numeric_scale
      FROM
          (select
              ordinal_position,
              column_name,
              data_type,
              character_maximum_length,
              numeric_precision,
              numeric_scale
          from INFORMATION_SCHEMA.COLUMNS
          where table_name = '{{ relation.identifier }}'
            and table_schema = '{{ relation.schema }}') cols


  {% endcall %}
  {% set table = load_result('get_columns_in_relation').table %}
  {{ return(sql_convert_columns_in_relation(table)) }}
{% endmacro %}

{% macro synapse__make_temp_relation(base_relation, suffix) %}
  {{ return(sqlserver__make_temp_relation(base_relation, suffix)) }}
{% endmacro %}

{% macro synapse__snapshot_string_as_time(timestamp) -%}
  {{ return(sqlserver__snapshot_string_as_time(timestamp)) }}
{%- endmacro %}