import { NavLink } from 'react-router-dom'

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>ERP System</h1>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/customers">Customers</NavLink>
        <NavLink to="/suppliers">Suppliers</NavLink>
        <NavLink to="/products">Products</NavLink>
        <NavLink to="/sales">Sales</NavLink>
        <NavLink to="/purchases">Purchases</NavLink>
        <NavLink to="/stock-adjustments">Stock adjustments</NavLink>
      </nav>
    </aside>
  )
}

export default Sidebar