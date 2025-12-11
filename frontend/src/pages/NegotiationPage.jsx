import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, FileText, AlertTriangle, Check, X, Bot, Loader2, Play } from 'lucide-react';
import { cn } from '../lib/utils';
import api from '../lib/axios';

// Components
const MessageBubble = ({ role, content, meta }) => (
    <div className={cn("flex gap-3 animate-in fade-in slide-in-from-bottom-2", role === 'user' ? "flex-row-reverse" : "flex-row")}>
        <div className={cn("w-8 h-8 rounded-full flex items-center justify-center shrink-0 border shadow-sm",
            role === 'agent' ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground")}>
            {role === 'agent' ? <Bot size={16} /> : "U"}
        </div>
        <div className={cn("max-w-[80%] rounded-lg p-4 text-sm space-y-2 shadow-sm",
            role === 'user' ? "bg-primary text-primary-foreground" : "bg-muted")}>
            <div className="whitespace-pre-wrap">{content}</div>
            {meta && (
                <div className="bg-background/20 rounded p-2 text-xs mt-2 border border-white/10 italic">
                    {meta}
                </div>
            )}
        </div>
    </div>
);

export default function NegotiationPage() {
    const { id: threadId } = useParams();
    const [input, setInput] = useState('');
    const queryClient = useQueryClient();

    // 1. Fetch Thread State
    const { data: threadState, isLoading } = useQuery({
        queryKey: ['thread', threadId],
        queryFn: async () => {
            const res = await api.get(`/agent/thread/${threadId}`);
            return res.data;
        },
        refetchInterval: 2000, // Poll every 2s
    });

    // 2. Send Message Mutation
    const sendMessage = useMutation({
        mutationFn: async (text) => {
            // We use a fixed mock UUID for contract/supplier in this MVP since dashboard is mocked
            await api.post('/agent/negotiate', {
                contract_id: "00000000-0000-0000-0000-000000000000",
                supplier_id: "00000000-0000-0000-0000-000000000000",
                clause_text: text,
                thread_id: threadId
            });
        },
        onSuccess: () => {
            setInput('');
            queryClient.invalidateQueries(['thread', threadId]);
        }
    });

    // 3. Resume (Approve/Reject) Mutation
    const resumeWorkflow = useMutation({
        mutationFn: async ({ action, feedback }) => {
            await api.post('/agent/resume', {
                thread_id: threadId,
                action,
                feedback
            });
        },
        onSuccess: () => queryClient.invalidateQueries(['thread', threadId])
    });

    // 4. Simulate Supplier Turn Mutation
    const simulateTurn = useMutation({
        mutationFn: async () => {
            // 1. Get Simulation Response
            const history = messages.map(m => ({
                sender: m.role === 'user' ? 'supplier' : 'buyer', // Role mapping: User in UI is Buyer/Agent
                content: m.content
            }));
            const res = await api.post('/simulation/turn', {
                persona_id: "techflow-saas", // Hardcoded for Demo R2
                conversation_history: history,
                latest_proposal: messages[messages.length - 1]?.content || "Please provide your initial draft."
            });

            // 2. Feed it back as a message from Supplier
            // Note: In a real system, the Supplier Agent would call the API directly.
            // Here we proxy it via frontend to show the simulation flow.
            await api.post('/agent/negotiate', {
                contract_id: "00000000-0000-0000-0000-000000000000",
                supplier_id: "00000000-0000-0000-0000-000000000000",
                clause_text: res.data.response,
                thread_id: threadId
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries(['thread', threadId]);
        }
    });

    // Derived State
    const messages = threadState?.messages || [];

    const isPaused = threadState?.status === 'paused';
    const pendingContext = threadState?.current_context;

    return (
        <div className="flex h-screen overflow-hidden bg-background animate-in fade-in">

            {/* Left Pane: Intelligence */}
            <aside className="w-80 border-r bg-card/50 p-6 space-y-8 overflow-y-auto hidden md:block">
                <div>
                    <h2 className="text-lg font-bold mb-4 tracking-tight">Intel Context</h2>
                    {/* Mocked for now - in dynamic version we'd fetch Supplier Details */}
                    <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20 space-y-2">
                        <div className="text-red-500 font-bold flex items-center gap-2">
                            <AlertTriangle size={16} /> High Risk (85)
                        </div>
                        <p className="text-xs text-muted-foreground">Financial Stress Score: 20/100</p>
                        <p className="text-xs text-muted-foreground">News Sentiment: Negative</p>
                    </div>
                </div>

                {/* Simulation Controls (Release 2) */}
                <div className="border-t pt-6">
                    <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
                        <Bot size={14} className="text-blue-500" />
                        Simulation Control
                    </h3>
                    <div className="p-4 bg-blue-500/5 rounded-lg border border-blue-500/10 space-y-3">
                        <p className="text-xs text-muted-foreground">
                            Simulate the counter-party (TechFlow SaaS) response to your last message.
                        </p>
                        <button
                            onClick={() => simulateTurn.mutate()}
                            disabled={simulateTurn.isPending || isPaused}
                            className="w-full bg-blue-600 text-white h-8 rounded text-xs font-medium hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                        >
                            {simulateTurn.isPending ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
                            Simulate Supplier Turn
                        </button>
                    </div>
                </div>
            </aside>

            {/* Center Pane: The Timeline */}
            <main className="flex-1 flex flex-col min-w-0 relative">
                <header className="h-14 border-b flex items-center px-6 justify-between shrink-0">
                    <h1 className="font-semibold flex items-center gap-2">
                        Negotiation #{threadId.substring(0, 6)}
                        {isLoading && <Loader2 className="animate-spin w-3 h-3 text-muted-foreground" />}
                    </h1>
                    <div className="flex items-center gap-3">
                        <span className="text-xs bg-yellow-500/10 text-yellow-500 px-2 py-1 rounded border border-yellow-500/20">Agency: Medium</span>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-6 space-y-6 pb-32">
                    {/* Chat History */}
                    {messages.map((m, idx) => (
                        <MessageBubble key={idx} role={m.role} content={m.content} />
                    ))}

                    {/* Logic: If Pending Approval, show the Decision Block */}
                    {isPaused && pendingContext && (
                        <div className="mx-auto max-w-lg border border-primary/50 bg-primary/5 rounded-lg p-5 shadow-lg animate-in slide-in-from-bottom-5">
                            <h4 className="font-bold text-primary flex items-center gap-2 mb-3">
                                <Bot size={18} /> Proposed Strategy
                            </h4>
                            <div className="text-sm space-y-2 mb-4">
                                <p className="font-semibold">{pendingContext.strategy}</p>
                                <p className="text-muted-foreground italic">"{pendingContext.reasoning}"</p>
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => resumeWorkflow.mutate({ action: "APPROVED" })}
                                    className="flex-1 bg-primary text-primary-foreground h-9 rounded-md text-sm font-medium hover:bg-primary/90 transition-colors flex items-center justify-center gap-2"
                                    disabled={resumeWorkflow.isPending}
                                >
                                    {resumeWorkflow.isPending ? <Loader2 size={14} className="animate-spin" /> : <Check size={14} />}
                                    Approve
                                </button>
                                <button
                                    onClick={() => resumeWorkflow.mutate({ action: "REJECTED", feedback: "Too aggressive." })}
                                    className="flex-1 bg-muted text-foreground h-9 rounded-md text-sm font-medium hover:bg-muted/80 transition-colors flex items-center justify-center gap-2"
                                >
                                    <X size={14} /> Reject
                                </button>
                            </div>
                        </div>
                    )}

                    {/* If Scribe finished, show the redaction (Local visual only if not in history) */}
                    {pendingContext?.redline && !isPaused && (
                        <div className="mx-auto max-w-2xl border-l-4 border-green-500 pl-4 py-2 bg-green-500/5 cursor-pointer hover:bg-green-500/10 transition-colors">
                            <span className="text-xs text-green-500 font-bold uppercase tracking-wider mb-1 block">Draft Generated</span>
                            <p className="font-mono text-sm whitespace-pre-wrap">{pendingContext.redline}</p>
                        </div>
                    )}
                </div>

                <div className="p-4 border-t bg-card absolute bottom-0 w-full">
                    <div className="flex gap-2 max-w-4xl mx-auto">
                        <input
                            className="flex-1 bg-muted/50 border-input border rounded-md px-4 text-sm focus:outline-none focus:ring-1 focus:ring-primary h-10 transition-all"
                            placeholder="Paste contract clause or type instructions..."
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && !sendMessage.isPending && sendMessage.mutate(input)}
                            disabled={sendMessage.isPending || isPaused}
                        />
                        <button
                            onClick={() => sendMessage.mutate(input)}
                            disabled={sendMessage.isPending || isPaused || !input.trim()}
                            className="bg-primary text-primary-foreground w-10 h-10 flex items-center justify-center rounded-md hover:bg-primary/90 disabled:opacity-50 transition-all"
                        >
                            {sendMessage.isPending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
                        </button>
                    </div>
                </div>
            </main>

            {/* Right Pane: Document Placeholder */}
            <aside className="w-96 border-l bg-card/30 p-0 flex flex-col hidden lg:flex">
                <header className="h-14 border-b flex items-center px-6 justify-between bg-card/50 px-6">
                    <h3 className="font-semibold text-sm">Document Preview</h3>
                </header>
                <div className="flex-1 p-8 text-center text-muted-foreground text-sm flex flex-col items-center justify-center">
                    <FileText size={48} className="mb-4 opacity-20" />
                    <p>Select a clause to view diff.</p>
                </div>
            </aside>
        </div>
    );
}
