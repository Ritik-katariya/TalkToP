import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import "highlight.js/styles/github.css"; // Light theme for code blocks
import logo from '../image/logo.png';
 // Replace with your AI logo

const MessageList = ({ messages }) => {
  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="space-y-6">
        {messages.length === 0 ? (
          <p className="text-center text-gray-500">No messages yet.</p>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="flex space-x-3">
              {/* Avatar Section */}
              {message.sender === "user" ? (
                <div className="w-8 h-8 rounded-full bg-purple-200 flex items-center justify-center text-purple-700">
                  {message.avatar || "U"}
                </div>
              ) : message.sender === "ai" ? (
                <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center">
                  <img src={logo} alt="AI Avatar" className="w-6 h-6" />
                </div>
              ) : (
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                  <svg
                    className="w-4 h-4 text-gray-500"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12" y2="8"></line>
                  </svg>
                </div>
              )}

              {/* Message Content Section */}
              <div className="flex-1 bg-gray-100 p-3 rounded-lg max-w-[90%] break-words">
                {message.sender === "ai" ? (
                  // ✅ AI messages with Markdown rendering (without className)
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    rehypePlugins={[rehypeHighlight]}
                    components={{
                      p: ({ node, ...props }) => (
                        <p {...props} className="text-gray-800" />
                      ),
                      code: ({ node, inline, className, children, ...props }) =>
                        inline ? (
                          <code className="bg-gray-200 text-red-500 px-1 rounded" {...props}>
                            {children}
                          </code>
                        ) : (
                          <pre className="bg-gray-900 text-white p-2 rounded">
                            <code {...props}>{children}</code>
                          </pre>
                        ),
                    }}
                  >
                    {message.text}
                  </ReactMarkdown>
                ) : (
                  // ✅ User messages as plain text
                  <p className="text-gray-800">{message.text}</p>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MessageList;
