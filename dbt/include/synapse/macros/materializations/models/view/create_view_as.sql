{% macro synapse__create_view_as(relation, sql) -%}

  {%- set temp_view_sql = sql.replace("'", "''") -%}

  {% set contract_config = config.get('contract') %}

    {{exceptions.warn("Model contracts cannot be enforced by <adapter>!")}}

  {% if contract_config.enforced %}
      {{ get_assert_columns_equivalent(sql) }}
  {%- endif %}

  EXEC('create view {{ relation }} as {{ temp_view_sql }};');

{% endmacro %}
