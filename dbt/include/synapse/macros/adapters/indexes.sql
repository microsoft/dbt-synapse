{% macro synapse__create_clustered_columnstore_index(relation) -%}
  {%- set cci_name = (relation.schema ~ '_' ~ relation.identifier ~ '_cci') | replace(".", "") | replace(" ", "") -%}
  {%- set relation_name = relation.schema ~ '_' ~ relation.identifier -%}
  {%- set full_relation = '"' ~ relation.schema ~ '"."' ~ relation.identifier ~ '"' -%}
  if object_id ('{{relation_name}}.{{cci_name}}','U') is not null
      begin
      drop index {{relation_name}}.{{cci_name}}
      end

  CREATE CLUSTERED COLUMNSTORE INDEX {{cci_name}}
    ON {{full_relation}}
{% endmacro %}


{# most of this code is from https://github.com/jacobm001/dbt-mssql/blob/master/dbt/include/mssql/macros/indexes.sql        #}

{% macro drop_xml_indexes() -%}
{# Altered from https://stackoverflow.com/q/1344401/10415173 #}
{# and https://stackoverflow.com/a/33785833/10415173         #}


{{ log("Running drop_xml_indexes() macro...") }}

declare @drop_xml_indexes nvarchar(max) = (
  select STRING_AGG(a.command, ' ') from (
    select 'IF INDEXPROPERTY(' + CONVERT(VARCHAR(MAX), sys.tables.[object_id]) + ', ''' + sys.indexes.[name] + ''', ''IndexId'') IS NOT NULL DROP INDEX [' + sys.indexes.[name] + '] ON ' + '[' + SCHEMA_NAME(sys.tables.[schema_id]) + '].[' + OBJECT_NAME(sys.tables.[object_id]) + ']; ' as command
    from sys.indexes
    inner join sys.tables on sys.indexes.object_id = sys.tables.object_id
    where sys.indexes.[name] is not null
      and sys.indexes.type_desc = 'XML'
      and sys.tables.[name] = '{{ this.table }}'
    ) a
); exec sp_executesql @drop_xml_indexes;

{%- endmacro %}


{% macro drop_spatial_indexes() -%}
{# Altered from https://stackoverflow.com/q/1344401/10415173 #}
{# and https://stackoverflow.com/a/33785833/10415173         #}

{{ log("Running drop_spatial_indexes() macro...") }}

declare @drop_spatial_indexes nvarchar(max) = (
  select STRING_AGG(a.command, ' ') from (
    select 'IF INDEXPROPERTY(' + CONVERT(VARCHAR(MAX), sys.tables.[object_id]) + ', ''' + sys.indexes.[name] + ''', ''IndexId'') IS NOT NULL DROP INDEX [' + sys.indexes.[name] + '] ON ' + '[' + SCHEMA_NAME(sys.tables.[schema_id]) + '].[' + OBJECT_NAME(sys.tables.[object_id]) + ']; ' as command
    from sys.indexes
    inner join sys.tables on sys.indexes.object_id = sys.tables.object_id
    where sys.indexes.[name] is not null
      and sys.indexes.type_desc = 'Spatial'
      and sys.tables.[name] = '{{ this.table }}'
    ) a
); exec sp_executesql @drop_spatial_indexes;

{%- endmacro %}


{% macro drop_fk_constraints() -%}
{# Altered from https://stackoverflow.com/q/1344401/10415173 #}

{{ log("Running drop_fk_constraints() macro...") }}

declare @drop_fk_constraints nvarchar(max) = (
  select STRING_AGG(a.command, ' ') from (
    select 'IF OBJECT_ID(''' + SCHEMA_NAME(CONVERT(VARCHAR(MAX), sys.foreign_keys.[schema_id])) + '.' + sys.foreign_keys.[name] + ''', ''F'') IS NOT NULL ALTER TABLE [' + SCHEMA_NAME(sys.foreign_keys.[schema_id]) + '].[' + OBJECT_NAME(sys.foreign_keys.[parent_object_id]) + '] DROP CONSTRAINT [' + sys.foreign_keys.[name]+ '];' as command
    from sys.foreign_keys
    inner join sys.tables on sys.foreign_keys.[referenced_object_id] = sys.tables.[object_id]
    where sys.tables.[name] = '{{ this.table }}'
    ) a
); exec sp_executesql @drop_fk_constraints;

{%- endmacro %}


{% macro drop_pk_constraints() -%}
{# Altered from https://stackoverflow.com/q/1344401/10415173 #}
{# and https://stackoverflow.com/a/33785833/10415173         #}

{{ drop_xml_indexes() }}

{{ drop_spatial_indexes() }}

{{ drop_fk_constraints() }}

{{ log("Running drop_pk_constraints() macro...") }}

declare @drop_pk_constraints nvarchar(max) = (
  select STRING_AGG(a.command, ' ') from (
    select 'IF INDEXPROPERTY(' + CONVERT(VARCHAR(MAX), sys.tables.[object_id]) + ', ''' + sys.indexes.[name] + ''', ''IndexId'') IS NOT NULL ALTER TABLE [' + SCHEMA_NAME(sys.tables.[schema_id]) + '].[' + sys.tables.[name] + '] DROP CONSTRAINT [' + sys.indexes.[name]+ '];' as command
    from sys.indexes
    inner join sys.tables on sys.indexes.[object_id] = sys.tables.[object_id]
    where sys.indexes.is_primary_key = 1
      and sys.tables.[name] = '{{ this.table }}'
    ) a
); exec sp_executesql @drop_pk_constraints;

{%- endmacro %}


{% macro drop_all_indexes_on_table() -%}
{# Altered from https://stackoverflow.com/q/1344401/10415173 #}
{# and https://stackoverflow.com/a/33785833/10415173         #}

{{ drop_pk_constraints() }}

{{ log("Dropping remaining indexes...") }}

declare @drop_remaining_indexes_last nvarchar(max) = (
  select STRING_AGG(a.command, ' ') from (
    select 'IF INDEXPROPERTY(' + CONVERT(VARCHAR(MAX), sys.tables.[object_id]) + ', ''' + sys.indexes.[name] + ''', ''IndexId'') IS NOT NULL DROP INDEX [' + sys.indexes.[name] + '] ON ' + '[' + SCHEMA_NAME(sys.tables.[schema_id]) + '].[' + OBJECT_NAME(sys.tables.[object_id]) + ']; ' as command
    from sys.indexes
    inner join sys.tables on sys.indexes.object_id = sys.tables.object_id
    where sys.indexes.[name] is not null
      and sys.tables.[name] = '{{ this.table }}'
    ) a
); exec sp_executesql @drop_remaining_indexes_last;

{%- endmacro %}


{% macro create_clustered_index(columns, unique=False) -%}
  {{ return(create_clustered_index(columns, unique=False)) }}
{%- endmacro %}


{% macro create_nonclustered_index(columns, includes=False) %}
  {{ return(create_nonclustered_index(columns, includes=False)) }}
{% endmacro %}


{% macro drop_fk_indexes_on_table(relation) -%}
  {% call statement('find_references', fetch_result=true) %}
      SELECT  obj.name AS FK_NAME,
      sch.name AS [schema_name],
      tab1.name AS [table],
      col1.name AS [column],
      tab2.name AS [referenced_table],
      col2.name AS [referenced_column]
      FROM sys.foreign_key_columns fkc
      INNER JOIN sys.objects obj
          ON obj.object_id = fkc.constraint_object_id
      INNER JOIN sys.tables tab1
          ON tab1.object_id = fkc.parent_object_id
      INNER JOIN sys.schemas sch
          ON tab1.schema_id = sch.schema_id
      INNER JOIN sys.columns col1
          ON col1.column_id = parent_column_id AND col1.object_id = tab1.object_id
      INNER JOIN sys.tables tab2
          ON tab2.object_id = fkc.referenced_object_id
      INNER JOIN sys.columns col2
          ON col2.column_id = referenced_column_id AND col2.object_id = tab2.object_id
      WHERE sch.name = '{{ relation.schema }}' and tab2.name = '{{ relation.identifier }}'
  {% endcall %}
      {% set references = load_result('find_references')['data'] %}
      {% for reference in references -%}
        {% call statement('main') -%}
           alter table [{{reference[1]}}].[{{reference[2]}}] drop constraint [{{reference[0]}}]
        {%- endcall %}
      {% endfor %}
{% endmacro %}
