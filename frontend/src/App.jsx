import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import NegotiationPage from './pages/NegotiationPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground font-sans antialiased">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/negotiation/:id" element={<NegotiationPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
