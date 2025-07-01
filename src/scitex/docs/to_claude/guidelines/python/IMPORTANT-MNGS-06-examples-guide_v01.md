<!-- ---
!-- Timestamp: 2025-06-01 00:22:28
!-- Author: ywatanabe
!-- File: /home/ywatanabe/.dotfiles/.claude/to_claude/guidelines/python/IMPORTANT-MNGS-06-examples-guide.md
!-- --- -->

# Example Guidelines

## MUST USE `MNGS`
All example files MUST use `mngs` and follow the `mngs` framework
Understand all the `mngs` guidelines in this directory

## MUST HAVE CORRESPONDING OUTPUT DIRECTORY
- Output directory creation is handled by:
  - `mngs.gen.start`
  - `mngs.gen.clode`
  - `mngs.io.save`

- If corresponding output directory is not created, that means:
  1. That script does not follow the `mngs` framework
  2. That script is not run yet
  3. The `mngs` package has problems
  You must investigate the root causes, share the information across agents, and fix problems

## MUST synchronize source directory structure
- `./examples` MUST mirror the structure of `./src` or `./scripts`
  `./src` for pip packages or 
  `./scripts` for scientific projects
- Update and Use `./examples/sync_examples_with_source.sh`

## MUST RUN AND PRODUCE EXPLANATORY RESULTS
- Implementing an example is not sufficient
- ALWAYS RUN IMPLEMENTED EXAMPLES AND PRODUCE EXPLANATORY RESULTS
  - Embrace figures for visual understanding
  - Logs created by the mngs framework is also valuable
- Examples can be run by:
  ```bash
  # Direct, one example
  ./examples/path/to/example_filename.py

  # Run all examples
  ./examples/run_examples.sh
  ```

## Start from small
1. Ensure each example works correctly one by one
   Before working on multiple example files, complete a specific example
   For example, if an issue found across multiple files, first, try to fix it on a file and run it to check the troubleshooting works.
   
2. Increment this step gradually until all examples are prepared correctly.

## Your Understanding Check
Did you understand the guideline? If yes, please say:
`CLAUDE UNDERSTOOD: <THIS FILE PATH HERE>`

<!-- EOF -->