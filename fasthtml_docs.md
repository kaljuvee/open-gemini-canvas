# FastHTML Migration Guide

## Framework Overview
FastHTML is a python library which brings together Starlette, Uvicorn, HTMX, and fastcore's `FT` "FastTags" into a library for creating server-rendered hypermedia applications.

## Key Components

### FastTags (FT)
- Components are created as functions returning FT trees
- Examples: `Title("FastHTML")`, `H1("My web app")`, `P("Hello")`
- FT components handle attributes via named parameters
- Special handling for classes (`cls`), reserved words, and nested components

### Routing
- Decorator-based routing with `@rt` above functions
- Route handlers can return FT components, tuples, or standard Starlette responses

### Migration Patterns from React/Next.js

1. **Components**: Replace React components with FT functions that return FT trees
2. **State Management**: Replace client-side state with server-side route handlers
3. **Interactivity**: Use HTMX attributes (`hx-get`, `hx-post`, `hx-trigger`) for dynamic behavior
4. **Routing**: Use `@rt` decorators instead of React router
5. **Forms**: Use `fill_form` and form data binding instead of React forms

### Key Differences
- Server-rendered instead of client-rendered
- HTMX for interactivity instead of JavaScript
- Python functions instead of React components
- Decorator-based routing instead of client-side routing

### Basic App Structure
```python
from fasthtml.common import *

app, rt = fast_app()

@rt("/")
def get():
    return Titled("FastHTML", 
        H1("My web app"),
        P("Hello")
    )

serve()
```

### Important Notes
- FastHTML is compatible with JS-native web components and vanilla JS
- NOT compatible with React, Vue, or Svelte
- Use `serve()` for running uvicorn
- Use `Titled` when a title is needed with response
