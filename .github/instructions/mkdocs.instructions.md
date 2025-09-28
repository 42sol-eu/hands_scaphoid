---
applyTo: "**/*.md"
---
# Project documentation standards for Markdown

## File Structure
- Use consistent heading hierarchy (`#`, `##`, `###`)
- Include table of contents for long documents
- Add file metadata for design documents:
```markdown
# Document Title
# ---yaml
# file: {{document_name}}.md
# uuid: {{generated-uuid}}
# date: {{modification-date, YYYY-MM-DD}}
# authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
```

## MkDocs Integration
- Follow mkdocs.yml navigation structure
- Use `mkdocstrings` syntax for API documentation:
```markdown
::: module.ClassName
    options:
      show_source: true
```
- Include code examples with proper syntax highlighting
- Use admonitions for important notes: `!!! note`, `!!! warning`

## Code Examples
- Always use proper language identifiers in code blocks
- Include complete, runnable examples when possible
- Show both direct operations and context manager usage:
```python
# Direct operations
File.read_content('path/to/file.txt')

# Context manager approach  
with FileContext('file.txt') as f:
    content = f.read_content()
```

## Documentation Standards
- Document handler patterns with validation examples
- Include registry usage patterns
- Show error handling approaches
- Explain architectural decisions with "why" context
- Link to related API documentation using relative paths
