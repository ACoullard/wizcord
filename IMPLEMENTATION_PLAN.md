# Voice Chat — Implementation Decisions

Decisions made while working through `PLAN.md`. Open items stay in `PLAN.md`
until they are settled here.

## SFU library: Pion (Go)

The media server is built on Pion. It is the most mature of the candidate
protocol libraries, and the off-the-shelf reference server named in `PLAN.md`
will be LiveKit, which is built on the same stack — so capacity comparisons are
same-stack and the reference's forwarding path is directly readable when ours
misbehaves.

Rejected: `webrtc-rs` (lags Pion without compensating strengths), `str0m`
(sound design, but a smaller community and more plumbing to write), `aiortc`
(keeps the repo single-language, but per-packet work in asyncio Python caps
capacity far below the goal).

## NAT traversal: host candidates only, for now

No TURN and no ICE-TCP fallback in the first implementation. Clients that cannot
reach the media server over UDP will fail to connect. Published figures put that
at roughly one session in six, concentrated in networks that block outbound UDP.

This is deferred, not dismissed. The signaling payload and session bookkeeping
should not assume a single candidate type, and the candidate type each session
selects should be recorded, so the fallback decision is made against measurements
rather than re-argued from first principles.

No STUN server is required: the media server advertises its own public address as
a host candidate and learns each client's mapped address from the inbound ICE
binding request. An EC2 NIC only sees its private address, so the server must read
its public address from IMDS at boot and advertise it explicitly.

## Control API: the media server opens every connection

All communication between the control plane and a media server travels over
connections the media server itself opens outbound to the app's public hostname.
The control plane never dials a media server. It opens nothing but its own calls
to the AWS API for instance lifecycle.

This costs one extra network leg on join, since a request that could have gone
straight from the home server to an EC2 public address instead goes out through
Cloudflare and back. In exchange:

- TLS is free and already terminated at Cloudflare. There is no certificate to
  issue, distribute, or renew on an ephemeral instance, and no plaintext control
  endpoint whose payload — which carries the DTLS fingerprint — would have to be
  signed and encrypted at the application layer to be safe.
- The media plane needs no inbound rule beyond the media ports. Because the
  control plane's egress address is residential and dynamic, a security group
  guarding a control endpoint could not be scoped to it and would have to be open
  to the internet.
- Ephemeral addresses stop being a problem to solve. Nothing needs to reach a
  media server at a known address, so an address that changes on every launch
  costs nothing.
- The fanout already exists. Routing work to a media server is the same Redis
  pub/sub-to-streaming-response pattern the client SSE streams already use, which
  is also what keeps it correct across multiple gunicorn workers.

Rejected: a direct control-plane-to-media-server endpoint. It is viable — a
self-signed certificate whose fingerprint is reported during registration and
pinned thereafter gives it real TLS without a CA or DNS — but it buys only join
latency, and pays for it with a certificate lifecycle and an internet-facing
endpoint on every media host.

### Two channels

On boot a media server registers, then opens a second long-lived request that the
control plane holds open and writes commands into. Commands flow down that stream;
everything originating at the media server goes up as an ordinary POST.

Down the stream, control plane to media server:

| Command | Purpose |
|---|---|
| `join` | A client's offer, with room, participant, and correlation ids. The answer comes back as a POST, not on this stream. |
| `leave` | Immediate teardown for a participant. ICE timeout eventually notices a departure, but far too slowly to free a slot, and not at all for a kick or a revoked permission, where the cut must not wait on a healthy connection. |
| `ice-restart` | A client changed networks and needs a new offer applied to an existing session. |
| `drain` | Stop accepting joins ahead of release, so a join racing the scale-down decision does not land on an instance about to terminate. |
| `close-room` | Tear down every participant at once. |
| `config` | Speaker-selection width, bitrate. Deferred; boot-time configuration is sufficient until these are being tuned against measurements. |

Up as POSTs, media server to control plane: registration, heartbeat and capacity,
answers to `join`, and session events — `participant-connected`,
`participant-disconnected`, `ice-failed`, `room-empty` — which are republished to
clients over their existing SSE streams. `room-empty` is what starts the
scale-down grace period; the media server is the only component that knows the
last participant actually left.

`join` and `leave` down, and registration, heartbeat, answers, and `room-empty`
up, are enough for a first working version.

### Topology

```
  +----------------------+    media: SRTP/UDP     +--------------------------+
  |    Browser client    |<======================>|    Media server (EC2)    |
  |                      |   direct - never       |   Pion SFU, public IP    |
  +----------------------+   through the tunnel   +--------------------------+
        |           ^                                  |              ^
        | join      | SSE                     register |              | commands:
        | (offer)   | client                 heartbeat |              | join, leave,
        |           | events                    answer |              | drain, ...
        v           |                           events v              |
  +-----------------------------------------------------------------------+
  |                    Cloudflare Tunnel - HTTPS only                     |
  +-----------------------------------------------------------------------+
                            |            ^
                            v            |
            +-------------------------------------------+
            |        Control plane - home server        |
            |      Flask (gevent), Redis, MongoDB       |
            |       no inbound ports, no public IP      |
            +-------------------------------------------+
                            |
                            | outbound HTTPS - instance lifecycle
                            v
                    +-------------------+
                    |      AWS API      |
                    +-------------------+
```

Arrows show data flow, not who dialled. Every connection here is opened by the
browser or by the media server; the `commands` arrow carries data down a
connection the media server opened itself.

### Join

```
  Client          Control plane          Redis          Media server
    |                   |                  |                  |
    |  POST join        |                  |                  |
    |  (SDP offer)      |                  |                  |
    |------------------>|                  |                  |
    |                   | publish job      |                  |
    |                   |----------------->|                  |
    |                   |                  | job down stream  |
    |                   |                  |----------------->|
    |                   |                  |                  |
    |                   | subscribe        |                  | negotiate,
    |                   | join:<corr-id>   |                  | build peer
    |                   | (greenlet parks) |                  | connection
    |                   |                  |                  |
    |                   |     POST answer  |                  |
    |                   |<-----------------+------------------|
    |                   | publish answer   |                  |
    |                   |----------------->|                  |
    |                   |<-----------------|                  |
    |  200 + SDP answer |                  |                  |
    |<------------------|                  |                  |
    |                   |                  |                  |
    |         ICE / DTLS / SRTP - direct to the media server  |
    |<=======================================================>|
```

The client's request is held open until the answer arrives, preserving the
synchronous handshake `PLAN.md` describes. Under gevent a parked greenlet is
nearly free. The answer may be POSTed to a different worker than the one holding
the client's request, which is why it is routed back through pub/sub rather than
returned in place. The wait needs a timeout and a failure path for a media server
that never answers.

### Failure behaviour

Because media never transits the control plane, control-plane failures do not drop
calls. Restarting the app drops every work-stream and every media server
reconnects, while in-progress calls keep flowing. A dropped stream means the media
server takes no new joins until it reconnects, not that its current sessions die.

The work-stream needs keepalives shorter than the Cloudflare Tunnel idle timeout,
and reconnects need backoff. It does not need the jittered expiry the client
streams use: there are few enough of these that synchronised reconnects are not a
concern.

If join latency through the doubled path measures badly, the retreat is to move
`join` alone to a direct call and leave everything else on the stream. That
reintroduces the inbound endpoint and its certificate, so it should follow
measurements rather than precede them.
