from collections import OrderedDict

## this is called to prompts dir

class PromptBuilder:
    def __init__(self, sections: OrderedDict):
        self.sections = sections

    def build(self) -> str:
        return "\n\n".join(self.sections.values())

    def override(self, **kwargs) -> 'PromptBuilder':
        new_sections = self.sections.copy()
        new_sections.update(kwargs)
        return PromptBuilder(new_sections)
