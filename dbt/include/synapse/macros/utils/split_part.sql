{#
    We have to replace the macro from dbt-sqlserver since that one uses XML which is an unsupported data type in Synapse.
    The function below is not supported in Synapse Dedicated SQL according to the documentation, but it seems to work.
#}
{% macro synapse__split_part(string_text, delimiter_text, part_number) %}

    (select value from string_split({{ string_text }}, {{ delimiter_text }}, 1) where ordinal = {{ part_number }})

{% endmacro %}
