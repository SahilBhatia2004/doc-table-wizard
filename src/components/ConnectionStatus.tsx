import { useEffect, useState } from "react";
import { Wifi, WifiOff, Database, Loader2 } from "lucide-react";
import { checkHealth, type HealthCheck } from "@/lib/api";

export function ConnectionStatus() {
  const [status, setStatus] = useState<"checking" | "connected" | "disconnected">("checking");
  const [health, setHealth] = useState<HealthCheck | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const result = await checkHealth();
        setHealth(result);
        setStatus("connected");
      } catch {
        setStatus("disconnected");
      }
    };

    check();
    const interval = setInterval(check, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center gap-3 text-sm">
      <div className="flex items-center gap-1.5">
        {status === "checking" ? (
          <Loader2 className="w-3.5 h-3.5 animate-spin text-muted-foreground" />
        ) : status === "connected" ? (
          <Wifi className="w-3.5 h-3.5 text-success" />
        ) : (
          <WifiOff className="w-3.5 h-3.5 text-destructive" />
        )}
        <span className={status === "connected" ? "text-success" : status === "disconnected" ? "text-destructive" : "text-muted-foreground"}>
          {status === "checking" ? "Checking..." : status === "connected" ? "API Connected" : "API Offline"}
        </span>
      </div>
      
      {health && (
        <div className="flex items-center gap-1.5 pl-3 border-l border-border">
          <Database className={`w-3.5 h-3.5 ${health.database === "connected" ? "text-success" : "text-warning"}`} />
          <span className={health.database === "connected" ? "text-success" : "text-warning"}>
            {health.database === "connected" ? "DB Connected" : "DB Error"}
          </span>
        </div>
      )}
    </div>
  );
}
