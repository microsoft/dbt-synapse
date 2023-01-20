{#
    synapse__create_csv_table handles distribution and indexing on
    seed tables over-writing global project macro meterialization.
#}
{% macro synapse__create_csv_table(model, agate_table) %}
    {%- set column_override = config.get('column_types', {}) -%}
    {%- set quote_seed_column = config.get('quote_columns', None) -%}
    {%- set index = config.get('index', "HEAP") -%}
    {%- set dist = config.get('dist', "ROUND_ROBIN") -%}

    {% set sql %}
        create table {{ this.render() }} (
            {%- for col_name in agate_table.column_names -%}
                {%- set inferred_type = adapter.convert_type(agate_table, loop.index0) -%}
                {%- set type = column_override.get(col_name, inferred_type) -%}
                {%- set column_name = (col_name | string) -%}
                {{ adapter.quote_seed_column(column_name, quote_seed_column) }} {{ type }} {%- if not loop.last -%}, {%- endif -%}
            {%- endfor -%}
        )
        WITH (DISTRIBUTION = {{dist}}, {{index}})
    {% endset %}

    {% call statement('_') -%}
        {{ sql }}
    {%- endcall %}

{% endmacro %}

{% macro synapse__load_csv_rows(model, agate_table) %}

    {# Synapse does not support the normal Table Value Constructor #}

    {% set batch_size = get_batch_size() %}

    {% set cols_sql = get_seed_column_quoted_csv(model, agate_table.column_names) %}

    {% set statements = [] %}

    {% for chunk in agate_table.rows | batch(batch_size) %}

        {% set sql %}
            insert into {{ this.render() }} ({{ cols_sql }})
            {% for row in chunk -%}
                {{'select'+' '}}
                {%- for column in agate_table.column_names -%}
                    {#
                        TSQL catch 22:
                        strings must be single-quoted &
                        single-quotes inside of strings must be doubled
                    #}

                    {% set col_type = agate_table.columns[column].data_type | string %}
                    {#
                        None should result in NULL, If the value in the seed file is 0, the database entry should 0
                    #}
                    {%-if None == row[column]-%}
                        NULL
                    {%-elif (("text.Text" in col_type))-%}
                        '{{str_replace(row[column])}}'
                    {#
                        else handles all other data types such as Date, DateTime, Int, Float (Numeric and Decimal is treated as float)
                        int, float are implicit conversions
                    #}
                    {% else %}
                        '{{row[column]}}'
                    {%- endif -%}
                    {%- if not loop.last%},{%- endif -%}
                {%- endfor -%}
                {%- if not loop.last -%} {{' '+'union all'+'\n'}} {%- endif -%}
            {%- endfor -%}
        {% endset %}
        {% do adapter.add_query(sql, abridge_sql_log=True) %}

        {% if loop.index0 == 0 %}
            {% do statements.append(sql) %}
        {% endif %}
    {% endfor %}

    {# Return SQL so we can render it out into the compiled files #}
    {{ return(statements[0]) }}
{% endmacro %}
