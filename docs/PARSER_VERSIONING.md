# Parser Versioning Policy

Document Version: 1.0.0 (Phase 4 Parser)  
Status: Approved & Implemented  

---

```text
parser_version = "1.0.0"
contract_version = "1.0.0"
```

## Version Bump Rules
- **Patch Bumps (1.0.x)**: Internal performance optimizations, non-behavioral refactoring.
- **Minor Bumps (1.x.0)**: Backward-compatible token additions or regex pattern expansions.
- **Major Bumps (x.0.0)**: Breaking changes to output wire schema, classification categories, or field names.
