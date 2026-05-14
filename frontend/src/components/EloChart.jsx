import {
  AreaChart, Area, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from 'recharts'

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface border border-surface-hover rounded-lg px-3 py-2">
      <p className="text-text-primary text-sm font-semibold">
        {Math.round(payload[0].value)} ELO
      </p>
      <p className="text-text-muted text-xs">{payload[0].payload.date}</p>
    </div>
  )
}

export default function EloChart({ history = [] }) {
  if (history.length === 0) {
    return (
      <div className="bg-surface border border-surface-hover rounded-2xl p-6">
        <p className="text-text-secondary text-sm font-medium mb-4">Evoluție ELO</p>
        <div className="h-32 flex items-center justify-center">
          <p className="text-text-muted text-sm">Rezolvă sarcini pentru a vedea graficul</p>
        </div>
      </div>
    )
  }

  const data = history
    .slice()
    .reverse()
    .slice(-20)
    .map((item, idx) => ({
      idx: idx + 1,
      elo: item.elo_after,
      date: new Date(item.solved_at).toLocaleDateString('ro-RO', {
        day: '2-digit',
        month: '2-digit',
      }),
    }))

  const rawMin = Math.min(...data.map(d => d.elo));
  const rawMax = Math.max(...data.map(d => d.elo));
  const minElo = Math.floor(rawMin / 100) * 100 - 100;
  const maxElo = Math.ceil(rawMax / 100) * 100 + 100;

  const yTicks = [];
    for (let i = minElo; i <= maxElo; i += 100) {
    yTicks.push(i);
    }
  return (
    <div className="bg-surface border border-surface-hover rounded-2xl p-6">
      <p className="text-text-secondary text-sm font-medium mb-4">Evoluție ELO</p>
      <ResponsiveContainer width="100%" height={140}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="eloGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#273548" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: '#475569', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[minElo, maxElo]}
            ticks={yTicks} // Forțează axa să afișeze doar valorile din 100 în 100
            tick={{ fill: '#475569', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            width={45}
            tickFormatter={(value) => Math.round(value)}
            />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="elo"
            stroke="#8B5CF6"
            strokeWidth={2}
            fill="url(#eloGradient)"
            dot={false}
            activeDot={{ r: 4, fill: '#8B5CF6' }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}