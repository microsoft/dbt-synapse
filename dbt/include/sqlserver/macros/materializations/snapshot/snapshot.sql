{% macro sqlserver__post_snapshot(staging_relation) %}
  -- Clean up the snapshot temp table
  {% do drop_relation(staging_relation) %}
{% endmacro %}


{% macro sqlserver__snapshot_merge_sql(target, source, insert_cols) -%}
      {{ log("insert_cols " ~ insert_cols)}}
      
      EXEC('  update {{ target }}
          set dbt_valid_to = TMP.dbt_valid_to
          from {{ source }} TMP
          where {{ target }}.dbt_scd_id = TMP.dbt_scd_id
            and TMP.dbt_change_type = ''update''
            and {{ target }}.dbt_valid_to is null;

            insert into {{ target }}
            select country_name,pto_total,dbt_scd_id,dbt_updated_at,dbt_valid_from,dbt_valid_to
            from {{ source }} 
            where dbt_change_type = ''insert'' ; ');


{% endmacro %}

{% materialization snapshot, default %}
  {%- set config = model['config'] -%}

  {%- set target_table = model.get('alias', model.get('name')) -%}

  {%- set strategy_name = config.get('strategy') -%}
  {%- set unique_key = config.get('unique_key') %}

  {% if not adapter.check_schema_exists(model.database, model.schema) %}
    {% do create_schema(model.database, model.schema) %}
  {% endif %}

  {% set target_relation_exists, target_relation = get_or_create_relation(
          database=model.database,
          schema=model.schema,
          identifier=target_table,
          type='table') -%}

  {%- if not target_relation.is_table -%}
    {% do exceptions.relation_wrong_type(target_relation, 'table') %}
  {%- endif -%}


  {{ run_hooks(pre_hooks, inside_transaction=False) }}

  {{ run_hooks(pre_hooks, inside_transaction=True) }}

  {% set strategy_macro = strategy_dispatch(strategy_name) %}
  {% set strategy = strategy_macro(model, "snapshotted_data", "source_data", config, target_relation_exists) %}

  {% if not target_relation_exists %}

      {% set build_sql = build_snapshot_table(strategy, model['injected_sql']) %}
      {% set final_sql = create_table_as(False, target_relation, build_sql) %}

       {% call statement('main') %}
      {{ final_sql }}
      {% endcall %}

  {% else %}

      {{ adapter.valid_snapshot_target(target_relation) }}

      {% set staging_table = build_snapshot_staging_table(strategy, sql, target_relation) %}

      {% set nandan_table = create_table_as(False, 'ajs.nandan_fake_temp', 'select * from {{staging_table}}') %}

      -- this may no-op if the database does not require column expansion
      {% do adapter.expand_target_column_types(from_relation=staging_table,
                                               to_relation=target_relation) %}

      {% set missing_columns = adapter.get_missing_columns(nandan_table, target_relation)
                                   | rejectattr('name', 'equalto', 'dbt_change_type')
                                   | rejectattr('name', 'equalto', 'DBT_CHANGE_TYPE')
                                   | rejectattr('name', 'equalto', 'dbt_unique_key')
                                   | rejectattr('name', 'equalto', 'DBT_UNIQUE_KEY')
                                   | list %}

      {% do create_columns(target_relation, missing_columns) %}

      {% set source_columns = adapter.get_columns_in_relation(nandan_table)
                                   | rejectattr('name', 'equalto', 'dbt_change_type')
                                   | rejectattr('name', 'equalto', 'DBT_CHANGE_TYPE')
                                   | rejectattr('name', 'equalto', 'dbt_unique_key')
                                   | rejectattr('name', 'equalto', 'DBT_UNIQUE_KEY')
                                   | list %}
      {{ log("wwww staging_table is" ~ staging_table)}}
      {% set quoted_source_columns = [] %}
      {{ log("wwww source columns are" ~ source_columns)}}
      {% for column in source_columns %}
        {% do quoted_source_columns.append(adapter.quote(column.name)) %}
      {% endfor %}

      {% do snapshot_merge_sql(
            target = target_relation,
            source = nandan_table,
            insert_cols = quoted_source_columns
         )
      %}

      {% do drop_relation(nandan_table) %}

  {% endif %}

  {% do persist_docs(target_relation, model) %}

  {{ run_hooks(post_hooks, inside_transaction=True) }}

  {{ adapter.commit() }}

  {% if staging_table is defined %}
      {% do post_snapshot(staging_table) %}
  {% endif %}

  {{ run_hooks(post_hooks, inside_transaction=False) }}

  {{ return({'relations': [target_relation]}) }}

{% endmaterialization %}
