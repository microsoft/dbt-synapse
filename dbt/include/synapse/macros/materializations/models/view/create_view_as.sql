{% macro synapse__create_view_as(relation, sql) -%}
  create view {{ relation.include(database=False) }} as
    {{ sql }}
{% endmacro %}
