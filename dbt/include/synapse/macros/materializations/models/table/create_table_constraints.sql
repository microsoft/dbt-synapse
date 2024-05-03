{% macro synapse__build_columns_constraints(relation) %}
  {# loop through user_provided_columns to create DDL with data types and constraints #}
    {%- set raw_column_constraints = adapter.render_raw_columns_constraints(raw_columns=model['columns']) -%}
    (
      {% for c in raw_column_constraints -%}
        {{ c }}{{ "," if not loop.last }}
      {% endfor %}
    )
{% endmacro %}

{% macro synapse__build_model_constraints(relation) %}
  {# loop through user_provided_columns to create DDL with data types and constraints #}
    {%- set raw_model_constraints = adapter.render_raw_model_constraints(raw_constraints=model['constraints']) -%}
    {% for c in raw_model_constraints -%}
        alter table {{ relation }} {{c}};
    {% endfor -%}
{% endmacro %}
