import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import styles from './DashboardLayout.module.css';

const DashboardLayout = () => {
    return (
        <div className={styles.container}>
            <aside className={styles.sidebar}>
                <div className={styles.logo}>
                    <h2>Negotiator<span style={{ color: 'var(--accent-primary)' }}>.AI</span></h2>
                </div>
                <nav className={styles.nav}>
                    <NavLink to="/" className={({ isActive }) => isActive ? `${styles.item} ${styles.active}` : styles.item}>
                        Dashboard
                    </NavLink>
                    <NavLink to="/policies" className={({ isActive }) => isActive ? `${styles.item} ${styles.active}` : styles.item}>
                        Policy Engine
                    </NavLink>
                    <NavLink to="/suppliers" className={({ isActive }) => isActive ? `${styles.item} ${styles.active}` : styles.item}>
                        Supplier Intel
                    </NavLink>
                    <NavLink to="/contracts" className={({ isActive }) => isActive ? `${styles.item} ${styles.active}` : styles.item}>
                        Contract Foundry
                    </NavLink>
                </nav>
                <div className={styles.user}>
                    <div className={styles.avatar}>CM</div>
                    <div className={styles.info}>
                        <p className={styles.name}>Contract Mgr</p>
                        <p className={styles.role}>Admin</p>
                    </div>
                </div>
            </aside>
            <main className={styles.main}>
                <header className={styles.header}>
                    <h1 className={styles.pageTitle}>Overview</h1>
                    <div className={styles.actions}>
                        <button className={styles.btnPrimary}>+ New Negotiation</button>
                    </div>
                </header>
                <div className={styles.content}>
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default DashboardLayout;
