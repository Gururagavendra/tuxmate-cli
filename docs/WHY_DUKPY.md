# Why dukpy?

The `data.ts` file from tuxmate's repository contains JavaScript function calls like `si('firefox', '#FF7139')` for icon URLs. Simple regex or JSON parsers fail to handle these dynamic expressions.

## The Problem

Tuxmate's `data.ts` is a TypeScript file with:
- Function calls: `si()`, `lo()`, `mdi()`, etc.
- Template literals and expressions
- Object shorthand syntax
- Trailing commas
- Dynamic icon references

Example from `data.ts`:
```typescript
{
  id: 'firefox',
  name: 'Firefox',
  icon: si('firefox', '#FF7139'),
  targets: { ... }
}
```

## The Solution

`dukpy` is a Python JavaScript interpreter that evaluates the actual JavaScript code, allowing us to:
- Execute function calls and return their values
- Parse complex JavaScript syntax
- Handle dynamic expressions
- Extract both `apps` and `distros` arrays accurately

## Alternatives Considered

- **Regex parsing**: Fails on nested objects and function calls
- **JSON parsing**: `data.ts` is not valid JSON
- **Manual conversion**: Would require constant maintenance as tuxmate updates
- **Node.js subprocess**: Adds heavy dependency, defeats Python-native goal

## Implementation

```python
import dukpy

# Evaluate JavaScript and extract data
result = dukpy.evaljs("""
    // Define icon helper functions
    function si(name, color) { return 'simpleicons:' + name; }
    function lo(name) { return 'logos:' + name; }

    // Load data.ts content
    """ + data_ts_content + """

    // Return parsed data
    JSON.stringify({ apps: apps, distros: distros });
""")
```

This approach ensures tuxmate-cli stays synchronized with tuxmate's data format without manual intervention.

## Future Migration

While dukpy works well for our current needs, we plan to migrate to **PythonMonkey** in a future release:

- **Modern JS engine**: Uses SpiderMonkey (Mozilla Firefox's JavaScript engine)
- **Active maintenance**: Regular updates and security patches (last updated 2024)
- **Better security**: More robust sandboxing and modern JS feature support
- **API compatibility**: Similar `eval()` API makes migration straightforward

The migration is planned as a low-priority improvement since dukpy is functioning correctly. See the [Roadmap in README.md](../README.md#roadmap) for current status.
