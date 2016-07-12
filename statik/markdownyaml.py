# -*- coding:utf-8 -*-

import yaml
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension

__all__ = [
    'MarkdownYamlMetaExtension',
    'MarkdownYamlMetaPreprocessor',
]


class MarkdownYamlMetaExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add(
            'yaml-meta',
            MarkdownYamlMetaPreprocessor(md),
            ">normalize_whitespace",
        )


class MarkdownYamlMetaPreprocessor(Preprocessor):

    def run(self, lines):
        result = []
        self.markdown.meta = {}

        if len(lines) > 1:
            yaml_lines = []
            if lines[0].strip() == '---':
                collecting_yaml = True
                start_line = 1
            else:
                collecting_yaml = False
                start_line = 0

            for line in lines[start_line:]:
                if collecting_yaml:
                    if line.strip() == '---':
                        collecting_yaml = False
                    else:
                        yaml_lines.append(line)
                else:
                    result.append(line.encode("ascii", "xmlcharrefreplace").decode("utf-8"))

            if len(yaml_lines) > 0:
                self.markdown.meta = yaml.load(
                    '\n'.join(yaml_lines).encode("ascii", "xmlcharrefreplace").decode("utf-8")
                )

        return result
