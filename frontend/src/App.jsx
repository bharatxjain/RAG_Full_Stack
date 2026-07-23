import { useState, useEffect, useRef } from "react";

const API_URL = "http://localhost:8000";

function uploadWithProgress(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}/upload`);
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable)
        onProgress(Math.round((e.loaded / e.total) * 100));
    };
    xhr.onload = () => {
      try {
        resolve({
          ok: xhr.status >= 200 && xhr.status < 300,
          data: JSON.parse(xhr.responseText),
        });
      } catch (err) {
        reject(err);
      }
    };
    xhr.onerror = () => reject(new Error("Network error"));
    const formData = new FormData();
    formData.append("file", file);
    xhr.send(formData);
  });
}

function App() {
  const [files, setFiles] = useState([]);
  const [question, setQuestion] = useState("");
  const [askedQuestion, setAskedQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [asking, setAsking] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [deletingFile, setDeletingFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    refreshFiles();
  }, []);

  async function refreshFiles() {
    try {
      const res = await fetch(`${API_URL}/files`);
      const data = await res.json();
      setFiles(data.files || []);
    } catch {
      // backend not up yet
    }
  }

  async function runUpload(file) {
    if (!file) return;
    setUploading(true);
    setProgress(0);
    setUploadStatus(null);

    try {
      const { ok, data } = await uploadWithProgress(file, setProgress);
      console.log("upload response:", ok, data);
      if (ok && data.status === "indexed") {
        setUploadStatus({
          type: "success",
          text: `Added to the Library: ${data.filename}`,
        });
      } else if (data.status === "warning") {
        setUploadStatus({ type: "warning", text: data.message });
      } else {
        setUploadStatus({
          type: "error",
          text: data.detail || "Could not read this file",
        });
      }
      setFiles(data.files || []);
    } catch {
      setUploadStatus({ type: "error", text: "Could not reach the server" });
    } finally {
      setUploading(false);
    }
  }

  function handleFileInputChange(e) {
    runUpload(e.target.files[0]);
    e.target.value = "";
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragActive(false);
    if (uploading) return;
    const file = e.dataTransfer.files[0];
    runUpload(file);
  }

  function handleDragOver(e) {
    e.preventDefault();
    if (!uploading) setDragActive(true);
  }

  function handleDragLeave(e) {
    e.preventDefault();
    setDragActive(false);
  }

  async function handleDelete(filename) {
    setDeletingFile(filename);
    try {
      const res = await fetch(
        `${API_URL}/files/${encodeURIComponent(filename)}`,
        { method: "DELETE" },
      );
      const data = await res.json();
      if (res.ok) {
        setFiles(data.files || []);
        setUploadStatus({ type: "success", text: `Removed: ${filename}` });
      } else {
        setUploadStatus({
          type: "error",
          text: data.detail || "Could not remove file",
        });
      }
    } catch {
      setUploadStatus({ type: "error", text: "Could not reach the server" });
    } finally {
      setDeletingFile(null);
    }
  }

  async function ask() {
    const q = question.trim();
    if (!q || asking) return;

    setAsking(true);
    setAskedQuestion(q);
    setAnswer("");
    setSources([]);
    setQuestion("");

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const data = await res.json();
      setAnswer(res.ok ? data.answer : data.detail);
      setSources(data.sources || []);
    } catch {
      setAnswer("Could not reach the server.");
    } finally {
      setAsking(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") ask();
  }

  return (
    <div className="page">
      <div className="catalog">
        <header className="catalog-header">
          <span className="eyebrow">Reference Desk</span>
          <h1>Document Q&A</h1>
          <p className="intro-text">
            Upload a document and I'll search it directly to answer your
            questions, with clear explanations and the source passages cited
            underneath.
          </p>
        </header>

        <section
          className={`upload-slot ${dragActive ? "drag-active" : ""}`}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <label className={`upload-label ${uploading ? "is-busy" : ""}`}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md"
              onChange={handleFileInputChange}
              disabled={uploading}
              hidden
            />
            {uploading ? (
              <span className="upload-busy-text">
                <span className="stamp-mini" aria-hidden="true" />
                Filing document... {progress}%
              </span>
            ) : (
              <span>
                <strong>Click to add a document</strong>, or drag one in here
              </span>
            )}
          </label>

          {uploading && (
            <div
              className="progress-track"
              role="progressbar"
              aria-valuenow={progress}
              aria-valuemin={0}
              aria-valuemax={100}
            >
              <div
                className="progress-fill"
                style={{ width: `${progress}%` }}
              />
            </div>
          )}

          <p className="allowed-formats">Allowed formats: PDF, DOCX, TXT, MD</p>

          {uploadStatus && (
            <p className={`upload-note note-${uploadStatus.type}`}>
              {uploadStatus.text}
            </p>
          )}

          {files.length > 0 && (
            <ul className="file-list">
              {files.map((f) => (
                <li key={f} className="file-item">
                  <span className="file-name">{f}</span>
                  <button
                    className="file-delete"
                    onClick={() => handleDelete(f)}
                    disabled={deletingFile === f}
                    aria-label={`Remove ${f}`}
                  >
                    {deletingFile === f ? "..." : "✕"}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="query-card">
          <span className="eyebrow">Question</span>
          <div className="query-row">
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="What would you like to know?"
              disabled={asking || files.length === 0}
              aria-label="Ask a question about your documents"
            />
            <button
              onClick={ask}
              disabled={asking || !question.trim() || files.length === 0}
            >
              {asking ? "Searching" : "Ask"}
            </button>
          </div>
          {files.length === 0 && (
            <p className="empty-hint">
              Add a document above before asking a question.
            </p>
          )}
        </section>

        {asking && (
          <div className="searching-row" role="status">
            <span className="stamp" aria-hidden="true">
              <span className="stamp-arm" />
              <span className="stamp-base" />
            </span>
            <span>Searching...</span>
          </div>
        )}

        {!asking && answer && (
          <section className="answer-card">
            <span className="eyebrow">Asked</span>
            <p className="asked-text">{askedQuestion}</p>

            <span className="eyebrow eyebrow-spaced">Answer</span>
            <p className="answer-text">{answer}</p>

            {sources.length > 0 && (
              <div className="card-footer">
                <span className="eyebrow eyebrow-small">Sources</span>
                <div className="source-row">
                  {sources.map((s, i) => (
                    <span key={i} className="source-stamp">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </section>
        )}

        {!asking && !answer && files.length > 0 && (
          <div className="idle-hint">
            <span className="idle-mark" aria-hidden="true" />
            Ask something above, I'll search{" "}
            {files.length === 1
              ? "this document"
              : `these ${files.length} documents`}{" "}
            for the answer.
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
