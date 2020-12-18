{% macro synapse__snapshot_hash_arguments(args) %}
    {{ return(sqlserver__snapshot_hash_arguments(args)) }}
{% endmacro %}

{% macro snapshot_check_strategy(node, snapshotted_rel, current_rel, config, target_exists) %}
    {{ return(snapshot_check_strategy(node, snapshotted_rel, current_rel, config, target_exists)) }}
{% endmacro %}