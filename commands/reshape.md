---
allowed-tools: Grep
description: Find @@@ markings in code and act accordingly
---
I've placed @@@ markings in code and they are grepped below.
Read them all and act as described below.

$ARGUMENTS

## Markings

! rg -C5  -- '@@@'

## Task

1. Read the relevant files
2. Implement the requested changes
3. Remove or update the markings with your response/comment
4. Commit the changes with [reshape] tag in description
5. Reflect (below)

## Reflect

When done with the changes:

- Reflect on what you did
- Summarize the refactoring work
- extract conventions to CONVENTIONS.md (if any)
- extract taste preferences to TASTE.md (if any)

If the markings are documenting convention, make sure they are followed in the rest of the code and either change them along or, if too big, plan a follow-up task to clean it up (in @plans) 


## Examples
- `@@@ find better name for variable` - refactor request
- `@@@- fix: @var is sometimes nil, investigate why` - just fix the bug
- `@@@: this is how memoize should be done` - note & remember the good practice
- `@@@: DO NOT USE general rescue unless reasoned` - note & remember to avoid that practice


