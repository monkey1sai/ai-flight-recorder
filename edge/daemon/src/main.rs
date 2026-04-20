mod blob;
mod config;
mod health;
mod otlp;
mod policy;
mod spool;

use blob::BlobWriter;
use config::EdgeConfig;
use health::HealthReporter;
use otlp::OtlpExporter;
use policy::{EdgeEvent, PolicyEngine};
use spool::Spool;

fn main() {
    let config = EdgeConfig::from_env();
    let exporter = OtlpExporter::new(config.otlp_endpoint.clone(), config.service_name.clone());
    let blob_writer = BlobWriter::new(config.blob_dir.clone());
    let mut spool = Spool::new(config.spool_dir.clone());
    let policy_engine = PolicyEngine::default();

    let event = EdgeEvent::sample();
    let decision = policy_engine.evaluate(&event);
    let blob_ref = blob_writer.stage(&event.trace_id, &event.payload);
    spool.enqueue(&event.trace_id, &decision, &blob_ref);

    let health = HealthReporter::snapshot(&config, &spool, &exporter);
    let export_preview = exporter.preview_payload(&spool.drain_snapshot());

    println!(
        "edge_daemon service={} step_type={} action={} reason={} spool_depth={} otlp={} spool_dir={} heartbeat={} preview={}",
        health.service_name,
        event.step_type,
        decision.action,
        decision.reason,
        health.spool_depth,
        health.otlp_endpoint,
        health.spool_dir,
        health.heartbeat_seconds,
        export_preview
    );
}
