import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import { PolicyEngine, SupplierIntel, ContractFoundry } from './pages/Modules';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="policies" element={<PolicyEngine />} />
          <Route path="suppliers" element={<SupplierIntel />} />
          <Route path="contracts" element={<ContractFoundry />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
