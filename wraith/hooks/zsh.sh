# Wraith zsh hook. Disable with: export WRAITH_ENABLED=0
_wraith_precmd() {
  local _wraith_status=$?
  [[ "${WRAITH_ENABLED:-1}" == "0" ]] && return
  [[ -n "${_WRAITH_LAST_CMD:-}" ]] || return
  [[ "${_WRAITH_LAST_CMD}" == wraith* ]] && return
  command wraith haunt "$_WRAITH_LAST_CMD" --status "$_wraith_status" --ghost "${WRAITH_GHOST:-geocities}" 2>/dev/null
}
_wraith_preexec() { _WRAITH_LAST_CMD="$1"; }
autoload -Uz add-zsh-hook
add-zsh-hook preexec _wraith_preexec
add-zsh-hook precmd _wraith_precmd
