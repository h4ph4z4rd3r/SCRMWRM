import React from 'react';

const Dashboard = () => {
    return (
        <div>
            <h2>Dashboard</h2>
            <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
                Welcome to the Negotiator War Room. Select a module to begin.
            </p>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '1.5rem',
                marginTop: '2rem'
            }}>
                {['Active Negotiations', 'Policy Updates', 'Supplier Risks'].map(item => (
                    <div key={item} style={{
                        backgroundColor: 'var(--bg-secondary)',
                        padding: '1.5rem',
                        borderRadius: 'var(--radius-md)',
                        border: '1px solid var(--bg-hover)'
                    }}>
                        <h3 style={{ fontSize: '1.1rem', marginBottom: '0.5rem' }}>{item}</h3>
                        <div style={{ height: '100px', background: 'var(--bg-hover)', borderRadius: 'var(--radius-sm)' }}></div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Dashboard;
