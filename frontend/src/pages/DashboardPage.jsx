import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { cn } from '../lib/utils';

// Mock Data
const negotiations = [
    { id: '1', supplier: 'Acme Corp', status: 'needs_approval', risk: 85, lastUpdate: '2h ago', snippet: 'Counter-offer pending approval' },
    { id: '2', supplier: 'Globex Inc', status: 'in_progress', risk: 40, lastUpdate: '5m ago', snippet: 'Agent analyzing response' },
    { id: '3', supplier: 'Soylent Corp', status: 'waiting_supplier', risk: 20, lastUpdate: '1d ago', snippet: 'Waiting for reply' },
    { id: '4', supplier: 'Umbrella Corp', status: 'closed', risk: 99, lastUpdate: '2d ago', snippet: 'Contract Rejected' },
];

const StatusBadge = ({ status }) => {
    const styles = {
        needs_approval: "bg-red-500/10 text-red-500",
        in_progress: "bg-yellow-500/10 text-yellow-500",
        waiting_supplier: "bg-blue-500/10 text-blue-500",
        closed: "bg-neutral-500/10 text-neutral-500",
    };

    const labels = {
        needs_approval: "Action Required",
        in_progress: "Processing",
        waiting_supplier: "Waiting",
        closed: "Closed"
    };

    return (
        <span className={cn("px-2 py-1 rounded-full text-xs font-medium border border-current", styles[status])}>
            {labels[status]}
        </span>
    );
};

export default function DashboardPage() {
    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <header className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Command Center</h1>
                    <p className="text-muted-foreground mt-2">Oversee active contract negotiations.</p>
                </div>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {negotiations.map((item) => (
                    <Link key={item.id} to={`/negotiation/${item.id}`}>
                        <div className="border rounded-lg p-6 bg-card hover:bg-muted/50 transition-colors cursor-pointer space-y-4 shadow-sm">
                            <div className="flex justify-between items-start">
                                <h3 className="font-semibold text-lg">{item.supplier}</h3>
                                <span className={cn("text-xs font-bold", item.risk > 70 ? "text-red-500" : "text-green-500")}>
                                    Risk: {item.risk}
                                </span>
                            </div>

                            <p className="text-sm text-muted-foreground line-clamp-2">{item.snippet}</p>

                            <div className="flex justify-between items-center pt-2">
                                <StatusBadge status={item.status} />
                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                    <Clock className="w-3 h-3" /> {item.lastUpdate}
                                </span>
                            </div>
                        </div>
                    </Link>
                ))}
            </div>
        </div>
    );
}
