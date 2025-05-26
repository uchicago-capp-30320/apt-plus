# Principles
We focus on three core values, in alphabetical order.

- **Transparency:** this project responds to data inaccuracies and bias on sites like Zillow. Our product will be guided by an approach to honestly share and present data so that users can make decisions.
- **Equity**: we design apt-plus such that anyone can use it because our product will be openly available. Therefore, we will include accessibility considerations in what data to display and how it can be understood.
- **Respect**: we are all in the same position, contributors to apartments plus. Our opinions should carry equal weight as long as they are well supported and respct th goals and we should all have space to deliver them.

All major decisions include discussion, but if there's disagreement, the frontend or backend leads make that decision.

Individual design decisions on technology will be recorded in the documentation and should be justified by (1) user research, then (2) values, and finally (3) personal opinions of the implementor. Implementation decisions will be owned by the implementor of the feature, including discussion with the lead as necessary.

Decisions that justify feature inclusion would be made as a group on GitHub issues. Decisions on feature implementation are up to the programmer. Decisions on integration are made by the Chief Architect.

# Practices
## Making contributions
Anyone can make a contribution, as long as it is appropriately reviewed and tested. This section talks about how.

### Tasks
We use GitHub Issues workflow to manage tasks and track progress. 

Each task can be collected tracked on a shared Kanban board, on GitHUb issues, moving through stages of “Backlog,” “To Do,” “In Progress,” On Hold,” and “Done.”

Feel free to add an issue and get it assigned out to you after a core team member reviews it.

### Code Review
We ask that you make requests to the original team ont his project for code review. They are contributors on the right bar of the GitHub home page.

### Branches
There will be no long-lived branches for the project, only main. 

All the branches will be short-lived branches related to additions/modifications of specific features. One single user can have multiple active short-lived branches at different times if these branches reflect sets of unrelated changes (those branches are related to different issues and are not dependent one of the other).

### Pull requests

Everyone merges their own code, after meeting the following criteria: the code has been linted, is already functional, pass all already existing tests, have new tests if it introduces new features/fixes bugs not previously tested, and has been reviewed for another person. We will review this policy after the first couple of week to determine when review will happen.

For the creation of the pull request, include a summary of what the new/modified code does. Delete the branch after pulling if the task for that branch has been completed by that pull.

### Commits

Each commit will be, ideally, a single unit of work, in the sense that each commit will have an specific isolated advancement and it will be named properly (no "idk :/", "trying", or "asd" as name). In general, this will mean also to don't do too many different things in the same commit (e.g. ideally one commit will be "adds submit button", not "adds submit button, fixes data model, and updates server").

We follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) guidelines for commit content.

### AI
We use AI tools **as references**, but we write our own code. Specifically, we can ask AI tools to:

- Provide existing solutions related to features we're trying to implement when we get stuck
- Explain how a particular function works
- Help explain error messages
- Proofread documentation
- Refactoring with human review
- Generates test cases

We ask that you do not use AI to write code if you contribute to this project.