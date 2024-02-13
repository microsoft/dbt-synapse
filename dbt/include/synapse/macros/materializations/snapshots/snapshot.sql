{% macro synapse__create_columns(relation, columns) %}
  {# default__ macro uses "add column"
     TSQL preferes just "add"
  #}

  {% set columns %}
    {% for column in columns %}
      , CAST(NULL AS {{column.data_type}}) AS {{column_name}}
    {% endfor %}
  {% endset %}

  {% set tempTableName %}
    [{{relation.database}}].[{{ relation.schema }}].[{{ relation.identifier }}_{{ range(1300, 19000) | random }}]
  {% endset %}

  {%- set index = config.get('index', default="CLUSTERED COLUMNSTORE INDEX") -%}
  {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}
  {% set tempTable %}
      CREATE TABLE {{tempTableName}}
      WITH(
      DISTRIBUTION = {{dist}},
      {{index}}
      )
      AS SELECT * {{columns}} FROM [{{relation.database}}].[{{ relation.schema }}].[{{ relation.identifier }}] {{ information_schema_hints() }}
  {% endset %}

  {% call statement('create_temp_table') -%}
      {{ tempTable }}
  {%- endcall %}

  {% set dropTable %}
      DROP TABLE [{{relation.database}}].[{{ relation.schema }}].[{{ relation.identifier }}]
  {% endset %}

  {% call statement('drop_table') -%}
      {{ dropTable }}
  {%- endcall %}

  {%- set index = config.get('index', default="CLUSTERED COLUMNSTORE INDEX") -%}
  {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}
  {% set createTable %}
      CREATE TABLE {{ relation }}
      WITH(
      DISTRIBUTION = {{dist}},
      {{index}}
      )
      AS SELECT * FROM {{tempTableName}} {{ information_schema_hints() }}
  {% endset %}

  {% call statement('create_Table') -%}
      {{ createTable }}
  {%- endcall %}

  {% set dropTempTable %}
      DROP TABLE {{tempTableName}}
  {% endset %}

  {% call statement('drop_temp_table') -%}
      {{ dropTempTable }}
  {%- endcall %}
{% endmacro %}
