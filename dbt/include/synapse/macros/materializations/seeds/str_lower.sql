{# in it's own file and macro because #}
{# there is no util available #}
{% macro str_lower(input_string) %}
  {{ return(input_string.lower()) }}
{% endmacro %}
