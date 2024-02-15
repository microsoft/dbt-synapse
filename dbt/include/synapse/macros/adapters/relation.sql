{% macro synapse__drop_relation(relation) -%}
  {% call statement('drop_relation', auto_begin=False) -%}
    {{ synapse__drop_relation_script(relation) }}
  {%- endcall %}
{% endmacro %}

{% macro synapse__drop_relation_script(relation) -%}
  {% if relation.type == 'view' or relation.type == 'materialized_view' -%}
    {% set object_id_type = 'V' %}
  {% elif relation.type == 'table'%}
    {% set object_id_type = 'U' %}
  {%- else -%} invalid target name
  {% endif %}

  if object_id ('{{ relation.include(database=False) }}','{{ object_id_type }}') is not null
  {% if relation.type == 'view' or relation.type == 'materialized_view' -%}
    begin
    drop view {{ relation.include(database=False) }}
    end
  {% elif relation.type == 'table' %}
    begin
    drop {{ relation.type }} {{ relation.include(database=False) }}
    end
  {% endif %}
{% endmacro %}

{% macro synapse__rename_relation(from_relation, to_relation) -%}
  {# dbt needs this 'call' macro, but it overwrites other SQL when reused in other macros #}
  {# so '_script' macro is reuseable script, for other macros to combine with more SQL #}

  {% call statement('rename_relation') %}
    {{ synapse__rename_relation_script(from_relation, to_relation) }}
  {%- endcall %}
{% endmacro %}

{% macro synapse__rename_relation_script(from_relation, to_relation) -%}
  -- drop all object types with to_relation.identifier name, to avoid error "new name already in use...duplicate...not permitted"
  if object_id ('{{ to_relation.include(database=False) }}','V') is not null
    begin
    drop view {{ to_relation.include(database=False) }}
    end

  if object_id ('{{ to_relation.include(database=False) }}','U') is not null
    begin
    drop table {{ to_relation.include(database=False) }}
    end

  rename object {{ from_relation.include(database=False) }} to {{ to_relation.identifier }}
{% endmacro %}

{% macro synapse__truncate_relation(relation) %}
    {% call statement('truncate_relation') -%}
      truncate table {{ relation }}
    {%- endcall %}
{% endmacro %}
