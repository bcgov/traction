# Traction WebVH Deployment

## Overview
Traction uses an ACA-Py agent with Traction-specific plugins to publish and resolve decentralized identifiers. When the `webvh` plugin is enabled, the agent integrates with a Web Verified History (WebVH) service so that DID documents are written to, and read from, a tamper-evident log. The diagram below captures the components involved in a typical deployment and how they communicate.

## Component Diagram
```mermaid
flowchart LR
    User[Issuer / Verifier Admin] --> UIFrontend["Tenant UI Frontend"]
    UIFrontend --> TenantProxy["Tenant Proxy"]
    TenantProxy --> ACApy["Traction ACA-Py Agent"]

    subgraph Traction["Traction Platform"]
        UIFrontend
        TenantProxy
        ACApy
    end

    subgraph WitnessService["Witness Service"]
        EndorserAPI["Endorser API"]
        WitnessAgent["Witness Agent"]
    end

    subgraph WebVH["WebVH Server"]
        WebVHService["WebVH API"]
    end

    subgraph WatcherLayer["Watcher Service"]
        Watcher["Watcher Worker"]
    end

    EndorserAPI --> WitnessAgent
    WitnessAgent -. webhooks .-> EndorserAPI
    WitnessAgent -. "DIDComm connection" .- ACApy
    ACApy --> WebVHService
    ACApy --> Watcher
    Watcher --> WebVHService
```

## Interaction Highlights
- Tenant administrators work in the Tenant UI, which forwards administrative API calls through the Tenant Proxy to the Traction ACA-Py agent.
- ACA-Py coordinates WebVH DID operations using the `webvh` plugin. When a DID update is prepared, ACA-Py waits for the Witness Service to supply co-signatures via their existing DIDComm connection.
- Witness operators (or automated jobs) interact with the Endorser API to trigger the Witness Agent. The Witness Agent posts webhook callbacks to the Endorser API and shares signed payload details with ACA-Py over the DIDComm channel.
- After collecting the necessary witness signatures, only the Traction ACA-Py agent submits the finalized payload to the WebVH server; there is no callback path from WebVH back to Traction.
- The Witness Agent maintains a DIDComm connection with the Traction ACA-Py agent, allowing event notifications and co-signing responses to flow asynchronously.
- WebVH anchoring details surface to the Tenant UI via the data that ACA-Py aggregates from witness signatures and submission results; WebVH itself does not call back into Traction.

## Sequence Diagram
```mermaid
sequenceDiagram
    participant User
    participant UI as Tenant UI
    participant Proxy as Tenant Proxy
    participant Agent as Traction ACA-Py Agent
    participant Witness as Witness Agent
    participant WebVH as WebVH Server

    User->>UI: Create new reservation
    UI->>Proxy: Forward reservation
    Proxy->>Proxy: Approve reservation
    Proxy->>Agent: Create tenant

    User->>UI: Connect to Witness service
    UI->>Proxy: Request DIDComm invite
    Proxy->>Agent: Fetch witness invitation
    Agent-->>Proxy: Invitation url
    Proxy-->>UI: Forward invitation URL
    UI->>Proxy: Configure WebVH Plugin with witness invitation
    Proxy->>Agent: Forward configuration
    Agent-->>Witness: Send connection response
    Agent-->>Proxy: Connection active
    Proxy-->>UI: Witness service connected

    User->>UI: Create new DID
    UI->>Proxy: Submit DID request
    Proxy->>Agent: Forward DID request
    Agent->>WebVH: Request current DID state
    WebVH-->>Agent: DID not found (initial entry)
    Agent->>Agent: Create initial log entry

    Agent->>Witness: Request witness signature
    Witness-->>Agent: Return signed payload

    Agent->>WebVH: Submit witnessed initial log entry
    WebVH-->>Agent: Acknowledge write
    Agent-->>Proxy: Report DID anchored
    Proxy-->>UI: Present DID status
```
