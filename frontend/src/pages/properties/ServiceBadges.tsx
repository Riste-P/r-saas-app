import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import type { ServiceBadge } from "@/types";

function abbreviate(name: string): string {
  return name
    .split(/[\s/]+/)
    .map((w) => w[0])
    .filter(Boolean)
    .join("")
    .toUpperCase();
}

export function ServiceBadges({ services }: { services: ServiceBadge[] }) {
  const active = services.filter((s) => s.is_active);

  if (active.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1">
      {active.map((s) => (
        <Tooltip key={s.service_type_name}>
          <TooltipTrigger asChild>
            <Badge
              variant="secondary"
              className="cursor-default px-1.5 py-0 text-[10px] leading-4"
            >
              {abbreviate(s.service_type_name)}
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p>{s.service_type_name}</p>
            <p className="text-primary-foreground/70">${Number(s.effective_price).toFixed(2)}</p>
          </TooltipContent>
        </Tooltip>
      ))}
    </div>
  );
}
