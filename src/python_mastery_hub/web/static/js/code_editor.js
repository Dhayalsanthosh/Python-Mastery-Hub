// Location: src/python_mastery_hub/web/static/js/code_editor.js

/**
 * Advanced Code Editor for Python Mastery Hub
 * Provides comprehensive code editing functionality with syntax highlighting,
 * auto-completion, error checking, and execution capabilities
 */

class CodeEditor {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = document.getElementById(containerId);
    this.options = {
      language: "python",
      theme: "dracula",
      fontSize: 14,
      lineNumbers: true,
      autoComplete: true,
      wordWrap: false,
      tabSize: 4,
      readOnly: false,
      placeholder: "# Write your Python code here...",
      autoSave: false,
      autoSaveInterval: 30000,
      showMinimap: false,
      showInlineErrors: true,
      ...options,
    };

    this.editor = null;
    this.decorations = [];
    this.autoSaveTimer = null;
    this.executionState = "idle"; // idle, running, completed, error
    this.currentCode = "";
    this.isFullscreen = false;

    this.init();
  }

  /**
   * Initialize the code editor
   */
  async init() {
    try {
      if (typeof monaco !== "undefined") {
        await this.initMonacoEditor();
      } else if (typeof CodeMirror !== "undefined") {
        this.initCodeMirrorEditor();
      } else {
        this.initBasicEditor();
      }

      this.setupEventListeners();
      this.setupAutoSave();
      this.loadSavedCode();
    } catch (error) {
      console.error("Failed to initialize code editor:", error);
      this.initBasicEditor();
    }
  }

  /**
   * Initialize Monaco Editor (preferred)
   */
  async initMonacoEditor() {
    // Configure Monaco
    monaco.languages.typescript.javascriptDefaults.setEagerModelSync(true);

    // Python language configuration
    monaco.languages.setLanguageConfiguration("python", {
      comments: {
        lineComment: "#",
        blockComment: ['"""', '"""'],
      },
      brackets: [
        ["{", "}"],
        ["[", "]"],
        ["(", ")"],
      ],
      autoClosingPairs: [
        { open: "{", close: "}" },
        { open: "[", close: "]" },
        { open: "(", close: ")" },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
      ],
      surroundingPairs: [
        { open: "{", close: "}" },
        { open: "[", close: "]" },
        { open: "(", close: ")" },
        { open: '"', close: '"' },
        { open: "'", close: "'" },
      ],
    });

    this.editor = monaco.editor.create(this.container, {
      value: this.options.starter || this.options.placeholder,
      language: this.options.language,
      theme: this.options.theme,
      fontSize: this.options.fontSize,
      lineNumbers: this.options.lineNumbers ? "on" : "off",
      wordWrap: this.options.wordWrap ? "on" : "off",
      tabSize: this.options.tabSize,
      readOnly: this.options.readOnly,
      minimap: { enabled: this.options.showMinimap },
      automaticLayout: true,
      scrollBeyondLastLine: false,
      formatOnPaste: true,
      formatOnType: true,
      suggestOnTriggerCharacters: this.options.autoComplete,
      quickSuggestions: this.options.autoComplete,
    });

    // Add custom Python snippets
    this.addPythonSnippets();

    // Setup keyboard shortcuts
    this.setupMonacoKeyBindings();
  }

  /**
   * Initialize CodeMirror editor (fallback)
   */
  initCodeMirrorEditor() {
    this.editor = CodeMirror(this.container, {
      value: this.options.starter || this.options.placeholder,
      mode: this.options.language,
      theme: this.options.theme,
      lineNumbers: this.options.lineNumbers,
      lineWrapping: this.options.wordWrap,
      tabSize: this.options.tabSize,
      indentUnit: this.options.tabSize,
      readOnly: this.options.readOnly,
      autoCloseBrackets: true,
      matchBrackets: true,
      extraKeys: {
        "Ctrl-Space": "autocomplete",
        "Ctrl-Enter": () => this.executeCode(),
        "Ctrl-S": () => this.saveCode(),
        F11: () => this.toggleFullscreen(),
      },
    });
  }

  /**
   * Initialize basic textarea editor (last resort)
   */
  initBasicEditor() {
    const textarea = document.createElement("textarea");
    textarea.className = "basic-code-editor";
    textarea.value = this.options.starter || this.options.placeholder;
    textarea.readOnly = this.options.readOnly;

    this.container.appendChild(textarea);
    this.editor = {
      getValue: () => textarea.value,
      setValue: (value) => {
        textarea.value = value;
      },
      focus: () => textarea.focus(),
      getSelection: () => ({
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: 1,
        endColumn: 1,
      }),
    };
  }

  /**
   * Add Python-specific code snippets
   */
  addPythonSnippets() {
    if (typeof monaco === "undefined") return;

    const snippets = [
      {
        label: "if",
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: "if ${1:condition}:\n\t${2:pass}",
        insertTextRules:
          monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: "If statement",
      },
      {
        label: "for",
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText: "for ${1:item} in ${2:iterable}:\n\t${3:pass}",
        insertTextRules:
          monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: "For loop",
      },
      {
        label: "def",
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText:
          'def ${1:function_name}(${2:parameters}):\n\t"""${3:docstring}"""\n\t${4:pass}',
        insertTextRules:
          monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: "Function definition",
      },
      {
        label: "class",
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText:
          'class ${1:ClassName}:\n\t"""${2:docstring}"""\n\t\n\tdef __init__(self${3:, parameters}):\n\t\t${4:pass}',
        insertTextRules:
          monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: "Class definition",
      },
      {
        label: "try",
        kind: monaco.languages.CompletionItemKind.Snippet,
        insertText:
          "try:\n\t${1:pass}\nexcept ${2:Exception} as ${3:e}:\n\t${4:pass}",
        insertTextRules:
          monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: "Try-except block",
      },
    ];

    monaco.languages.registerCompletionItemProvider("python", {
      provideCompletionItems: () => ({
        suggestions: snippets,
      }),
    });
  }

  /**
   * Setup Monaco editor key bindings
   */
  setupMonacoKeyBindings() {
    if (typeof monaco === "undefined" || !this.editor) return;

    this.editor.addAction({
      id: "execute-code",
      label: "Execute Code",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter],
      run: () => this.executeCode(),
    });

    this.editor.addAction({
      id: "save-code",
      label: "Save Code",
      keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS],
      run: () => this.saveCode(),
    });

    this.editor.addAction({
      id: "format-code",
      label: "Format Code",
      keybindings: [
        monaco.KeyMod.Alt | monaco.KeyMod.Shift | monaco.KeyCode.KeyF,
      ],
      run: () => this.formatCode(),
    });

    this.editor.addAction({
      id: "toggle-fullscreen",
      label: "Toggle Fullscreen",
      keybindings: [monaco.KeyCode.F11],
      run: () => this.toggleFullscreen(),
    });
  }

  /**
   * Setup general event listeners
   */
  setupEventListeners() {
    if (this.editor && this.editor.onDidChangeModelContent) {
      this.editor.onDidChangeModelContent(() => {
        this.currentCode = this.getValue();
        this.onCodeChange();
      });
    }

    // Handle window resize
    window.addEventListener("resize", () => {
      if (this.editor && this.editor.layout) {
        this.editor.layout();
      }
    });

    // Handle visibility change for auto-save
    document.addEventListener("visibilitychange", () => {
      if (document.hidden && this.options.autoSave) {
        this.saveCode();
      }
    });
  }

  /**
   * Setup auto-save functionality
   */
  setupAutoSave() {
    if (!this.options.autoSave) return;

    this.autoSaveTimer = setInterval(() => {
      this.saveCode();
    }, this.options.autoSaveInterval);
  }

  /**
   * Handle code changes
   */
  onCodeChange() {
    // Clear previous error decorations
    this.clearErrorDecorations();

    // Perform basic syntax checking
    if (this.options.showInlineErrors) {
      this.checkSyntax();
    }

    // Emit custom event
    this.container.dispatchEvent(
      new CustomEvent("codeChanged", {
        detail: { code: this.currentCode },
      })
    );
  }

  /**
   * Execute the current code
   */
  async executeCode() {
    const code = this.getValue();
    if (!code.trim()) {
      this.showMessage("No code to execute", "warning");
      return;
    }

    this.setExecutionState("running");

    try {
      const response = await fetch("/api/code/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          code: code,
          language: this.options.language,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        this.handleExecutionResult(result);
      } else {
        this.handleExecutionError(result.error || "Execution failed");
      }
    } catch (error) {
      this.handleExecutionError("Network error: " + error.message);
    }
  }

  /**
   * Handle successful code execution
   */
  handleExecutionResult(result) {
    this.setExecutionState("completed");

    // Display output
    if (result.output) {
      this.showOutput(result.output, "success");
    }

    // Display errors if any
    if (result.stderr) {
      this.showOutput(result.stderr, "error");
    }

    // Show execution time
    if (result.execution_time) {
      this.showMessage(`Executed in ${result.execution_time}ms`, "info");
    }

    // Emit execution event
    this.container.dispatchEvent(
      new CustomEvent("codeExecuted", {
        detail: { result },
      })
    );
  }

  /**
   * Handle code execution errors
   */
  handleExecutionError(error) {
    this.setExecutionState("error");
    this.showOutput(error, "error");

    // Try to highlight error line if possible
    this.highlightErrorLine(error);
  }

  /**
   * Set execution state and update UI
   */
  setExecutionState(state) {
    this.executionState = state;
    this.container.setAttribute("data-execution-state", state);

    // Update status indicator if exists
    const statusElement = this.container.querySelector(".execution-status");
    if (statusElement) {
      statusElement.textContent =
        state.charAt(0).toUpperCase() + state.slice(1);
      statusElement.className = `execution-status ${state}`;
    }
  }

  /**
   * Check syntax and highlight errors
   */
  checkSyntax() {
    const code = this.getValue();
    if (!code.trim()) return;

    // Basic Python syntax checking
    const lines = code.split("\n");
    const errors = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Check for common syntax errors
      if (
        line.endsWith(":") &&
        lines[i + 1] &&
        !lines[i + 1].trim().startsWith(" ")
      ) {
        errors.push({
          line: i + 1,
          message: "Expected indented block",
          severity: "error",
        });
      }
    }

    this.highlightErrors(errors);
  }

  /**
   * Highlight syntax errors in the editor
   */
  highlightErrors(errors) {
    if (!this.editor || !errors.length) return;

    if (typeof monaco !== "undefined" && this.editor.deltaDecorations) {
      const decorations = errors.map((error) => ({
        range: new monaco.Range(error.line, 1, error.line, 1),
        options: {
          isWholeLine: true,
          className: "error-line",
          glyphMarginClassName: "error-glyph",
          hoverMessage: { value: error.message },
        },
      }));

      this.decorations = this.editor.deltaDecorations(
        this.decorations,
        decorations
      );
    }
  }

  /**
   * Highlight specific error line from execution
   */
  highlightErrorLine(errorMessage) {
    const lineMatch = errorMessage.match(/line (\d+)/i);
    if (lineMatch && this.editor) {
      const lineNumber = parseInt(lineMatch[1]);

      if (typeof monaco !== "undefined" && this.editor.revealLine) {
        this.editor.revealLine(lineNumber);
        this.editor.setPosition({ lineNumber, column: 1 });
      }
    }
  }

  /**
   * Clear error decorations
   */
  clearErrorDecorations() {
    if (
      this.decorations.length &&
      this.editor &&
      this.editor.deltaDecorations
    ) {
      this.decorations = this.editor.deltaDecorations(this.decorations, []);
    }
  }

  /**
   * Format the code
   */
  async formatCode() {
    const code = this.getValue();
    if (!code.trim()) return;

    try {
      const response = await fetch("/api/code/format", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          code: code,
          language: this.options.language,
        }),
      });

      const result = await response.json();

      if (response.ok && result.formatted_code) {
        this.setValue(result.formatted_code);
        this.showMessage("Code formatted successfully", "success");
      } else {
        // Fallback to basic formatting
        this.basicFormat();
      }
    } catch (error) {
      this.basicFormat();
    }
  }

  /**
   * Basic code formatting fallback
   */
  basicFormat() {
    const code = this.getValue();
    const lines = code.split("\n");
    let indentLevel = 0;
    const formatted = [];

    for (const line of lines) {
      const trimmed = line.trim();

      if (trimmed.endsWith(":")) {
        formatted.push("    ".repeat(indentLevel) + trimmed);
        indentLevel++;
      } else if (trimmed === "") {
        formatted.push("");
      } else {
        if (
          trimmed.startsWith("return") ||
          trimmed.startsWith("break") ||
          trimmed.startsWith("continue")
        ) {
          formatted.push("    ".repeat(Math.max(0, indentLevel - 1)) + trimmed);
        } else {
          formatted.push("    ".repeat(indentLevel) + trimmed);
        }
      }
    }

    this.setValue(formatted.join("\n"));
    this.showMessage("Code formatted with basic rules", "info");
  }

  /**
   * Save the current code
   */
  saveCode() {
    if (!this.options.autoSave) return;

    const code = this.getValue();
    const data = {
      code: code,
      timestamp: Date.now(),
      editorId: this.containerId,
    };

    localStorage.setItem(
      `code_editor_${this.containerId}`,
      JSON.stringify(data)
    );

    // Show save status
    this.showMessage("Code saved", "success", 2000);
  }

  /**
   * Load previously saved code
   */
  loadSavedCode() {
    if (!this.options.autoSave) return;

    const saved = localStorage.getItem(`code_editor_${this.containerId}`);
    if (saved) {
      try {
        const data = JSON.parse(saved);
        if (data.code && data.code !== this.options.placeholder) {
          this.setValue(data.code);
        }
      } catch (error) {
        console.error("Failed to load saved code:", error);
      }
    }
  }

  /**
   * Toggle fullscreen mode
   */
  toggleFullscreen() {
    if (this.isFullscreen) {
      this.exitFullscreen();
    } else {
      this.enterFullscreen();
    }
  }

  /**
   * Enter fullscreen mode
   */
  enterFullscreen() {
    this.container.classList.add("fullscreen");
    this.isFullscreen = true;

    if (this.editor && this.editor.layout) {
      setTimeout(() => this.editor.layout(), 100);
    }

    document.addEventListener("keydown", this.fullscreenKeyHandler);
  }

  /**
   * Exit fullscreen mode
   */
  exitFullscreen() {
    this.container.classList.remove("fullscreen");
    this.isFullscreen = false;

    if (this.editor && this.editor.layout) {
      setTimeout(() => this.editor.layout(), 100);
    }

    document.removeEventListener("keydown", this.fullscreenKeyHandler);
  }

  /**
   * Handle keyboard events in fullscreen
   */
  fullscreenKeyHandler = (event) => {
    if (event.key === "Escape") {
      this.exitFullscreen();
    }
  };

  /**
   * Show output in console or output area
   */
  showOutput(output, type = "info") {
    const outputContainer =
      this.container.querySelector(".output-container") ||
      document.querySelector(".console-output") ||
      this.createOutputContainer();

    const outputElement = document.createElement("div");
    outputElement.className = `output-line output-${type}`;
    outputElement.textContent = output;

    outputContainer.appendChild(outputElement);
    outputContainer.scrollTop = outputContainer.scrollHeight;
  }

  /**
   * Create output container if it doesn't exist
   */
  createOutputContainer() {
    const container = document.createElement("div");
    container.className = "output-container";
    this.container.appendChild(container);
    return container;
  }

  /**
   * Show temporary messages
   */
  showMessage(message, type = "info", duration = 3000) {
    const messageElement = document.createElement("div");
    messageElement.className = `editor-message message-${type}`;
    messageElement.textContent = message;

    this.container.appendChild(messageElement);

    setTimeout(() => {
      if (messageElement.parentNode) {
        messageElement.remove();
      }
    }, duration);
  }

  /**
   * Get current editor value
   */
  getValue() {
    if (!this.editor) return "";

    if (this.editor.getValue) {
      return this.editor.getValue();
    } else if (this.editor.value !== undefined) {
      return this.editor.value;
    }

    return "";
  }

  /**
   * Set editor value
   */
  setValue(value) {
    if (!this.editor) return;

    if (this.editor.setValue) {
      this.editor.setValue(value);
    } else if (this.editor.value !== undefined) {
      this.editor.value = value;
    }

    this.currentCode = value;
  }

  /**
   * Focus the editor
   */
  focus() {
    if (this.editor && this.editor.focus) {
      this.editor.focus();
    }
  }

  /**
   * Get current selection
   */
  getSelection() {
    if (this.editor && this.editor.getSelection) {
      return this.editor.getSelection();
    }
    return null;
  }

  /**
   * Insert text at cursor position
   */
  insertText(text) {
    if (!this.editor) return;

    if (typeof monaco !== "undefined" && this.editor.trigger) {
      this.editor.trigger("keyboard", "type", { text });
    }
  }

  /**
   * Change editor theme
   */
  setTheme(theme) {
    this.options.theme = theme;

    if (typeof monaco !== "undefined" && this.editor) {
      monaco.editor.setTheme(theme);
    } else if (this.editor && this.editor.setOption) {
      this.editor.setOption("theme", theme);
    }
  }

  /**
   * Change font size
   */
  setFontSize(size) {
    this.options.fontSize = size;

    if (typeof monaco !== "undefined" && this.editor) {
      this.editor.updateOptions({ fontSize: size });
    }
  }

  /**
   * Dispose of the editor and clean up
   */
  dispose() {
    if (this.autoSaveTimer) {
      clearInterval(this.autoSaveTimer);
    }

    if (this.editor && this.editor.dispose) {
      this.editor.dispose();
    }

    document.removeEventListener("keydown", this.fullscreenKeyHandler);
  }
}

// Export for use in other modules
window.CodeEditor = CodeEditor;

// Auto-initialize editors on page load
document.addEventListener("DOMContentLoaded", () => {
  const editors = document.querySelectorAll("[data-code-editor]");
  editors.forEach((container) => {
    const options = JSON.parse(container.dataset.options || "{}");
    new CodeEditor(container.id, options);
  });
});
