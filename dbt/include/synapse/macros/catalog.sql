
{% macro synapse__get_catalog(information_schemas, schemas) -%}
  {{ return(sqlserver__get_catalog(information_schemas, schemas)) }}
{%- endmacro %}
