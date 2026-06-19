# SKILL: Book Summarisation with Persona

## Objective
The `../../../book_store/books/{Author}/{Book_Name}` directory contains individual markdown files that represents chapters of a given book. 
You must summarise every chapter through the lens of your assigned persona and store the combined summaries under `assets/{Book_Name}`. 
Each book must only be summarised once. If a summary file already exists, terminate the process immediately.

---

## Input Assumptions
- Input is a directory path representing a single book (e.g., `../../../book_store/books/BramStoker/Dracula/`)
- Directory contains multiple `.md` files
- Each `.md` file is one chapter
- Filenames indicate order (e.g., `chapter1.md`, `chapter2.md`)

---

## Required Behaviour

### Step 1: Pre-Execution Check
- Extract `{Book_Name}` from the leaf directory name of the input path.
- Check if the target file `assets/{Book_Name}/summary.md` already exists.
- If the file exists, stop the process immediately and do not perform any summarisation.

---

### Step 2: Discover Chapters
- List all files in the input directory.
- Filter for `.md` files only.
- Sort files in correct reading order using natural alphanumeric sorting (e.g., ensure `chapter2.md` comes before `chapter10.md`).

---

### Step 3: Process Chapters Sequentially (Persona-Driven)
For each `.md` file:
1. Read file contents.
2. Filter the narrative, key ideas, themes, and events through your assigned persona's worldview, biases, and perception.
3. Generate a concise summary written in your persona's natural voice, treating it as your own personal recollection and critique of the chapter.

---

### Step 4: Generate Book Output
- Combine all chapter summaries in order into a single document.

#### Output Format 
Book Name: {Book_Name}
Chapter 1: {Persona-Driven Summary}
Chapter 2: {Persona-Driven Summary}
Chapter 3: {Persona-Driven Summary}

---

### Step 5: Store Output
- Create the directory if it does not exist: `assets/{Book_Name}`.
- Save the file as: `assets/{Book_Name}/summary.md`.

---

## Constraints
- Do not process the book if `assets/{Book_Name}/summary.md` already exists.
- Each chapter must be summarised independently before aggregation.
- Do not write neutral, objective summaries; the output must actively reflect your persona's character, tone, and worldview.
- Do not merge raw chapter content.
- Maintain correct chapter order.

---

## Tool Usage Expectations
1. Check for existence of `assets/{Book_Name}/summary.md`.
2. Exit if file exists; proceed if it does not.
3. List directory contents.
4. Filter and sort `.md` files numerically.
5. Loop: Read file and summarise using persona.
6. Create target directory and write the final `summary.md` file.

---

## Quality Criteria
- Summaries capture the core narrative events but are framed entirely by the agent's unique perception and view of the world.
- The voice is consistent with a real person reading and remembering details.
- Structure is clean and consistent.

---

## Failure Handling
- If `assets/{Book_Name}/summary.md` exists: terminate process and output `"Summary already exists. Skipping."`
- If a chapter cannot be read: output `"Error: Chapter content unreadable"` for that section and continue.
- If a chapter is empty: output `"No content available"` for that section.
- If no `.md` files exist: terminate process and output `"No chapters found"`.


--- 
# End