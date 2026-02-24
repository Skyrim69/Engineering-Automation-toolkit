# CI-Integrated Source Instrumentation Toolkit

## Overview

This repository contains a collection of automation utilities developed to support CI/CD workflows, source code instrumentation, and build validation processes.

The primary module provides stage-driven dynamic modification of C source files during Jenkins pipeline execution, enabling automated test instrumentation and controlled runtime validation.

---

## Source Instrumentation Framework

### Purpose

This module dynamically modifies selected C source files during specific Jenkins pipeline stages, builds the modified binaries, executes validation, and safely restores original source files after execution.

---

### Key Capabilities

- Stage-based module detection using environment variables
- Automated backup of original source files
- Targeted modification of `.c` source files:
  - Insertion of test variables
  - Injection of instrumentation counters
  - Controlled replacement of RTE write calls
  - Structured data transfer logic insertion
- Automated binary copy management
- Safe restoration of original source files after stage completion

---

### Workflow

1. Detect active pipeline stage (via `STAGE_NAME`)
2. Identify associated modules using stage-to-module mapping
3. Backup original source files
4. Apply structured source modifications
5. Trigger build via CI pipeline
6. Execute modules
7. Restore original source files

---

### Design Characteristics

- Centralized module configuration using dictionary-driven architecture
- Idempotent modification logic (avoids duplicate insertions)
- Reversible operations to ensure source integrity
- Environment-driven configuration
- CI/CD friendly CLI interface

---

## Additional Utilities

- HTML report merging scripts
- C# backend utilities
- Binary management tools
