{% macro synapse__get_columns_in_query(select_sql) %}
    {% call statement('get_columns_in_query', fetch_result=True, auto_begin=False) -%}
        select TOP 0 * from (
            {{ select_sql }}
        ) as __dbt_sbq
    {% endcall %}
    {{ return(load_result('get_columns_in_query').table.columns | map(attribute='name') | list) }}
{% endmacro %}

{% macro synapse__list_relations_without_caching(schema_relation) %}
  {% call statement('list_relations_without_caching', fetch_result=True) -%}
    select
      table_catalog as [database],
      table_name as [name],
      table_schema as [schema],
      case when table_type = 'BASE TABLE' then 'table'
           when table_type = 'VIEW' then 'view'
           else table_type
      end as table_type

    from information_schema.tables
    where table_schema like '{{ schema_relation.schema }}'
      and table_catalog like '{{ schema_relation.database }}'
  {% endcall %}
  {{ return(load_result('list_relations_without_caching').table) }}
{% endmacro %}
 
{% macro synapse__list_schemas(database) %}
  {% call statement('list_schemas', fetch_result=True, auto_begin=False) -%}
    select  name as [schema]
    from sys.schemas
  {% endcall %}
  {{ return(load_result('list_schemas').table) }}
{% endmacro %}

{% macro synapse__create_schema(relation) -%}
  {% call statement('create_schema') -%}
    IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{{ relation.without_identifier().schema }}')
    BEGIN
    EXEC('CREATE SCHEMA {{ relation.without_identifier().schema }}')
    END
  {% endcall %}
{% endmacro %}

{% macro synapse__drop_relation(relation) -%}
  {% call statement('drop_relation', auto_begin=False) -%}
    {{ synapse__drop_relation_script(relation) }}
  {%- endcall %}
{% endmacro %}

{% macro synapse__drop_relation_script(relation) -%}
  {% if relation.type == 'view' -%}
    {% set object_id_type = 'V' %}
  {% elif relation.type == 'table'%}
    {% set object_id_type = 'U' %}
  {%- else -%} invalid target name
  {% endif %}
  if object_id ('{{ relation.include(database=False) }}','{{ object_id_type }}') is not null
    begin
    drop {{ relation.type }} {{ relation.include(database=False) }}
    end
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
