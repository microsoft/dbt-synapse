{% macro synapse__get_catalog_tables_sql(information_schemas) -%}
-- avoid with statement to be able to wrap into CTE (limitation of Synapse)

    SELECT
        table_name,
        table_schema,
        principal_name,
        table_type
    FROM (
        SELECT
            table_name,
            schema_name AS table_schema,
            COALESCE(relations.principal_id, schemas.principal_id) AS owner_principal_id,
            table_type
        FROM (
            SELECT
                name AS table_name,
                schema_id AS schema_id,
                principal_id AS principal_id,
                'BASE TABLE' AS table_type
            FROM
                sys.tables {{ information_schema_hints() }}
            UNION ALL
            SELECT
                name AS table_name,
                schema_id AS schema_id,
                principal_id AS principal_id,
                'VIEW' AS table_type
            FROM
                sys.views {{ information_schema_hints() }}
        ) AS relations
        JOIN (
            SELECT
                name AS schema_name,
                schema_id AS schema_id,
                principal_id AS principal_id
            FROM
                sys.schemas {{ information_schema_hints() }}
        ) AS schemas ON relations.schema_id = schemas.schema_id
    ) AS relations_with_metadata
    JOIN (
        SELECT
            name AS principal_name,
            principal_id AS principal_id
        FROM
            sys.database_principals {{ information_schema_hints() }}
    ) AS principals ON relations_with_metadata.owner_principal_id = principals.principal_id

{% endmacro %}

{% macro synapse__get_catalog_columns_sql(information_schemas) -%}

    select
        table_catalog as table_database,
        table_schema,
        table_name,
        column_name,
        ordinal_position as column_index,
        data_type as column_type
    from INFORMATION_SCHEMA.COLUMNS {{ information_schema_hints() }}

{% endmacro %}

{% macro synapse__get_catalog_schemas_where_clause_sql(schemas) -%}
    where ({%- for schema in schemas -%}
        upper(table_schema) = upper('{{ schema }}'){%- if not loop.last %} or {% endif -%}
    {%- endfor -%})
{%- endmacro %}

{% macro synapse__get_catalog_relations_where_clause_sql(relations) %}

    where (
        {%- for relation in relations -%}
            {% if relation.schema and relation.identifier %}
                (
                    upper(table_schema) = upper('{{ relation.schema }}')
                    and upper(table_name) = upper('{{ relation.identifier }}')
                )
            {% elif relation.schema %}
                (
                    upper(table_schema) = upper('{{ relation.schema }}')
                )
            {% else %}
                {% do exceptions.raise_compiler_error(
                    '`get_catalog_relations` requires a list of relations, each with a schema'
                ) %}
            {% endif %}

            {%- if not loop.last %} or {% endif -%}
        {%- endfor -%}
    )

{% endmacro %}

{% macro synapse__get_catalog_results_sql() -%}
    select
        cols.table_database,
        tv.table_schema,
        tv.table_name,
        tv.table_type,
        null as table_comment,
        tv.principal_name as table_owner,
        cols.column_name,
        cols.column_index,
        cols.column_type,
        null as column_comment
    from tables as tv
    join columns as cols on tv.table_schema = cols.table_schema and tv.table_name = cols.table_name
    order by cols.column_index
{%- endmacro %}

-- combine everything into the get_catalog_(relations) macro
{% macro synapse__get_catalog(information_schema, schemas) -%}

    {% set query %}
        with tables as (
            {{ synapse__get_catalog_tables_sql(information_schema) }}
            {{ synapse__get_catalog_schemas_where_clause_sql(schemas) }}
        ),
        columns as (
            {{ synapse__get_catalog_columns_sql(information_schema) }}
            {{ synapse__get_catalog_schemas_where_clause_sql(schemas) }}
        )
        {{ synapse__get_catalog_results_sql() }}
    {%- endset -%}

    {{ return(run_query(query)) }}

{%- endmacro %}

{% macro synapse__get_catalog_relations(information_schema, relations) -%}

    {% set query %}
        with tables as (
            {{ synapse__get_catalog_tables_sql(information_schema) }}
            {{ synapse__get_catalog_relations_where_clause_sql(relations) }}
        ),
        columns as (
            {{ synapse__get_catalog_columns_sql(information_schema) }}
            {{ synapse__get_catalog_relations_where_clause_sql(relations) }}
        )
        {{ synapse__get_catalog_results_sql() }}
    {%- endset -%}

    {{ return(run_query(query)) }}

{%- endmacro %}
