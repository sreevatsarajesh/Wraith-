from wraith.core import GHOSTS, classify, fallback, redact, should_ignore

def test_ghosts(): assert {'geocities','fortran','deleted-file','unix-daemon'} <= set(GHOSTS)
def test_failure_fallback(): assert '👻' in fallback('fortran','pytest',1)
def test_destructive_fallback(): assert 'DESTRUCTION' in fallback('deleted-file','rm notes.txt',0)
def test_secret_redaction():
    assert 'supersecret' not in redact('export API_KEY=supersecret')
    assert 'ghp_abcdefghijklmnopqrstuvwxyz123456' not in redact('git push ghp_abcdefghijklmnopqrstuvwxyz123456')
def test_sensitive_commands_ignored():
    assert should_ignore('env') and should_ignore('export TOKEN=abc') and not should_ignore('git status')
def test_classification():
    assert classify('pytest',1)=='failure' and classify('rm -rf build',0)=='destructive' and classify('git status',0)=='git'
