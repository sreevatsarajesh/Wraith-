import { useEffect, useRef, useState } from "react";
import { Ghost, Terminal, ShieldCheck, Wifi, WifiOff, Trash2, Code2, ChevronRight, Circle, Sparkles } from "lucide-react";
const API = "http://127.0.0.1:8765";
const personalities = ["geocities", "fortran", "deleted-file", "unix-daemon"];
const intro = [
  { type: "system", text: "WRAITH TERMINAL // build 0.2.0" },
  { type: "system", text: "A ghost is listening. Type `help` to see available commands." },
  { type: "ghost", text: "👻 The guestbook is open, mortal. Try not to break the webring." }
];

export default function App() {
  const [ghost, setGhost] = useState("geocities");
  const [input, setInput] = useState("");
  const [lines, setLines] = useState(intro.map((x,i)=>({...x,id:i})));
  const [busy, setBusy] = useState(false);
  const [connected, setConnected] = useState(false);
  const [model, setModel] = useState("qwen2.5:3b");
  const [memory, setMemory] = useState([]);
  const [showMemory, setShowMemory] = useState(false);
  const [clock, setClock] = useState(new Date());
  const endRef = useRef(null);
  const inputRef = useRef(null);
  const seq = useRef(10);

  useEffect(() => {
    const t = setInterval(()=>setClock(new Date()),1000);
    const check = async () => {
      try {
        const r = await fetch(`${API}/api/status`);
        const d = await r.json();
        setConnected(Boolean(d.api));
        setModel(d.model || "qwen2.5:3b");
      } catch { setConnected(false); }
    };
    check();
    const p = setInterval(check, 8000);
    return ()=>{clearInterval(t);clearInterval(p)};
  }, []);
  useEffect(()=>{endRef.current?.scrollIntoView({behavior:"smooth",block:"end"})},[lines,busy,showMemory]);

  const add = (type,text,extra={}) => setLines(prev=>[...prev,{id:seq.current++,type,text,...extra}]);
  const run = async (raw) => {
    const command = raw.trim();
    if (!command || busy) return;
    setInput("");
    add("command",command);
    const c = command.toLowerCase();
    if (c === "clear") { setLines([]); return; }
    if (c === "help") {
      add("system","Available UI commands: help, clear, ghosts, status, memory");
      add("system","Any other input is sent as command text to Wraith for a reaction. It is NOT executed.");
      return;
    }
    if (c === "ghosts") { add("system",`Available spirits: ${personalities.join(" · ")}`); return; }
    if (c === "status") {
      add("system",`API: ${connected ? "connected" : "offline"} · Model: ${model} · Selected ghost: ${ghost}`);
      return;
    }
    if (c === "memory") {
      try {
        const r = await fetch(`${API}/api/memory?limit=8`);
        const d = await r.json();
        setMemory(d.events || []);
        setShowMemory(true);
        add("system",`Loaded ${d.events?.length || 0} recent memories from local SQLite.`);
      } catch { add("error","Could not load memory. Is the local Wraith API running?"); }
      return;
    }
    setShowMemory(false);
    setBusy(true);
    try {
      const r = await fetch(`${API}/api/haunt`, {
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({command,ghost})
      });
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || "API error");
      add("ghost",d.response || "👻 The spirit is silent.");
    } catch (e) {
      add("error",`The veil is closed: ${e.message}. Start the local Wraith API and try again.`);
    } finally { setBusy(false); }
  };

  const submit = e => {e.preventDefault();run(input)};
  return <main className="shell">
    <div className="ambient ambient-a"/><div className="ambient ambient-b"/>
    <header className="topbar">
      <div className="brand"><div className="brandmark"><Ghost size={22}/></div><div><div className="brandname">WRAITH<span>_</span></div><div className="brandmeta">LOCAL TERMINAL SPIRIT</div></div></div>
      <div className="topright"><span className={`connection ${connected?"online":""}`}><Circle size={7} fill="currentColor"/>{connected?"LOCAL API CONNECTED":"API DISCONNECTED"}</span><span className="clock">{clock.toLocaleTimeString([], {hour12:false})}</span></div>
    </header>
    <section className="hero">
      <div className="eyebrow"><Sparkles size={13}/> GHOST IN THE MACHINE</div>
      <h1>Your terminal.<br/><span>Your haunting.</span></h1>
      <p>A local AI companion from the forgotten corners of computing.</p>
    </section>
    <section className="terminal-window">
      <div className="windowbar">
        <div className="traffic"><i/><i/><i/></div>
        <div className="windowtitle"><Terminal size={13}/> wraith — zsh — local session</div>
        <div className="windowbadge"><span/> {connected?"ENCRYPTED LOCAL LOOP":"WAITING FOR API"}</div>
      </div>
      <div className="terminal-body" onClick={()=>inputRef.current?.focus()}>
        <div className="welcome"><pre>{` __      __  ____    ___   ___ _____ _   _\n \\ \\    / / |  _ \\  / _ \\ / __|_   _| | | |\n  \\ \\/\\/ /  | |_) || | | |\\__ \\ | | | |_| |\n   \\_/\\_/   |  _ < | |_| |___) || | |  _  |\n             |_| \\_\\\\___/|____/ |_| |_| |_|`}</pre><div className="welcome-note">A ghost in your terminal. <span>v0.2.0</span></div></div>
        <div className="output">
          {lines.map(line=><div className={`line line-${line.type}`} key={line.id}>
            {line.type==="command" ? <><span className="prompt">vatsa@wraith <b>~</b> $</span><span className="line-text">{line.text}</span></> :
             line.type==="ghost" ? <><span className="ghost-icon"><Ghost size={14}/></span><span className="line-text">{line.text}</span></> :
             <><span className="line-marker">{line.type==="error"?"!":"›"}</span><span className="line-text">{line.text}</span></>}
          </div>)}
          {busy && <div className="line line-ghost"><span className="ghost-icon"><Ghost size={14}/></span><span className="thinking">The spirit is crossing the veil<span>...</span></span></div>}
          <div ref={endRef}/>
        </div>
        <form className="inputrow" onSubmit={submit}>
          <span className="prompt">vatsa@wraith <b>~</b> $</span>
          <input ref={inputRef} value={input} onChange={e=>setInput(e.target.value)} placeholder={busy?"The ghost is thinking…":"Type a command for the ghost…"} disabled={busy} autoComplete="off" spellCheck="false" aria-label="Command input"/>
          <button className="enter" type="submit" disabled={busy||!input.trim()}>ENTER <ChevronRight size={14}/></button>
        </form>
        <div className="terminal-foot"><span><span className="key">↵</span> ENTER TO HAUNT</span><span>COMMANDS ARE OBSERVED, NEVER EXECUTED</span><span>{lines.length.toString().padStart(2,"0")} EVENTS</span></div>
      </div>
    </section>
    <section className="controls">
      <div className="control-label">CHOOSE YOUR SPIRIT</div>
      <div className="ghost-grid">
        {personalities.map((name,i)=><button key={name} className={`ghost-card ${ghost===name?"selected":""}`} onClick={()=>setGhost(name)}>
          <div className="ghost-card-top"><Ghost size={17}/><span className="ghost-number">0{i+1}</span></div>
          <strong>{name}</strong><small>{["The lost web of 1999","Punch cards never die","An echo of what vanished","Keeper of the system logs"][i]}</small>
          <span className="select-dot">{ghost===name?"ACTIVE":"SELECT"}</span>
        </button>)}
      </div>
    </section>
    {showMemory && <section className="memory-panel"><div className="panel-heading"><div><div className="control-label">LOCAL MEMORY</div><h2>Recent echoes</h2></div><button className="icon-button" onClick={()=>setShowMemory(false)}><Trash2 size={15}/> CLOSE</button></div>
      {memory.length ? memory.map((m,i)=><div className="memory-row" key={i}><code>{m.command}</code><span>{m.ghost}</span><p>{m.response}</p></div>):<p className="empty">No memories yet. The ghost has a clean slate.</p>}
    </section>}
    <footer className="footer"><div><ShieldCheck size={15}/> <span>LOCAL-FIRST BY DESIGN</span></div><span>NO CLOUD API · NO COMMAND EXECUTION</span><span>BUILT FOR THE OPEN WEB <Ghost size={13}/></span></footer>
  </main>;
}
