import { Users, UserCheck, DollarSign, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDashboardStats } from "@/hooks/useDashboard";

export default function DashboardPage() {
  const { data: stats, isLoading } = useDashboardStats();

  if (isLoading) {
    return <p className="text-muted-foreground">Loading stats...</p>;
  }

  const cards = [
    {
      title: "Total Users",
      value: stats?.total_users ?? 0,
      icon: Users,
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: "Active Users",
      value: stats?.active_users ?? 0,
      icon: UserCheck,
      format: (v: number) => v.toLocaleString(),
    },
    {
      title: "Revenue",
      value: stats?.revenue ?? 0,
      icon: DollarSign,
      format: (v: number) => `$${v.toLocaleString(undefined, { minimumFractionDigits: 2 })}`,
    },
    {
      title: "Growth",
      value: stats?.growth ?? 0,
      icon: TrendingUp,
      format: (v: number) => `${v > 0 ? "+" : ""}${v}%`,
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold">Dashboard</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Overview for {stats?.tenant}
      </p>
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map((card) => (
          <Card key={card.title}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              <card.icon className="size-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {card.format(card.value)}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
