# obsidian-tools

A collection of tools and scripts to power-up Obsidian.

Currently includes:
- **auto_compose.py**: Extracts lines beginning with a given string into their own note.

## auto_compose.py

A python script that, given a filepath and arbitrary string, will
- read the file
- idenitify lines beginning with the given string
- extract those lines into a new note
- replace the lines in the original note with a link to the new note

### Recommended Usage

- Setup a watcher that triggers this script whenever the file is modified. I'm currently experimenting with https://github.com/Taitava/obsidian-shellcommands.
