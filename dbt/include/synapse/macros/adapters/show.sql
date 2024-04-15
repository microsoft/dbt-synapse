
{% macro get_limit_subquery_sql(sql, limit) %}
  {{ adapter.dispatch('get_limit_subquery_sql', 'dbt')(sql, limit) }}
{% endmacro %}

{# Synapse doesnt support ANSI LIMIT clause #}
{% macro synapse__get_limit_subquery_sql(sql, limit) %}
{%- set warn = "-- limit of " ~ limit ~ " is ignored. Synapse doesn't support the implementation" -%}

{{ warn }}
{{ sql }}

{% endmacro %}
