## Quick Start:

[Installation](#installation) • [Usage](#usage) • [Template Syntax](#template-syntax)

### Installation:

```
pip3 install gender-render
```

### Usage:

```python
import gender_render as gr

# use:
rendered_template_as_a_str = gr.render_template(
    template_as_a_string,
    pronoun_data_as_a_string_or_dict
)

# or:
rendered_template_as_a_str = gr.render_template(
    template_file_path,
    pronoun_data_file_path,
    takes_file_path=True
)
```

### Template Syntax:

<table>
<tr>
<td> Template </td> <td> Pronoun Data (json) </td> <td> Result </td>
</tr>

<tr><td>

Addressing one person:
```
Dear {Mr_s Doe},
Yesterday, I was asked about your wellbeing,
"Is there reason to worry about {them}?",
and I told the person why asked that [...]
```

</td><td>

```json
{
    "addressing": "Mrs",
    "family-name": "Smith",
    "object": "her"
}
```

Having more value in the pronoun data than needed is, of course, also allowed!

</td><td>

```
Dear Mrs Smith,
Yesterday, I was asked about your wellbeing,
"Is there reason to worry about her?",
and I told the person why asked that [...]
```

</td></tr>
<tr><td>



</td></tr>

</table>