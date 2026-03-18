CI-Integrated Source Instrumentation & Report Consolidation Toolkit

Overview

This repository contains a collection of automation utilities designed to enhance CI/CD workflows, enable dynamic source code instrumentation, and streamline test report consolidation.

It combines two key capabilities:

1. Stage-driven C source instrumentation integrated with Jenkins pipelines
2. Automated HTML test report comparison and merging utility

---

## Source Instrumentation Framework

### Purpose

This module dynamically modifies selected C source files during specific Jenkins pipeline stages, builds the modified binaries, executes validation, and safely restores original source files after execution.

Key Features
1.Stage-based module detection using environment variables
2.Automated backup and restoration of original source files
3.Dynamic modification of .c files:
  >.Test variable insertion
  >.Instrumentation counters injection
  >.Controlled replacement of RTE write calls
  >.Structured data transfer logic
4.CI-triggered build and execution workflow
5.Idempotent and reversible modifications to maintain source integrity
---

## HTML Report Merger & Comparator

### Purpose 
This module processes multiple HTML test reports, validates their structural consistency, and generates a unified merged report.

Key Features
1.Parses multiple HTML reports using structured DOM processing
2.Validates consistency across:
  Test Unit
  Test Group
  Test Fixture
3.Intelligent merging logic:
  Adds missing test groups, fixtures, or test cases
  Avoids duplication of existing entries
  Preserves original report hierarchy
4.Generates a consolidated output report (MergedReport.html)

The implementation uses Python-based parsing and comparison logic to ensure only compatible reports are merged

---

### Design Characteristics

1.Modular and extensible architecture
2.Environment-driven configuration
3.Safe, reversible operations
4.CI/CD friendly CLI utilities
5.Structured and reusable parsing logic for report processing

---

## Additional Utilities

- HTML report merging scripts
- C# backend utilities
- Binary management tools
