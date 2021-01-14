{% macro synapse__snapshot_hash_arguments(args) %}
    {{ return(sqlserver__snapshot_hash_arguments(args)) }}
{% endmacro %}
