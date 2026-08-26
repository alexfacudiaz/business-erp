import { Navigate, Route, Routes } from 'react-router-dom'

import AppLayout from './components/layout/AppLayout'

import DashboardPage from './pages/DashboardPage'
import CustomersPage from './pages/CustomersPage'
import SuppliersPage from './pages/SuppliersPage'
import ProductsPage from './pages/ProductsPage'
import SalesPage from './pages/SalesPage'
import PurchasesPage from './pages/PurchasesPage'
import StockAdjustmentsPage from './pages/StockAdjustmentsPage'

import './App.css'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />

        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/customers" element={<CustomersPage />} />
        <Route path="/suppliers" element={<SuppliersPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/sales" element={<SalesPage />} />
        <Route path="/purchases" element={<PurchasesPage />} />
        <Route
          path="/stock-adjustments"
          element={<StockAdjustmentsPage />}
        />
      </Route>
    </Routes>
  )
}

export default App