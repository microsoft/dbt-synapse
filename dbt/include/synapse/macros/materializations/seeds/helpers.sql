{#
    synapse__create_csv_table handles distribution and indexing on
    seed tables over-writing global project macro meterialization.
#}
{% macro synapse__create_csv_table(model, agate_table) %}
    {%- set column_override = model['config'].get('column_types', {}) -%}
    {%- set quote_seed_column = model['config'].get('quote_columns', None) -%}

    {% set sql %}
        create table {{ this.render() }} (
            {%- for col_name in agate_table.column_names -%}
                {%- set inferred_type = adapter.convert_type(agate_table, loop.index0) -%}
                {%- set type = column_override.get(col_name, inferred_type) -%}
                {%- set column_name = (col_name | string) -%}
                {{ adapter.quote_seed_column(column_name, quote_seed_column) }} {{ type }} {%- if not loop.last -%}, {%- endif -%}
            {%- endfor -%}
        )
    {% endset %}

    {#
        The seed table distribution property is defined using {seed file name}_distribution property.
        Read the seed table distribution property provided in dbt project.yml file to get the distribution of a seed table.
    #}
    {% set seed_table_distribution = model['name']~'_distribution' %}

    {#
        If the {seed file name}_distribution value is not available or set to replicate,
        then the distribution of a seed table will be set to REPLICATE
    #}
    {%-if model['config'][seed_table_distribution] is not defined or str_lower(model['config'][seed_table_distribution]) == 'replicate' -%}
        {% set sql_distribution = 'REPLICATE'%}

    {#
        If the {seed file name}_distribution value is set to round_robin,
        then the distribution of a seed table will be set to ROUND_ROBIN
    #}
    {%-elif str_lower(model['config'][seed_table_distribution]) == 'round_robin'  -%}
        {% set sql_distribution = 'ROUND_ROBIN'%}

    {# Consider the distribution of a seed table is hash #}
    {% else %}
        {% set seed_table_hashDistribution_columnName = model['name']~'_hashDistributedColumn' %}

        {#
            checking if distribution column info is defined or not using {seed file name}_hashDistributedColumn property.
            If {seed file name}_hashDistributedColumn is not defined, default the distirbution to REPLICATE.
            Note: Multi Column Distribution strategy is not available
        #}
        {%- if model['config'][seed_table_hashDistribution_columnName] is not defined -%}
            {% set sql_distribution = 'REPLICATE' %}
        {% else %}
            {% set sql_distribution = 'HASH (' ~ model['config'][seed_table_hashDistribution_columnName] ~ ')' %}
        {%- endif -%}
    {%- endif -%}

    {#
        The seed table index property is defined using {seed file name}_index property.
        Read the seed table index property provided in dbt project.yml file to get the index of a seed table.
    #}
    {% set seed_table_index = model['name']~'_index' %}

    {#
        If the {seed file name}_index value is not available or set to heap,
        then the index of a seed table will be set to HEAP
    #}
    {%-if model['config'][seed_table_index] is not defined or str_lower(model['config'][seed_table_index]) == 'heap' -%}
        {% set sql_index = 'HEAP'%}

    {#
        If the {seed file name}_index value is set to cci,
        then the index of a seed table will be set to CLUSTERED COLUMNSTORE INDEX
    #}
    {%-elif str_lower(model['config'][seed_table_index]) == 'cci' -%}
        {% set sql_index = 'CLUSTERED COLUMNSTORE INDEX' %}

    {# Clustered Index #}
    {% else %}

        {% set seed_table_ci_columns = model['name']~'_ciIndexColumns' %}

        {#
            If the {seed file name}_ciIndexColumns value is not defined,
            then the index of a seed table will default to HEAP
        #}
        {%- if model['config'][seed_table_ci_columns] is not defined -%}
            {% set sql_index = 'HEAP'%}
        {% else %}
            {% set sql_index = 'CLUSTERED INDEX (' ~ model['config'][seed_table_ci_columns] ~ ')' %}
        {%- endif -%}
    {%- endif -%}

    {# Combining SQL Text with Distribution and index provided in dbt project.yml file #}
    {% set sql = sql ~ ' ' ~ 'WITH ( DISTRIBUTION = ' ~ sql_distribution ~ ', ' ~ sql_index ~ ')' %}

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
