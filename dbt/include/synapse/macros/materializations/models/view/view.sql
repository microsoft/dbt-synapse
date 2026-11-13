{#
  Dedicated SQL pools can't rename views, so the default rename-and-swap fails when the view
  already exists. Alter it in place instead, which also keeps its permissions.
#}
{% materialization view, adapter='synapse' %}
  {%- set target_relation = this.incorporate(type='view') -%}
  {%- set existing_relation = load_cached_relation(this) -%}
  {%- set grant_config = config.get('grants') -%}

  {{ run_hooks(pre_hooks, inside_transaction=False) }}
  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {% if existing_relation is not none and not existing_relation.is_view %}
    {% do adapter.drop_relation(existing_relation) %}
    {% set existing_relation = none %}
  {% endif %}

  {% call statement('main') -%}
    {% if existing_relation is none %}
      {{ get_create_view_as_sql(target_relation, sql) }}
    {% else %}
      {{ synapse__alter_view_as(target_relation, sql) }}
    {% endif %}
  {%- endcall %}

  {% set should_revoke = should_revoke(existing_relation, full_refresh_mode=True) %}
  {% do apply_grants(target_relation, grant_config, should_revoke=should_revoke) %}

  {% do persist_docs(target_relation, model) %}
  {{ run_hooks(post_hooks, inside_transaction=True) }}
  {{ adapter.commit() }}
  {{ run_hooks(post_hooks, inside_transaction=False) }}
  {{ return({'relations': [target_relation]}) }}
{% endmaterialization %}
