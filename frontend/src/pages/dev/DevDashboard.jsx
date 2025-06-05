import React, { useEffect, useState, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import apiFetch from "../../utils/apiClient";
import "./DevDashboard.css";
import { toast } from "react-toastify";
import TemplateDriftTab from "./TemplateDriftTab";

export default function DevDashboard() {
  const [docs, setDocs] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [markdownContent, setMarkdownContent] = useState("");
  const [activeTab, setActiveTab] = useState("docs");
  const location = useLocation();
  const navigate = useNavigate();
  const markdownRef = useRef(null);

  const cleanupUnused = async () => {
    try {
      const res = await apiFetch('/assistants/cleanup-unused/', { method: 'DELETE' });
      toast.success(`🧹 Deleted ${res.deleted} assistants`);
    } catch (err) {
      console.error('Cleanup failed', err);
      toast.error('Cleanup failed');
    }
  };

  useEffect(() => {
    const loadDocs = async () => {
      try {
        const res = await apiFetch("/mcp/dev_docs/");
        const docList = Array.isArray(res) ? res : res.results || [];
        setDocs(docList);

        const params = new URLSearchParams(location.search);
        const requestedSlug = params.get("doc");

        const defaultDoc = requestedSlug
          ? docList.find((doc) => doc.slug === requestedSlug)
          : docList[0];

        if (defaultDoc) {
          loadDocContent(defaultDoc.slug);
        }
      } catch (err) {
        console.error("❌ Failed to load dev docs list:", err);
      }
    };
    loadDocs();
  }, [location.search]);

  const loadDocContent = async (slug) => {
    setSelectedDoc(slug);
    try {
      const res = await apiFetch(`/mcp/dev_docs/${slug}/`);
      setMarkdownContent(res.content || "⚠️ No content found.");
      setTimeout(() => {
        if (markdownRef.current) {
          markdownRef.current.scrollTop = 0;
        }
      }, 50);
    } catch (err) {
      console.error(`❌ Failed to load doc: ${slug}`, err);
      setMarkdownContent("⚠️ Failed to load file.");
    }
  };

  const reflectOnDoc = async () => {
    const doc = docs.find((d) => d.slug === selectedDoc);
    if (!doc) return;

    try {
      await apiFetch(`/mcp/dev_docs/${doc.id}/reflect/`, { method: "POST" });
      navigate(`/dev-docs/${doc.slug}/`);
    } catch (err) {
      console.error("❌ Reflection failed:", err);
    }
  };

  const renderBody = () => {
    if (activeTab === "docs") {
      return (
        <div className="row flex-grow-1" style={{ overflow: "hidden" }}>
          <div
            className="col-md-3 scroll-sidebar"
            style={{ overflowY: "auto", height: "100%", paddingRight: "1rem", borderRight: "1px solid #ccc" }}
          >
            <h5 className="mb-3">📚 Available Docs</h5>
            <ul className="list-group dev-doc-list">
              {docs.map((doc) => (
                <li
                  key={doc.slug}
                  className={`list-group-item ${doc.slug === selectedDoc ? "active" : ""}`}
                  onClick={() => loadDocContent(doc.slug)}
                  style={{ cursor: "pointer" }}
                >
                  {doc.title || doc.slug}
                </li>
              ))}
            </ul>
          </div>

          <div
            className="col-md-9 markdown-preview"
            ref={markdownRef}
            style={{ overflowY: "auto", height: "100%", paddingLeft: "1rem" }}
          >
            <div className="markdown-preview">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdownContent}</ReactMarkdown>
            </div>

            <button className="btn btn-outline-primary my-3" onClick={reflectOnDoc}>
              🪞 Reflect on This DevDoc
            </button>
          </div>
        </div>
      );
    }

    return <TemplateDriftTab />;
  };

  return (
    <div
      className="container-fluid mt-4 dev-dashboard"
      style={{ height: "100vh", overflow: "hidden", display: "flex", flexDirection: "column" }}
    >
      <div>
        <h2 className="mb-3">🧠 Dev Dashboard</h2>
        <Link to="/grouped-reflection" className="btn btn-outline-secondary my-3 me-2">
          🧠 View Grouped Reflection
        </Link>
        <button className="btn btn-outline-danger my-3" onClick={cleanupUnused}>
          🧹 Delete Unused Assistants
        </button>
        <Link to="/dev/route-explorer" className="btn btn-outline-secondary my-3 ms-2">
          🗺 Route Explorer
        </Link>
        <ul className="nav nav-tabs mt-2">
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "docs" ? "active" : ""}`}
              onClick={() => setActiveTab("docs")}
            >
              Dev Docs
            </button>
          </li>
          <li className="nav-item">
            <button
              className={`nav-link ${activeTab === "templates" ? "active" : ""}`}
              onClick={() => setActiveTab("templates")}
            >
              Template Drift
            </button>
          </li>
        </ul>
      </div>

      {renderBody()}
    </div>
  );
}
