{% macro ref(model_name) %}

    {% do return(builtins.ref(model_name).include(database=false)) %}

{% endmacro %}

{% macro synapse__get_create_materialized_view_as_sql(relation, sql) %}
    {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}

    CREATE materialized view {{ relation.include(database=False) }}
    WITH ( DISTRIBUTION = {{dist}} )
    AS {{ sql }};

{% endmacro %}
