# 60-second demo script

1. Show `wraith status` with Ollama running.
2. Run `wraith haunt "git push origin main" --ghost geocities`.
3. Run `wraith haunt "pytest" --status 1 --ghost fortran`.
4. Run `wraith haunt "rm old_notes.txt" --ghost deleted-file`.
5. Show `wraith memory` and then `wraith forget`.
6. Turn off Wi-Fi and repeat a command to demonstrate local inference (only after the model has been downloaded). If Ollama is stopped, deterministic fallback lines still work.

Be transparent: the fallback works without Ollama; generative responses require the local Ollama service and a downloaded model.
