{% macro synapse__post_snapshot(staging_relation) %}
  {{ return(sqlserver__post_snapshot(staging_relation)) }}
{% endmacro %}