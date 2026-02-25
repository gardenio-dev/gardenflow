# Feature: File Management Service

## Context

Gardenflow needs a tenant-aware file management service to support archiving
and extracting files within tenant home directories. This is a foundational
capability for DAG workflows that produce or consume file artifacts.

The service follows the established pattern from `gardenflow.core.gardenio`:
an abstract base class with a local-filesystem implementation, leaving room
for future backends (S3, etc.).

---

## Design Decisions

| Decision | Choice |
|---|---|
| Tenant path resolution | `{settings.home}/{tenant}/{relative_path}` |
| Path argument type | `Path`, always relative to tenant home |
| Absolute path handling | Raise `ValueError` |
| Path traversal (`..`) | Raise `ValueError` |
| Callback style | `Callable[[Path], None] \| None = None` (optional, not generator) |
| Callback path values | Relative to tenant home (consistent with inputs/outputs) |
| `archive()` return | `Path` to the created zip (relative to tenant home) |
| `extract()` return | `Path` to the extraction directory (relative to tenant home) |
| All return values | Always relative to tenant home — `_resolve()` is internal only |
| Settings env var | `GARDENFLOW__FILES__LOCAL__HOME` |

---

## Module Structure

```
gardenflow/core/files/
├── __init__.py
├── services.py             FilesService — abstract base
├── settings.py             FilesSettings + FilesClientKind enum
└── local/
    ├── __init__.py
    ├── services.py         LocalFilesService — local filesystem impl
    └── settings.py         LocalFilesSettings (GARDENFLOW__FILES__LOCAL__HOME)
```

---

## Progress

- [x] `features/files/FEATURE.md` — this document
- [x] `gardenflow/core/files/settings.py`
- [x] `gardenflow/core/files/local/settings.py`
- [x] `gardenflow/core/files/services.py`
- [x] `gardenflow/core/files/local/services.py`

---

## Future Work

- Additional archive formats (`.tar`, `.tar.gz`)
- `S3FilesService` backend
- Tests in `tests/core/files/`
