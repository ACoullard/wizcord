# Voice Chat — Design Plan

Status: design agreed, not yet implemented. This document describes the intended
shape only. Concrete API design, data structures, and library usage are left to
the implementation stage.

## Goal

Real-time group voice channels alongside the existing text channels, built to
handle a meaningful number of concurrent participants per node rather than a
handful.

## Why the media plane lives outside the current deployment

Production runs on a low-powered home server reached only through a Cloudflare
Tunnel (see `DEPLOYMENT.md`). That tunnel carries HTTP/HTTPS and WebSockets
only — no public UDP — and there is no port forwarding or public IP. WebRTC
media therefore cannot terminate on the production host under any configuration.

The media plane runs on AWS EC2 instead. The existing host keeps the control
plane: signaling, auth, room state, MongoDB, and Redis.

## Architecture

Two planes with a hard boundary between them.

**Control plane** — the existing Flask app.
Owns authentication, channel permissions, room membership, media server
discovery, and media server lifecycle. Communicates with clients over the
existing HTTPS + SSE transport, and with media servers over an authenticated
HTTP API.

**Media plane** — a Selective Forwarding Unit (SFU) on EC2.
Terminates ICE/DTLS/SRTP per participant and forwards Opus RTP between them
without decoding it. Holds no persistent state and no database access.

An SFU is used rather than peer-to-peer mesh (does not scale past a few
participants) or server-side mixing (far higher CPU cost, adds latency, and
removes per-user volume control and spatial audio).

### Signaling transport

Signaling reuses what the app already has: HTTP POST for client-to-server, and
the existing SSE + Redis pub/sub for server-to-client. No WebSocket layer is
needed — the SFU produces its answer synchronously, and asynchronous events fit
the SSE model already used for messages and member joins.

Media traffic goes directly from client to SFU over UDP and never passes through
the control plane. No TLS certificate is required for the media server; WebRTC
authenticates it via a fingerprint carried in the signaling payload, which
already travels over trusted HTTPS.

## AWS services

Media servers run as plain EC2 instances managed by an Auto Scaling Group with a
warm pool, using compute-optimized ARM instances rather than burstable ones —
forwarding audio is a sustained packet-processing workload, and burstable
instances throttle to a low baseline once credits are exhausted, degrading calls
the longer they run. Instances sit in a public subnet with auto-assigned public
addresses, since a media server needs a directly reachable address for ICE and
the addresses are already treated as ephemeral. Container images are stored in
ECR, capacity and health metrics go to CloudWatch where they drive scaling
decisions, and the whole media plane should be defined as infrastructure as code
so it can be torn down and recreated cheaply. Load-testing fleets use spot
capacity, kept in the same availability zone as the media server so test traffic
does not incur internet egress charges.

Two AWS pricing traps are avoided by design and should stay avoided: NAT
gateways, which bill continuously and are unnecessary once instances are in a
public subnet, and Elastic IPs, which bill whether or not they are attached and
are unnecessary given instances self-register their address on boot. Managed
alternatives — Lightsail, Fargate, and the managed WebRTC service — were
considered and rejected: they either constrain the deployment model or take
ownership of the forwarding behaviour this project intends to control.

## Media server lifecycle

Voice channels are idle most of the time, so media servers are not run
continuously.

1. **Pre-warm** — an authenticated user arriving in the app triggers a warm
   media server, subject to a cooldown so ordinary traffic cannot cause repeated
   launches.
2. **Join** — the control plane resolves an available media server for the
   channel, or starts one, then brokers the WebRTC handshake between client and
   server.
3. **Registration** — a media server reports its address and capacity to the
   control plane on boot. Addresses are ephemeral and must not be assumed stable
   across restarts.
4. **Scale down** — when the last participant leaves, a grace period runs before
   the instance is released, so brief disconnects and rejoins do not cause churn.

A warm pool keeps startup latency low enough that the first join is not
disruptive. Launch decisions must be guarded against concurrent joins starting
duplicate instances.

## SFU implementation

Built directly on a WebRTC protocol library rather than adopting a finished
media server, so that forwarding behaviour — in particular which speakers are
forwarded to whom — is owned by this project and can be tuned.

Audio-only removes most of what makes an SFU large: no simulcast, no layered
encoding, no keyframe handling, no video negotiation, no bandwidth-estimation
driven adaptation. What remains is session management, RTP forwarding, and
speaker selection.

Core responsibilities:

- Accept peer connections and negotiate Opus
- Track room membership and per-participant subscriptions
- Forward RTP between participants, preserving stream continuity for receivers
- Rank speakers by signalled audio level and forward only the most active ones,
  so per-room load grows linearly rather than quadratically with participants
- Report capacity and health to the control plane

An off-the-shelf SFU should be stood up alongside it as a reference: it provides
a correctness baseline when audio sounds subtly wrong, a comparison point for
capacity measurements, and a fallback if the custom server stalls.

## Prerequisites

A read-through of the current code surfaced work that must happen first or
alongside:

- **Streams per user.** Each open SSE stream holds a dedicated Redis pub/sub
  connection, so the ceiling is set by whichever runs out first: gevent
  connections per worker, or Redis connections in the pool. A voice channel
  adding a third stream per user divides the reachable user count accordingly.
  Either multiplex voice events onto an existing stream or budget for the extra
  connection deliberately.
- **Reconnect behaviour.** SSE streams are deliberately short-lived and the
  frontend refetches on reopen. A voice session must survive its signaling
  stream being cut and replaced mid-call, so call state cannot be tied to the
  identity or lifetime of an SSE connection. Any voice stream added needs the
  same jittered expiry the existing streams use; an unjittered cap
  resynchronises every client onto a single expiry moment.
- **Proxy configuration.** SSE requires response buffering to be disabled. The
  repo's nginx config covers development only; in production this depends on the
  external reverse proxy and the Cloudflare Tunnel, neither of which is version
  controlled. Verify before relying on it — including that the tunnel's idle
  timeout is longer than the heartbeat interval.
- **Channel types.** Channels currently have no type field, and the frontend
  resolves channel selection by name. Both need to change to distinguish voice
  channels from text channels.
- **Test fakes.** AWS calls need a fake installed the way the Redis and MongoDB
  fakes are: session-wide in `conftest.py`, before any app code imports, not per
  module.
- **Credentials.** The control plane host is not on AWS and has no instance role,
  so it needs scoped long-lived credentials permitting only tagged instance
  lifecycle operations.
- **Local development.** There is currently no way to run a media server locally;
  the development compose stack needs one.

## Capacity validation

Capacity should be measured, not assumed. The intended approach is a fleet of
headless synthetic clients publishing real audio against a media server, scaled
up until a limit is found, with the constraint identified explicitly.

Audio is a packets-per-second workload rather than a bandwidth one — small
payloads at a fixed frame rate — so the expected limits are CPU and packet rate,
not link capacity. Cloud instances enforce packet-rate quotas separately from
bandwidth and shed packets silently when exceeded, which is indistinguishable
from network loss unless specifically monitored. Any capacity measurement must
account for this or it will measure the host, not the software.

## Out of scope

Video, screen sharing, recording, PSTN interop, and multi-region deployment.
End-to-end encrypted media is a plausible later extension — the SFU only needs
packet headers, not payloads — but is not part of this work.

## Open questions

- Whether one media server hosts a single channel or many, which determines the
  capacity model and how scaling decisions are made.
- Where the pre-warm trigger lives, given the auth context currently mounts on
  every page including public ones.
- How long to allow for the custom SFU before falling back to the reference
  implementation.
- Quality-versus-cost settings — codec bitrate, redundancy under packet loss,
  and receiver buffering depth — which trade audio quality against bandwidth and
  latency. These should be decided with measurements in hand rather than up front.
