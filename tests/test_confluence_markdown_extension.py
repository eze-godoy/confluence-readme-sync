import unittest
from src.confluence_markdown_extension import *
from unittest.mock import patch

class TestSectionLinkPreprocessor(unittest.TestCase):
    def test_run(self):
        lines: list[str] = [
            " - [How to debug](##How-to-debug)",
            "  - [Deploy the app](###header3)",
            "- [Header](#header1)"
        ]
        processed_lines = SectionLinkPreprocessor().run(lines)
        self.assertEqual(processed_lines, [
            " - [How to debug](#How-to-debug)",
            "  - [Deploy the app](#header3)",
            "- [Header](#header1)"
        ])

class TestIndentedCodeBlockPreprocessor(unittest.TestCase):
    def setUp(self):
        self.preprocessor = IndentedCodeBlockPreprocessor()
    
    def test_run_with_indented_fenced_code_block(self):
        lines = [
            "1. Copy your chosen template:",
            "   ```bash",
            "   cp template.json repositories/my-new-service.json",
            "   ```",
            "2. Next step"
        ]
        processed_lines = self.preprocessor.run(lines)
        expected = [
            "1. Copy your chosen template:",
            "```bash",
            "cp template.json repositories/my-new-service.json",
            "```",
            "2. Next step"
        ]
        self.assertEqual(processed_lines, expected)
    
    def test_run_with_multiple_indented_code_blocks(self):
        lines = [
            "Step 1:",
            "   ```python",
            "   def hello():",
            "       print('world')",
            "   ```",
            "",
            "Step 2:",
            "    ```json",
            "    {\"key\": \"value\"}",
            "    ```"
        ]
        processed_lines = self.preprocessor.run(lines)
        expected = [
            "Step 1:",
            "```python",
            "def hello():",
            "    print('world')",
            "```",
            "",
            "Step 2:",
            "```json",
            "{\"key\": \"value\"}",
            "```"
        ]
        self.assertEqual(processed_lines, expected)

class TestCodeBlockPostprocessor(unittest.TestCase):
    def setUp(self):
        self.postprocessor = CodeBlockPostprocessor()
    def test_run(self):
        text = "<pre><code class=\"language-shell\">ping github.com/gabesw</code></pre>"
        processed_text = self.postprocessor.run(text)
        self.assertEqual(processed_text, "<ac:structured-macro ac:name=\"code\"><ac:parameter ac:name=\"language\">shell</ac:parameter><ac:plain-text-body><![CDATA[ping github.com/gabesw]]></ac:plain-text-body></ac:structured-macro>")
    
    def test_run_with_html_entities(self):
        text = "<pre><code class=\"language-json\">{&quot;name&quot;: &quot;value&quot;}</code></pre>"
        processed_text = self.postprocessor.run(text)
        self.assertEqual(processed_text, "<ac:structured-macro ac:name=\"code\"><ac:parameter ac:name=\"language\">json</ac:parameter><ac:plain-text-body><![CDATA[{\"name\": \"value\"}]]></ac:plain-text-body></ac:structured-macro>")
    
    def test_run_without_language(self):
        text = "<pre><code>echo 'hello world'</code></pre>"
        processed_text = self.postprocessor.run(text)
        self.assertEqual(processed_text, "<ac:structured-macro ac:name=\"code\"><ac:parameter ac:name=\"language\">none</ac:parameter><ac:plain-text-body><![CDATA[echo 'hello world']]></ac:plain-text-body></ac:structured-macro>")
    
    def test_run_with_indented_code(self):
        text = "<pre><code class=\"language-bash\">   cp template.json repositories/my-new-service.json\n   cd repositories</code></pre>"
        processed_text = self.postprocessor.run(text)
        self.assertEqual(processed_text, "<ac:structured-macro ac:name=\"code\"><ac:parameter ac:name=\"language\">shell</ac:parameter><ac:plain-text-body><![CDATA[   cp template.json repositories/my-new-service.json\n   cd repositories]]></ac:plain-text-body></ac:structured-macro>")
    
    def test_run_with_mixed_indentation(self):
        text = "<pre><code class=\"language-python\">    def hello():\n        print(&quot;world&quot;)\n    \n    hello()</code></pre>"
        processed_text = self.postprocessor.run(text)
        self.assertEqual(processed_text, "<ac:structured-macro ac:name=\"code\"><ac:parameter ac:name=\"language\">python</ac:parameter><ac:plain-text-body><![CDATA[    def hello():\n        print(\"world\")\n    \n    hello()]]></ac:plain-text-body></ac:structured-macro>")

class TestConfluenceExtension(unittest.TestCase):
    def test_extend_markdown(self):
        md = Markdown()
        confluence_extension = ConfluenceExtension()
        confluence_extension.extendMarkdown(md)
        self.assertTrue(confluence_extension in md.registeredExtensions, "Extension is registered")
        self.assertTrue('confluence_indented_code_blocks' in md.preprocessors, "Indented code blocks preprocessor is registered")
        self.assertTrue('confluence_section_links' in md.preprocessors, "Section links preprocessor is registered")
        self.assertTrue('confluence_code_block' in md.postprocessors, "Code block postprocessor is registered")

class TestMakeExtension(unittest.TestCase):
    def test_make_extension(self):
        extension = makeExtension()
        self.assertIsInstance(extension, ConfluenceExtension)