"""
An extension for the `python-markdown <https://pypi.org/project/Markdown/>`_ package that formats certain elements for Confluence
pages in a nicer way than pure markdown.
"""

import re
import html
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from markdown import Markdown

class SectionLinkPreprocessor(Preprocessor):
    """
    A preprocessor that removes extra hashtags before section links.
    """
    def run(self, lines: list[str]) -> list[str]:
        """
        Removes extra hashtags before section links such that they have only one hashtag.
        """
        modified_lines: list[str] = []
        for line in lines:
            # replace links to sections on the page with one hashtag instead of multiple to work in confluence urls
            modified_lines.append(re.sub(r'\]\(#+', r'](#', line, flags=re.DOTALL))
        return modified_lines

class CodeBlockPostprocessor(Postprocessor):
    """
    A postprocessor that reformats HTML code blocks to Confluence code snippet macros.
    """
    def run(self, text: str) -> str:
        """
        Replaces HTML code blocks with Confluence code snippet macros with language support.
        """
        def decode_and_wrap(match):
            """Helper function to decode HTML entities, remove indentation, and wrap in CDATA"""
            language = match.group(1) if match.lastindex >= 1 else "none"
            code_content = match.group(2) if match.lastindex >= 2 else match.group(1)
            # Decode HTML entities in the code content
            decoded_content = html.unescape(code_content)
            # Remove common indentation from all lines
            lines = decoded_content.split('\n')
            if len(lines) > 1:
                # Find the minimum indentation (excluding empty lines)
                non_empty_lines = [line for line in lines if line.strip()]
                if non_empty_lines:
                    min_indent = min(len(line) - len(line.lstrip()) for line in non_empty_lines)
                    # Remove the common indentation from all lines
                    lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]
                    decoded_content = '\n'.join(lines)
            return f'<ac:structured-macro ac:name="code"><ac:parameter ac:name="language">{language}</ac:parameter><ac:plain-text-body><![CDATA[{decoded_content}]]></ac:plain-text-body></ac:structured-macro>'
        
        # First, handle code blocks with language specification
        processed_text = re.sub(
            r'<pre><code class="language-(\w+)">(.*?)</code></pre>', 
            decode_and_wrap,
            text,
            flags=re.DOTALL
        )
        
        # Then handle code blocks without language specification
        processed_text = re.sub(
            r'<pre><code>(.*?)</code></pre>', 
            decode_and_wrap,
            processed_text,
            flags=re.DOTALL
        )
        
        # Map certain languages to supported confluence languages
        if processed_text != text:
            processed_text = re.sub(
                r'<ac:parameter ac:name="language">bash</ac:parameter>', 
                r'<ac:parameter ac:name="language">shell</ac:parameter>', 
                processed_text,
                flags=re.DOTALL
            )
        return processed_text

class ConfluenceExtension(Extension):
    """
    The extension to be included in the `extensions` argument of the :ref:`Markdown.markdown` function.
    """
    def extendMarkdown(self, md: Markdown):
        """
        Adds the processors to the extension.
        """
        md.registerExtension(self)
        md.preprocessors.register(SectionLinkPreprocessor(md), 'confluence_section_links', 0)
        md.postprocessors.register(CodeBlockPostprocessor(md), 'confluence_code_block', 0)

def makeExtension(*args, **kwargs):
    """
    Initializes the Confluence extension.
    """
    return ConfluenceExtension(*args, **kwargs)
