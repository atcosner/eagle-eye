# Feature improvements
- [X] Ability to remove added files
- [X] Accept PDF files
- [X] Add logging all messages (debug+) to a file in the working dir
- [ ] Resize window when the tab of the processing pipeline changes
- [ ] Fix tab ordering in result check to allow pressing tab to iterate through the whole flow

# Bugs
- [ ] When updating a text field, validation stripping can prevent the user from typing
  - Add a space at the end of locality
- [ ] When a file fails to pre-process, the user is prevented from continuing the pipeline
- [ ] Re-running the pre-processing step on an input file causes a violation on a primary key constraint
  - I think this is because the old pre-processing result does not get deleted
