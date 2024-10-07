import { Server } from "http";
import WebSocket from "ws";

const WEBSOCKET_URL = "ws://host.docker.internal:3100/loki/api/v1/tail";

const wss = new WebSocket.Server({ noServer: true });

const handleLokiWebSocket = (tenantId: string, ws: WebSocket) => {
  const loki = new WebSocket(
    `${WEBSOCKET_URL}?query={container_name="scripts-traction-agent-1"} |= \`${tenantId}\``
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
  server.on("upgrade", (req, socket, head) => {
    socket.on("error", (err) => {
      // Socket pre-error
      console.error(`Socket error: ${err}`);
    });

    // TODO: Perform token auth here

    wss.handleUpgrade(req, socket, head, (ws) => {
      socket.removeListener("error", (err) => {
        // Socket post-error
        console.error(`Socket error: ${err}`);
      });

      wss.emit("connection", ws, req);
    });
  });

  wss.on("connection", (ws, req) => {
    // TODO: The Tenant ID should be extracted from the token
    // const tenantId = req.headers["x-tenant-id"] as string;
    const tenantId = "innkeeper";
    const loki = handleLokiWebSocket(tenantId, ws);
    handleTenantWebSocket(tenantId, ws, loki);
  });
};
