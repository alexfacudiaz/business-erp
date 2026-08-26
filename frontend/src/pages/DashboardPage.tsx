import StatCard from '../components/ui/StatCard'

function DashboardPage() {
  return (
    <div className="dashboard">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>General system overview.</p>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Active customers"
          value="128"
          description="Registered customers"
        />

        <StatCard
          title="Active suppliers"
          value="24"
          description="Registered suppliers"
        />

        <StatCard
          title="Products"
          value="356"
          description="Registered products"
        />

        <StatCard
          title="Low stock"
          value="12"
          description="Products below minimum"
        />
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h2>Sales</h2>

          <div className="summary-row">
            <span>Sales this month</span>
            <strong>42</strong>
          </div>

          <div className="summary-row">
            <span>Pending sales</span>
            <strong>5</strong>
          </div>
        </div>

        <div className="dashboard-section">
          <h2>Purchases</h2>

          <div className="summary-row">
            <span>Purchases this month</span>
            <strong>18</strong>
          </div>

          <div className="summary-row">
            <span>Pending purchases</span>
            <strong>3</strong>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage