import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, AlertCircle, CheckCircle2, Clock, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { cn } from '../lib/utils';
import api from '../lib/axios';

const StatusBadge = ({ status }) => {
    const styles = {
        active: "bg-blue-500/10 text-blue-500", // Default active
        paused: "bg-red-500/10 text-red-500", // Human approval needed
        completed: "bg-green-500/10 text-green-500",

        // Mapped from mock types if needed, but backend sends active/paused/completed
        needs_approval: "bg-red-500/10 text-red-500",
        in_progress: "bg-yellow-500/10 text-yellow-500",
        waiting_supplier: "bg-blue-500/10 text-blue-500",
        closed: "bg-neutral-500/10 text-neutral-500",
    };

    const labels = {
        active: "In Progress",
        paused: "Action Required",
        completed: "Closed",

        needs_approval: "Action Required",
        in_progress: "Processing",
        waiting_supplier: "Waiting",
        closed: "Closed"
    };

    return (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium border border-current", styles[status] || styles.active)}>
            {labels[status] || status}
        </span>
    );
};

export default function DashboardPage() {
    const { data: negotiations, isLoading } = useQuery({
        queryKey: ['negotiations'],
        queryFn: async () => {
            const res = await api.get('/agent/negotiations');
            return res.data;
        },
        refetchInterval: 5000
    });

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Command Center</h1>
                    <p className="text-muted-foreground mt-2">Oversee active contract negotiations.</p>
                </div>
            </header>

            {isLoading ? (
                <div className="flex justify-center py-20">
                    <Loader2 className="animate-spin text-muted-foreground" size={32} />
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {negotiations?.map((item) => (
                        <Link key={item.id} to={`/negotiation/${item.id}`}>
                            <div className="border rounded-lg p-6 bg-card hover:bg-muted/50 transition-colors cursor-pointer space-y-4 shadow-sm">
                                <div className="flex justify-between items-start">
                                    <h3 className="font-semibold text-lg">{item.supplier}</h3>
                                    <span className={cn("text-xs font-bold", item.risk_score > 70 ? "text-red-500" : "text-green-500")}>
                                        Risk: {item.risk_score}
                                    </span>
                                </div>

                                <p className="text-sm font-medium">{item.contract_title}</p>
                                <p className="text-xs text-muted-foreground line-clamp-2 italic">{item.strategy || "Analyzing..."}</p>

                                <div className="flex justify-between items-center pt-2">
                                    <StatusBadge status={item.status} />
                                    <span className="text-xs text-muted-foreground flex items-center gap-1">
                                        <Clock className="w-3 h-3" /> Since: {new Date(item.last_update).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </Link>
                    ))}
                    {negotiations?.length === 0 && (
                        <div className="col-span-3 text-center py-20 text-muted-foreground border border-dashed rounded-lg">
                            No active negotiations found. Run the seed script to populate data.
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
