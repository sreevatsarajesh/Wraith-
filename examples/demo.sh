#!/usr/bin/env bash
set -e
wraith haunt "git push origin main" --status 0 --ghost geocities
wraith haunt "make test" --status 1 --ghost fortran
wraith haunt "rm old_notes.txt" --status 0 --ghost deleted-file
wraith status
wraith memory --limit 5
