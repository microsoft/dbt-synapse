{% macro synapse__get_test_sql(main_sql, fail_calc, warn_if, error_if, limit) -%}
  {% set target_schema = var('synapse_test_schema', generate_schema_name() ) %}

  -- Create target schema in synapse db if it does not
  IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = '{{ target_schema }}')
  BEGIN
    EXEC('CREATE SCHEMA [{{ target_schema }}]')
  END

  {% if main_sql.strip().lower().startswith('with') %}
    {% set testview %}
      {{ target_schema }}.testview_{{ range(1300, 19000) | random }}
    {% endset %}

    {% set sql = main_sql.replace("'", "''")%}
    EXEC('create view {{testview}} as {{ sql }};')
    select
      {{ "top (" ~ limit ~ ')' if limit != none }}
      {{ fail_calc }} as failures,
      case when {{ fail_calc }} {{ warn_if }}
        then 'true' else 'false' end as should_warn,
      case when {{ fail_calc }} {{ error_if }}
        then 'true' else 'false' end as should_error
    from (
      select * from {{testview}}
    ) dbt_internal_test;

    EXEC('drop view {{testview}};')

  {% else -%}
    select
      {{ "top (" ~ limit ~ ')' if limit != none }}
      {{ fail_calc }} as failures,
      case when {{ fail_calc }} {{ warn_if }}
        then 'true' else 'false' end as should_warn,
      case when {{ fail_calc }} {{ error_if }}
        then 'true' else 'false' end as should_error
    from (
      {{ main_sql }}
    ) dbt_internal_test
  {%- endif -%}
{%- endmacro %}
