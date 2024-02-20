{% macro synapse__create_table_as(temporary, relation, sql) -%}
   {%- set index = config.get('index', default="CLUSTERED COLUMNSTORE INDEX") -%}
   {%- set dist = config.get('dist', default="ROUND_ROBIN") -%}
   {% set tmp_relation = relation.incorporate(
   path={"identifier": relation.identifier.replace("#", "") ~ '_temp_view'},
   type='view')-%}
   {%- set temp_view_sql = sql.replace("'", "''") -%}

   {{ synapse__drop_relation_script(tmp_relation) }}

   {{ synapse__drop_relation_script(relation) }}

   {{ synapse__create_view_as(tmp_relation, sql) }}

   {% set contract_config = config.get('contract') %}

   {% if contract_config.enforced %}

        {{exceptions.warn("Model contracts cannot be enforced by <adapter>!")}}

        CREATE TABLE [{{relation.schema}}].[{{relation.identifier}}]
        {{ synapse__build_columns_constraints(tmp_relation) }}
        WITH(
          DISTRIBUTION = {{dist}},
          {{index}}
        )
        {{ get_assert_columns_equivalent(sql)  }}

        {% set listColumns %}
            {% for column in model['columns'] %}
                {{ "["~column~"]" }}{{ ", " if not loop.last }}
            {% endfor %}
        {%endset%}
        {{ synapse__build_model_constraints(relation) }}

        INSERT INTO [{{relation.schema}}].[{{relation.identifier}}]
        ({{listColumns}}) SELECT {{listColumns}} FROM [{{tmp_relation.schema}}].[{{tmp_relation.identifier}}]

    {%- else %}
        EXEC('CREATE TABLE [{{relation.database}}].[{{relation.schema}}].[{{relation.identifier}}]WITH(DISTRIBUTION = {{dist}},{{index}}) AS (SELECT * FROM [{{tmp_relation.database}}].[{{tmp_relation.schema}}].[{{tmp_relation.identifier}}]);');
    {% endif %}

   {{ synapse__drop_relation_script(tmp_relation) }}

{% endmacro %}
