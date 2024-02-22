{% macro get_show_sql(compiled_code, sql_header, limit) -%}
  {%- if sql_header -%}
  {{ sql_header }}
  {%- endif -%}
  {%- if limit is not none -%}
  {{ get_limit_subquery_sql(compiled_code, limit) }}
  {%- else -%}
  {{ compiled_code }}
  {%- endif -%}
{% endmacro %}

{% macro get_limit_subquery_sql(sql, limit) %}
  {{ adapter.dispatch('get_limit_subquery_sql', 'dbt')(sql, limit) }}
{% endmacro %}

{# Synapse doesnt support ANSI LIMIT clause #}
{% macro synapse__get_limit_subquery_sql(sql, limit) %}
    select top {{ limit }} *
    from (
        {{ sql }}
    ) as model_limit_subq
{% endmacro %}
