## 2024-05-22 - Symlink Attack Prevention
**Vulnerability:** File operations on untrusted paths can be redirected via symlinks to arbitrary files, leading to data loss or information disclosure.
**Learning:** `open()` blindly follows symlinks. Even checking `os.path.exists()` before opening is vulnerable to TOCTOU (Time-of-Check Time-of-Use) races.
**Prevention:** Use `os.open` with `O_CREAT | O_EXCL` for creation to ensure atomicity. Check `os.path.islink()` before sensitive read/delete operations on untrusted files, or use file descriptors where possible.
