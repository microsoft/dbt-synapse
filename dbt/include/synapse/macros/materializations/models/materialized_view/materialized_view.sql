{% macro ref(model_name) %}

    {% do return(builtins.ref(model_name).include(database=false)) %}

{% endmacro %}

{% macro synapse__get_replace_materialized_view_as_sql(relation, sql, existing_relation, backup_relation, intermediate_relation) %}
    {# Synapse does not have ALTER...RENAME function, so use existing macro synapse__rename_relation #}

    {{- synapse__get_create_materialized_view_as_sql(intermediate_relation, sql) -}} GO

    if object_id ('{{ backup_relation.include(database=False) }}','V') is not null
        begin
        drop view {{ backup_relation.include(database=False) }}
        end

    if object_id ('{{ backup_relation.include(database=False) }}','U') is not null
        begin
        drop table {{ backup_relation.include(database=False) }}
        end

    rename object {{ existing_relation.include(database=False) }} to {{ backup_relation.identifier }}

    rename object {{ intermediate_relation.include(database=False) }} to {{ existing_relation.identifier }}

{% endmacro %}

{% macro synapse__get_create_materialized_view_as_sql(relation, sql) %}
    {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}

    CREATE materialized view {{ relation.include(database=False) }}
    WITH ( DISTRIBUTION = {{dist}} )
    AS {{ sql }}

{% endmacro %}
