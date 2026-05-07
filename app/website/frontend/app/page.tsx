"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown"

export default function Home() {
  const [url, setUrl] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [loading, setLoading] = useState(false);

  const downloadMarkdown = () => {
    if (!markdown) return;

    const blob = new Blob([markdown], {
      type: "text/markdown",
    });

    const fileUrl = window.URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = fileUrl;
    link.download = "README.md";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    window.URL.revokeObjectURL(fileUrl);
  };

  const handleConvert = async () => {
    if (!url) return;

    setLoading(true);

    try {
      // const response = await fetch(`https://chat2readme-d2yf.vercel.app/convert`, {
      //   method: "POST",
      //   headers: {
      //     "Content-Type": "application/json",
      //   },
      //   body: JSON.stringify({
      //     url,
      //     include_links: true,
      //   }),
      // });
      const response = await fetch(`https://chat2readme-d2yf.vercel.app/convert`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ url, include_links: true }),
});


      // const data = await response.json();

      // setMarkdown(data.markdown);
      // Always check if response is ok BEFORE parsing JSON
if (!response.ok) {
  const errText = await response.text();   // safe — won't crash on HTML
  console.error("Server error:", errText);
  alert(`Server error ${response.status}`);
  return;
}

const data = await response.json();
setMarkdown(data.markdown);
    } catch (error) {
      console.error(error);
      alert("Conversion failed");
    }

    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <div className="w-full max-w-3xl space-y-6">
        <h1 className="text-5xl font-bold">
          Chat2Readme
        </h1>

        <p className="text-zinc-400">
          Convert ChatGPT shared chats into beautiful README.md files.
        </p>

        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Paste ChatGPT share URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 p-4 rounded-xl bg-zinc-900 border border-zinc-700"
          />

          <button
            onClick={handleConvert}
            disabled={loading}
            className="bg-white text-black px-6 rounded-xl font-semibold"
          >
            {loading ? "Converting..." : "Convert"}
          </button>
        </div>

        {markdown && (
          <div className="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
            {/* MARKDOWN PREVIEW */}
            <div className="bg-zinc-900 rounded-2xl border border-zinc-800 p-6 overflow-auto">
              <h2 className="text-2xl font-semibold mb-4">
                Preview
              </h2>
              <article className="prose prose-invert max-w-none">
                <ReactMarkdown>
                  {markdown}
                </ReactMarkdown>
              </article>

            </div>

            <br />


            <div className="bg-zinc-900 rounded-2xl border border-zinc-800 p-6 overflow-auto">
              <h2 className="text-2xl font-semibold mb-4">
                Generated Markdown
              </h2>

              <textarea
                value={markdown}
                readOnly
                className="w-full h-100 bg-black p-4 rounded-xl text-sm"
              />

              <button
                onClick={() => navigator.clipboard.writeText(markdown)}
                className="mt-4 bg-white text-black px-4 py-2 rounded-lg"
              >
                Copy Markdown
              </button>
            </div>

            <br />

            <button
              onClick={downloadMarkdown}
              className="px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white transition"
            >
              Download README.md
            </button>

          </div>


        )}
      </div>
    </main>
  );
}