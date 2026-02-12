import { useState } from "react";
import { Collapsible } from "radix-ui";
import {
  Home,
  Building,
  Building2,
  Store,
  MapPin,
  User,
  ChevronRight,
  MoreHorizontal,
} from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardAction,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import type { Property, PropertySummary, PropertyType } from "@/types";
import type { LucideIcon } from "lucide-react";

const typeIcons: Record<PropertyType, LucideIcon> = {
  house: Home,
  apartment: Building,
  building: Building2,
  commercial: Store,
};

const typeLabels: Record<string, string> = {
  house: "House",
  apartment: "Apartment",
  building: "Building",
  commercial: "Commercial",
};

interface PropertyCardViewProps {
  properties: Property[];
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

export function PropertyCardView({ properties, onEdit, onDelete }: PropertyCardViewProps) {
  if (properties.length === 0) {
    return (
      <div className="flex h-24 items-center justify-center text-sm text-muted-foreground">
        No properties found.
      </div>
    );
  }

  return (
    <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {properties.map((property) => (
        <PropertyCard
          key={property.id}
          property={property}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

interface PropertyCardProps {
  property: Property;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

function PropertyCard({ property, onEdit, onDelete }: PropertyCardProps) {
  const [childrenOpen, setChildrenOpen] = useState(false);
  const TypeIcon = typeIcons[property.property_type];
  const hasChildren = property.child_properties.length > 0;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <TypeIcon className="size-5 text-muted-foreground" />
          <CardTitle className="text-base">{property.name}</CardTitle>
        </div>
        <CardDescription>
          <Badge variant="outline">{typeLabels[property.property_type]}</Badge>
        </CardDescription>
        <CardAction>
          <ActionsMenu
            onEdit={() => onEdit(property.id)}
            onDelete={() => onDelete(property.id)}
          />
        </CardAction>
      </CardHeader>

      <CardContent className="space-y-2 text-sm">
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <MapPin className="size-3.5 shrink-0" />
          <span className="truncate">{formatAddress(property)}</span>
        </div>
        {property.client_name && (
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <User className="size-3.5 shrink-0" />
            <span>{property.client_name}</span>
          </div>
        )}
        <div className="flex items-center gap-1.5 text-muted-foreground">
          <span className={cn(
            "size-2 rounded-full",
            property.is_active ? "bg-emerald-500" : "bg-gray-400"
          )} />
          <span className="text-xs">{property.is_active ? "Active" : "Inactive"}</span>
        </div>
      </CardContent>

      {hasChildren && (
        <CardFooter className="flex-col items-stretch">
          <Collapsible.Root open={childrenOpen} onOpenChange={setChildrenOpen}>
            <Collapsible.Trigger asChild>
              <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
                <ChevronRight
                  className={cn("size-4 transition-transform", childrenOpen && "rotate-90")}
                />
                {property.child_properties.length} apartment
                {property.child_properties.length !== 1 ? "s" : ""}
              </Button>
            </Collapsible.Trigger>
            <Collapsible.Content>
              <div className="mt-2 space-y-1 border-t pt-2">
                {property.child_properties.map((child) => (
                  <ChildRow
                    key={child.id}
                    child={child}
                    onEdit={onEdit}
                    onDelete={onDelete}
                  />
                ))}
              </div>
            </Collapsible.Content>
          </Collapsible.Root>
        </CardFooter>
      )}
    </Card>
  );
}

interface ChildRowProps {
  child: PropertySummary;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

function ChildRow({ child, onEdit, onDelete }: ChildRowProps) {
  return (
    <div className="flex items-center justify-between py-1 pl-6 text-sm">
      <div className="min-w-0 flex-1">
        <span className={cn("truncate", !child.is_active && "text-muted-foreground line-through")}>{child.name}</span>
        {child.client_name && (
          <span className="ml-2 text-muted-foreground">· {child.client_name}</span>
        )}
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <ActionsMenu
          onEdit={() => onEdit(child.id)}
          onDelete={() => onDelete(child.id)}
        />
      </div>
    </div>
  );
}

function ActionsMenu({ onEdit, onDelete }: { onEdit: () => void; onDelete: () => void }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon-xs">
          <MoreHorizontal />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={onEdit}>Edit</DropdownMenuItem>
        <DropdownMenuItem
          className="text-destructive focus:text-destructive"
          onClick={onDelete}
        >
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function formatAddress(property: Property): string {
  const parts = [property.address, property.city].filter(Boolean);
  return parts.length > 0 ? parts.join(", ") : "No address";
}
