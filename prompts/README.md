# Prompts for the Iterated Prisoner's Dilemma

Templated prompts use Jinja2. An example:

```python
from jinja2 import Template

# Define the path to the file
file_path = "/prompts/simple_ipd_template.txt"

# Read the content of the file into a string
with open(file_path, 'r') as f:
    prompt_template = f.read()

# Create a jinja2 template from the string
template = Template(prompt_template)

# Render the template with specific values for payoffs, history, and examples
rendered_prompt = template.render(
    cooperate_cooperate=3,
    defect_defect=1,
    cooperate_defect=0,
    defect_cooperate=5,
    current_history=[],
    examples=[
        {"history": "[(C, C), (C, D)]", "response": "D"},
        {"history": "[]", "response": "C"}
    ]
)

print(rendered_prompt)
```

The user can change the payoffs of the game, set the current state of the game via the history, or potentially change model behavior by adjusting the examples of gameplay given (e.g, one could pass examples of Tit-for-Tat play vs. grim trigger).