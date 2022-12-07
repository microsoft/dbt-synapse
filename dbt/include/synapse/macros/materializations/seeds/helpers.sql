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