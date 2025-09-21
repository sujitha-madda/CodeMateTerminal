const terminal = document.getElementById('terminal');
let history = [];
let historyIndex = -1;
let currentFiles = []; // for autocomplete

function appendOutput(text){
  let lines = text.split("\n").map(line => {
    if(line.toLowerCase().includes("error") || line.toLowerCase().includes("unknown")){
      return `<span class="error">${line}</span>`;
    } else if(line.endsWith("/")) {
      return `<span class="directory">${line}</span>`;
    } else {
      return `<span class="file">${line}</span>`;
    }
  });
  terminal.innerHTML += lines.join("<br>") + "<br>";
  terminal.scrollTop = terminal.scrollHeight;
}

function showPrompt() {
  terminal.innerHTML += '<span class="prompt">> </span><span class="input-line" contenteditable="true"></span>';
  const inputLine = terminal.querySelector('.input-line:last-child');
  inputLine.focus();

  inputLine.addEventListener('keydown', async (e)=>{
    if(e.key === 'Enter'){
      e.preventDefault();
      const cmd = inputLine.textContent.trim();
      inputLine.contentEditable = "false";
      appendOutput('');
      if(cmd){
        history.push(cmd);
        historyIndex = history.length;
        await runCommand(cmd);
      }
      showPrompt();
    } else if(e.key === 'ArrowUp'){
      e.preventDefault();
      if(historyIndex > 0) historyIndex--;
      inputLine.textContent = history[historyIndex] || '';
      placeCaretAtEnd(inputLine);
    } else if(e.key === 'ArrowDown'){
      e.preventDefault();
      if(historyIndex < history.length-1) historyIndex++;
      inputLine.textContent = history[historyIndex] || '';
      placeCaretAtEnd(inputLine);
    } else if(e.key === 'Tab'){ // autocomplete
      e.preventDefault();
      const text = inputLine.textContent.trim();
      const parts = text.split(" ");
      const lastPart = parts[parts.length - 1];
      const suggestions = currentFiles.filter(f => f.startsWith(lastPart));
      if(suggestions.length === 1){
        parts[parts.length - 1] = suggestions[0];
        inputLine.textContent = parts.join(" ");
        placeCaretAtEnd(inputLine);
      } else if(suggestions.length > 1){
        appendOutput(suggestions.join("    "));
        showPrompt(); // show new prompt to display options
      }
    }
  });
}

function placeCaretAtEnd(el) {
  el.focus();
  document.getSelection().selectAllChildren(el);
  document.getSelection().collapseToEnd();
}

async function runCommand(cmd){
  try {
    const res = await fetch('/api/command', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({command: cmd})
    });
    const j = await res.json();
    appendOutput(j.output || '');

    // Update currentFiles for autocomplete
    if(cmd.startsWith("ls") || cmd.startsWith("pwd")){
      currentFiles = (j.output || "").split("\n").map(s => s.trim()).filter(s => s);
    }

  } catch(err){
    appendOutput('Error: ' + err);
  }
}

// Initialize
appendOutput('Welcome to CodeMate Terminal (workspace). Type commands and press Enter.');
showPrompt();
