import Card from './Card'

interface StatCardProps {
  title: string
  value: string | number
  description?: string
}

function StatCard({
  title,
  value,
  description,
}: StatCardProps) {
  return (
    <Card className="stat-card">
      <p className="stat-card-title">{title}</p>

      <p className="stat-card-value">
        {value}
      </p>

      {description && (
        <p className="stat-card-description">
          {description}
        </p>
      )}
    </Card>
  )
}

export default StatCard