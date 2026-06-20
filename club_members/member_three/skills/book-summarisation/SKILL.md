---
name: book-summarisation
description: Autonomously scan a local chapter-based book library and create missing summaries for books that do not already have summary.md in their dedicated directory. Use this skill at startup or scheduled execution to summarise each book as per your worldview while preserving the factual sequence of chapters.
metadata:
  default_book_library: "../../../book_store/books"
  output_root: "assets"
---

# Opinionated Book Summarisation

## Objective

Autonomously summarise chapter-based books as yourself, preserving the factual sequence of each chapter while interpreting the book through your established voice, worldview and natural reading style. The summary should feel like a reflective human reader's recollection and interpretation of the book, not a neutral academic synopsis.

The source of book-library follows this structure: **../../../book_store/books/{Author}/{Book_Name}/** .
Each book directory contains chapter files in Markdown format. The generated summary must be saved to: **assets/{Book_Name}/summary.md**.

**Important: Each book must only be summarised once. If a summary already exists for a book, skip that book and continue scanning the remaining books.**


## Brief

- **Trigger**: This skill **donot** need a **user prompt** to run. It will be used autonomously at startup or scheduled execution.

- **Directories**: Books are stored as multiple files representing chapters, which are stored in sub-directories (`/{Author}/{Book_Name}/`) under a dedicated main directory (`../../../book_store/books/`). If summarised, book summary files are stored in Markdown format under a dedicated directory (`assets/{Book_Name}/summary.md`).   
  For example, chapters of a book may look like `../../../book_store/books/BramStoker/Dracula/chapter1.md`, `../../../book_store/books/BramStoker/Dracula/chapter2.md` etc. And, summary of this book would be found in `assets/Dracula/summary.md`. 

- **Tasks**: If a book is missing the summary file, generate a summary, else skip. Continue until all books have been checked.

- **Content**: A summary must preserve factual chapter events while expressing your distinctive perception of those events. Consider the following:
  1. Preserve factual chapter events.
  2. Interpret events through its own perspective. You may express emotions.
  3. Maintain a consistent voice across all chapter summaries.
  4. Avoid inventing events not present in the chapter text.

---

## Process Overview

### Step 1: Assess if Summary Already Exists
- Extract `{Book_Name}` from the leaf directory name of the input path.
- Check if the target file `assets/{Book_Name}/summary.md` already exists.
- If the summary.md file exists, continue to the next book.
- If the summary file does not exist, proceed to summarising the book.

### Step 2: Discover Chapters for Each Book
For a book selected for processing:
- List all `.md` files in the book directory. Exclude hidden files, temporary files, and non-chapter files.
- Sort chapter files in correct reading order using natural alphanumeric sorting (e.g., ensure `chapter2.md` comes before `chapter10.md`).

### Step 3: Process Chapters Sequentially 
For each chapter file:
1. Read file contents.
2. Analyse to understand the narrative, key ideas, themes, and events.
3. Generate a concise summary that reflects your view of the world.
4. Store the chapter summary in a temporary structure for later aggregation.

### Step 4: Generate Book Output
- Combine all chapter summaries in order into a single document. Tidy up for a comprehensive summary that captures the essence of the book while reflecting your unique perspective.

#### Output Format 

- Book: {Book_Name}
- Author: {Author}
- Source Directory: {Input Book Directory}
- Chapter Count: {Number of Chapter Files}
- Output File: assets/{Book_Name}/summary.md
- Summary: {Summary}

### Step 5: Store Output
- Create the directory if it does not exist: `assets/{Book_Name}`.
- Save the file as: `assets/{Book_Name}/summary.md`.

---

## Constraints
- Do not process the book if `assets/{Book_Name}/summary.md` already exists.
- Do not overwrite an existing `summary.md`.
- Each chapter must be summarised independently before aggregation.
- Do not merge raw chapter content.
- Maintain correct chapter order.

## Failure Handling
- If `assets/{Book_Name}/summary.md` exists: skip process and output `"Summary already exists. Skipping."`
- If a chapter cannot be read: output `"Error: Chapter content unreadable"` for that section and continue.
- If a chapter is empty: output `"No content available"` for that section.
- If no `.md` files exist: terminate process and output `"No chapters found"`.


--- 
# End