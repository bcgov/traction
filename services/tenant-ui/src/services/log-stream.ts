import { IncomingMessage, Server } from "http";
import axios from "axios";
import config from "config";
import jwt from "jsonwebtoken";
import WebSocket from "ws";

const LOKI_URL: string = config.get("server.lokiUrl");
const TRACTION_URL: string = config.get("server.tractionUrl");

const wss = new WebSocket.Server({ noServer: true });

const getTenant = async (token: string): Promise<any> => {
  const response = await axios.get(`${TRACTION_URL}/tenant`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};

const parseToken = (url: URL): string | null => {
  const token = url.searchParams.get("token");
  return token;
};

const authenticateTenant = async (
  req: IncomingMessage
): Promise<any | never> => {
  const token = parseToken(
    new URL(req.url as string, `http://${req.headers.host}`)
  );

  if (!token) {
    throw new Error("Unauthorized: No token provided");
  }

  const decodedToken = jwt.decode(token, { complete: true });
  if (!decodedToken) {
    throw new Error("Unauthorized: Invalid token");
  }

  const tenant = await getTenant(token);
  if (!tenant) {
    throw new Error("Unauthorized: Tenant not found");
  }

  return tenant;
};

const logError = (err: Error) => {
  console.error(`Error: ${err}`);
};

const handleLokiWebSocket = (tenantId: string, ws: WebSocket) => {
  const loki = new WebSocket(
    `${LOKI_URL}/loki/api/v1/tail?query={container_name="scripts-traction-agent-1"} |= \`${tenantId}\``
  );

  loki.on("open", () => {
    console.log(`Loki websocket established for Tenant ID: ${tenantId}`);
  });

  loki.on("message", (message) => {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(message.toString());
    }
  });

  loki.on("error", (err) => {
    console.error(`Loki websocket for Tenant ID: ${tenantId} error: ${err}`);
    if (ws?.readyState === WebSocket.OPEN) {
      ws.close();
    }
  });

  loki.on("close", () => {
    console.log(`Loki websocket closed for Tenant ID: ${tenantId}`);
    if (ws?.readyState === WebSocket.OPEN) {
      ws.close();
    }
  });

  return loki;
};

const handleTenantWebSocket = (
  tenantId: string,
  ws: WebSocket,
  loki: WebSocket
): void => {
  ws.on("open", () => {
    console.log(`Tenant websocket established for Tenant ID: ${tenantId}`);
  });

  ws.on("error", (err) => {
    console.error(`Tenant webSocket for Tenant ID: ${tenantId} error: ${err}`);
    if (loki?.readyState === WebSocket.OPEN) {
      loki.close();
    }
  });

  ws.on("close", () => {
    console.log(`Tenant websocket closed for Tenant ID: ${tenantId}`);
    if (loki?.readyState === WebSocket.OPEN) {
      loki.close();
    }
  });
};

export const configureLogStream = (server: Server): void => {
  server.on(
    "upgrade",
    async (req: IncomingMessage & { tenant: any }, socket, head) => {
      // Socket pre upgrade
      socket.on("error", logError);

      try {
        req.tenant = await authenticateTenant(req);
      } catch (err: any | Error) {
        socket.write(`HTTP/1.1 401 ${err.message}\r\n\r\n`);
        socket.destroy();
        return;
      }

      wss.handleUpgrade(req, socket, head, (ws) => {
        // Socket post upgrade
        socket.removeListener("error", logError);
        wss.emit("connection", ws, req);
      });
    }
  );

  wss.on("connection", (ws, req: IncomingMessage & { tenant: any }) => {
    const { tenant_id: tenantId = null } = req.tenant;
    const loki = handleLokiWebSocket(tenantId, ws);
    handleTenantWebSocket(tenantId, ws, loki);
  });
};
