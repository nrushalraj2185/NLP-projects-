import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, Paperclip, Trash2, Maximize2, Minimize2, Search, Settings } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  role: 'user' | 'model';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      if (data.content) {
        const userMsgContent = `Uploaded file: ${file.name}\n\n[System: Document content attached]`;
        setMessages(prev => [...prev, { role: 'user', content: userMsgContent }]);

        const chatResponse = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `I've uploaded a file named ${file.name}. Here is its content: ${data.content}. Please summarize it and tell me how you can help me with it.`,
            history: messages.map(m => ({ role: m.role, parts: [m.content] }))
          }),
        });
        const chatData = await chatResponse.json();
        if (chatData.response) {
          setMessages(prev => [...prev, { role: 'model', content: chatData.response }]);
        }
      } else {
        alert(data.error || 'Failed to process file');
      }
    } catch (error) {
      alert('Error uploading file');
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          history: messages.map(m => ({
            role: m.role,
            parts: [m.content]
          }))
        }),
      });

      const data = await response.json();
      if (data.response) {
        setMessages(prev => [...prev, { role: 'model', content: data.response }]);
      } else {
        setMessages(prev => [...prev, { role: 'model', content: 'Sorry, I encountered an error: ' + (data.error || 'Unknown error') }]);
      }
    } catch (error) {
      setMessages(prev => [...prev, { role: 'model', content: 'Connection error. Please check if the backend is running.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages, isLoading]);

  return (
    <div className="main-bg flex h-screen w-full items-center justify-center p-0 md:p-6 transition-all duration-500 overflow-hidden">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        className="hidden"
        accept=".pdf,.docx,.png,.jpg,.jpeg"
      />

      <motion.div
        layout
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        className={`glass-panel relative flex flex-col overflow-hidden shadow-[0_0_50px_-12px_rgba(0,0,0,0.5)] transition-all duration-500 ${isFullscreen ? 'h-full w-full rounded-none' : 'h-[90vh] w-full max-w-6xl rounded-3xl md:border'
          }`}
      >
        {/* Top Navbar */}
        <header className="z-20 flex h-20 items-center justify-between border-b border-white/5 bg-black/20 px-6 backdrop-blur-xl">
          <div className="flex items-center gap-4">
            <div className="relative group">
              <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-violet-600 to-blue-600 opacity-40 blur-md transition group-hover:opacity-75"></div>
              <div className="relative flex h-12 w-12 items-center justify-center rounded-2xl bg-[#11111a] border border-white/10 shadow-xl">
                <Sparkles className="h-6 w-6 text-violet-400 group-hover:scale-110 transition-transform" />
              </div>
            </div>
            <div>
              <h1 className="font-display text-xl font-bold tracking-tight text-white/90">Nova <span className="text-violet-500">AI</span></h1>
              <div className="flex items-center gap-2">
                <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                <span className="text-[10px] font-semibold uppercase tracking-widest text-white/30">Intelligence Hub</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button className="flex h-10 w-10 items-center justify-center rounded-xl text-white/40 hover:bg-white/5 hover:text-white transition-all">
              <Search className="h-5 w-5" />
            </button>
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="flex h-10 w-10 items-center justify-center rounded-xl text-white/40 hover:bg-white/5 hover:text-white transition-all"
            >
              {isFullscreen ? <Minimize2 className="h-5 w-5" /> : <Maximize2 className="h-5 w-5" />}
            </button>
            <button
              onClick={() => setMessages([])}
              className="flex h-10 w-10 items-center justify-center rounded-xl text-white/40 hover:bg-red-500/10 hover:text-red-400 transition-all"
            >
              <Trash2 className="h-5 w-5" />
            </button>
            <div className="h-6 w-px bg-white/10 mx-2"></div>
            <button className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/5 text-white/60 hover:text-white transition-all">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </header>

        {/* Content Area */}
        <main className="relative flex-1 flex flex-col min-h-0 bg-gradient-to-b from-transparent to-black/20">
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto px-4 py-8 md:px-10 scroll-smooth"
          >
            <div className="mx-auto flex max-w-4xl flex-col gap-8">
              {messages.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-20 flex flex-col items-center text-center space-y-8"
                >
                  <div className="relative">
                    <div className="absolute -inset-4 rounded-full bg-violet-500/10 blur-2xl"></div>
                    <div className="relative flex h-24 w-24 items-center justify-center rounded-[2rem] bg-indigo-500/10 border border-indigo-500/20 shadow-2xl">
                      <Bot className="h-12 w-12 text-indigo-400" />
                    </div>
                  </div>
                  <div className="space-y-3">
                    <h2 className="font-display text-4xl font-bold text-white leading-tight">Welcome to the future of <br /> <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-blue-400">Assistance</span></h2>
                    <p className="mx-auto max-w-md text-white/40 text-lg">
                      Nova is ready to analyze your documents, process images, and help you build amazing things.
                    </p>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl px-4">
                    {[
                      "Explain quantum mechanics simply",
                      "How do I analyze this PDF document?",
                      "Write a professional email for me",
                      "Analyze the sentiment of this text"
                    ].map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => setInput(suggestion)}
                        className="p-4 rounded-2xl bg-white/[0.03] border border-white/5 text-left text-sm text-white/60 hover:bg-white/[0.06] hover:border-white/10 transition-all group"
                      >
                        <span className="group-hover:text-white transition-colors">{suggestion}</span>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              <AnimatePresence initial={false}>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, scale: 0.98, y: 10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    className={`flex items-start gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                  >
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl shadow-lg ${msg.role === 'user'
                      ? 'bg-violet-600 shadow-violet-600/20 ring-1 ring-violet-400/50'
                      : 'bg-[#1e1e2d] border border-white/10'
                      }`}>
                      {msg.role === 'user' ? <User className="h-5 w-5 text-white" /> : <Bot className="h-5 w-5 text-indigo-400" />}
                    </div>
                    <div className={`group relative max-w-[85%] rounded-[1.25rem] px-5 py-4 text-[15px] leading-relaxed transition-all ${msg.role === 'user'
                      ? 'bg-violet-600 border border-violet-500/50 text-white shadow-xl shadow-violet-600/10'
                      : 'bg-[#11111a]/80 border border-white/5 text-slate-200 backdrop-blur-md shadow-lg group-hover:border-white/10'
                      }`}>
                      <div className="whitespace-pre-wrap font-sans">{msg.content}</div>
                      <div className={`absolute -bottom-6 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] uppercase font-bold text-white/20 tracking-widest ${msg.role === 'user' ? 'right-0' : 'left-0'
                        }`}>
                        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {isLoading && (
                <div className="flex items-start gap-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#1e1e2d] border border-white/10">
                    <Loader2 className="h-5 w-5 animate-spin text-indigo-400" />
                  </div>
                  <div className="flex items-center gap-1.5 rounded-2xl bg-white/[0.03] border border-white/5 px-6 py-4 backdrop-blur-sm">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500/50" style={{ animationDelay: '0ms' }}></span>
                    <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500/50" style={{ animationDelay: '200ms' }}></span>
                    <span className="h-2 w-2 animate-bounce rounded-full bg-indigo-500/50" style={{ animationDelay: '400ms' }}></span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Typing Area */}
          <div className="p-6 md:px-10 md:pb-10 pt-4 z-10">
            <div className="mx-auto max-w-4xl">
              <div className="relative flex flex-col gap-1 rounded-3xl bg-[#11111a]/80 border border-white/10 p-2 backdrop-blur-2xl shadow-2xl focus-within:border-violet-500/50 transition-all group">
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSend();
                    }
                  }}
                  placeholder="Ask Nova anything..."
                  rows={1}
                  className="w-full resize-none bg-transparent px-5 py-4 text-white placeholder-white/20 focus:outline-none min-h-[58px] max-h-48 overflow-y-auto"
                />

                <div className="flex items-center justify-between px-3 pb-2 pt-1">
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="flex h-10 w-10 items-center justify-center rounded-xl text-white/30 hover:bg-white/5 hover:text-white transition-all group/btn"
                      title="Attach documents"
                    >
                      <Paperclip className="h-5 w-5 group-hover/btn:rotate-12 transition-transform" />
                    </button>
                    <div className="h-4 w-px bg-white/5 mx-1"></div>
                    <span className="text-[10px] font-bold text-white/10 uppercase tracking-widest px-2">GPT-4.0 Equivalent Engine</span>
                  </div>

                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-all ${input.trim() && !isLoading
                      ? 'bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:scale-105 active:scale-95'
                      : 'bg-white/5 text-white/10 cursor-not-allowed'
                      }`}
                  >
                    <Send className="h-5 w-5" />
                  </button>
                </div>
              </div>
              <div className="mt-4 flex items-center justify-center gap-2 text-[10px] font-bold tracking-[0.2em] text-white/10 uppercase">
                <Sparkles className="h-3 w-3" />
                Nova Intelligence Hub v2.0
              </div>
            </div>
          </div>
        </main>
      </motion.div>
    </div>
  );
}

export default App;
