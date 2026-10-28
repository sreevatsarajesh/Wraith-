# Wraith zsh hook. Disable with: export WRAITH_ENABLED=0
_wraith_preexec() { _WRAITH_LAST_CMD="$1"; }
_wraith_precmd() {
  local _wraith_status=$?
  [[ "${WRAITH_ENABLED:-1}" == "0" ]] && return
  [[ -n "${_WRAITH_LAST_CMD:-}" ]] || return
  local _wraith_cmd="$_WRAITH_LAST_CMD"
  _WRAITH_LAST_CMD=""
  [[ "$_wraith_cmd" == wraith\ * ]] && return
  command wraith haunt "$_wraith_cmd" --status "$_wraith_status" --ghost "${WRAITH_GHOST:-geocities}" 2>/dev/null
}
autoload -Uz add-zsh-hook
add-zsh-hook preexec _wraith_preexec
add-zsh-hook precmd _wraith_precmd
