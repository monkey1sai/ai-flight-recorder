FROM rust:1.92-slim AS builder

WORKDIR /workspace
COPY edge/daemon ./edge/daemon
RUN cargo build --manifest-path edge/daemon/Cargo.toml --release

FROM debian:bookworm-slim

WORKDIR /srv
COPY --from=builder /workspace/edge/daemon/target/release/aeris-edge-daemon /usr/local/bin/aeris-edge-daemon

CMD ["/usr/local/bin/aeris-edge-daemon"]
