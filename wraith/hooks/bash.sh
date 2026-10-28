# Wraith bash hook. Disable with: export WRAITH_ENABLED=0
# zsh is the recommended integration; Bash DEBUG traps can observe compound commands.
_wraith_prompt_command() {
  local _wraith_status=$?
  [[ "${WRAITH_ENABLED:-1}" == "0" ]] && return
  [[ -n "${_WRAITH_LAST_CMD:-}" ]] || return
  local _wraith_cmd="$_WRAITH_LAST_CMD"; _WRAITH_LAST_CMD=""
  [[ "$_wraith_cmd" == wraith\ * ]] && return
  command wraith haunt "$_wraith_cmd" --status "$_wraith_status" --ghost "${WRAITH_GHOST:-geocities}" 2>/dev/null
}
_wraith_debug_trap() { [[ "$BASH_COMMAND" == _wraith_* || "$BASH_COMMAND" == wraith\ * ]] && return; _WRAITH_LAST_CMD="$BASH_COMMAND"; }
trap '_wraith_debug_trap' DEBUG
PROMPT_COMMAND="_wraith_prompt_command${PROMPT_COMMAND:+;$PROMPT_COMMAND}"
