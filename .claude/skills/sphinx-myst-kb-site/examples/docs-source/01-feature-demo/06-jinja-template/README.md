---
doc_id: xDIvlUxVMdDn
description: "Renders Python data as a Markdown table and as list-tables with sphinx-jinja. A templating demo."
tags: [sphinx, jinja]
---

# Rendering Data with Jinja

The data lives in Python, the document holds only the template. Change the data, rebuild, and every table follows.

## Where the data comes from

`conf.py` defines the data and registers it as the jinja context `doc_data`:

```{literalinclude} ../../conf.py
:language: python
:start-after: "# -- sphinx-jinja"
:end-before: "# -- end sphinx-jinja"
```

The `{jinja}` directive first renders its body with jinja, then parses the result **in the page's own syntax**: MyST in a `.md` page, reST in a `.rst` page.

## Example 1: Markdown table

Template:

````markdown
```{jinja} doc_data
| id | name |
| :--- | :--- |
{% for id, name in doc_data.users -%}
| {{ id }} | {{ name }} |
{% endfor %}
```
````

Result:

```{jinja} doc_data
| id | name |
| :--- | :--- |
{% for id, name in doc_data.users -%}
| {{ id }} | {{ name }} |
{% endfor %}
```

## Example 2: reST list-table

To emit reST from a `.md` page, wrap the rendered text in `{eval-rst}`. In a `.rst` page, write `.. jinja:: doc_data` directly, without `eval-rst`.

Template:

`````markdown
````{jinja} doc_data
```{eval-rst}
.. list-table:: Users
    :header-rows: 1
    :widths: 10 90

    * - id
      - name
{% for id, name in doc_data.users %}
    * - {{ id }}
      - {{ name }}
{% endfor %}
```
````
`````

Result:

````{jinja} doc_data
```{eval-rst}
.. list-table:: Users
    :header-rows: 1
    :widths: 10 90

    * - id
      - name
{% for id, name in doc_data.users %}
    * - {{ id }}
      - {{ name }}
{% endfor %}
```
````

## Example 3: list-table without reST

MyST has its own `{list-table}` directive, with the reST syntax inside a Markdown fence:

````{jinja} doc_data
```{list-table} Users (MyST list-table)
:header-rows: 1

* - id
  - name
{% for id, name in doc_data.users -%}
* - {{ id }}
  - {{ name }}
{% endfor %}
```
````
