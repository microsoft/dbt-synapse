{# in it's own file and macro because #}
{# the quoted quotes breaks the formatting for seed.sql #}
{% macro str_replace(input_string) %}
  {{ return(input_string.replace("'","''")) }}
{% endmacro %}