import UploadPanel from "@/components/UploadPanel";
import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8 flex flex-col">
      <header className="mb-8 mt-4">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-center">
          <span style={{ color: 'var(--neon-purple)' }}>Graph</span>
          <span style={{ color: 'var(--neon-blue)' }}>RAG</span>
          <span className="text-white opacity-80"> System</span>
        </h1>
        <p className="text-center text-gray-400 mt-2 text-lg">Intelligent Multi-Hop Document Reasoning</p>
      </header>

      <div className="flex-1 max-w-7xl w-full mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8 h-full min-h-[70vh]">
        
        {/* Left Side: Upload Panel (takes up 4 columns on large screens) */}
        <div className="lg:col-span-4 flex flex-col justify-start">
          <UploadPanel />
          
          <div className="mt-8 glass-panel p-6 animate-fade-in" style={{ animationDelay: '0.2s' }}>
             <h3 className="text-lg font-semibold mb-3 text-purple-300">How it works</h3>
             <ul className="text-sm text-gray-400 space-y-3">
               <li className="flex gap-2"><span className="text-blue-400">1.</span> Upload your documents.</li>
               <li className="flex gap-2"><span className="text-blue-400">2.</span> The system extracts entities and relationships into Neo4j.</li>
               <li className="flex gap-2"><span className="text-blue-400">3.</span> Text chunks are embedded into ChromaDB.</li>
               <li className="flex gap-2"><span className="text-blue-400">4.</span> Ask a question to trigger hybrid retrieval!</li>
             </ul>
          </div>
        </div>

        {/* Right Side: Chat Interface (takes up 8 columns on large screens) */}
        <div className="lg:col-span-8 h-full flex flex-col">
          <ChatInterface />
        </div>

      </div>
    </main>
  );
}
