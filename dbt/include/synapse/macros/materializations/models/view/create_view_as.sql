{% macro synapse__create_view_as(relation, sql) -%}

  {%- set temp_view_sql = sql.replace("'", "''") -%}

  {% set contract_config = config.get('contract') %}


  {% if contract_config.enforced %}
      {{ exceptions.warn("Model contracts cannot be enforced by <adapter>!" }}
      {{ get_assert_columns_equivalent(sql) }}
  {%- endif %}

  EXEC('create view {{ relation.include(database=False) }} as {{ temp_view_sql }};');

{% endmacro %}
