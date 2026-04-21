use crate::{config::EdgeConfig, otlp::OtlpExporter, spool::Spool};

#[derive(Clone, Debug)]
pub struct HealthReport {
    pub service_name: String,
    pub spool_depth: usize,
    pub otlp_endpoint: String,
    pub spool_dir: String,
    pub heartbeat_seconds: u64,
}

pub struct HealthReporter;

impl HealthReporter {
    pub fn snapshot(config: &EdgeConfig, spool: &Spool, exporter: &OtlpExporter) -> HealthReport {
        HealthReport {
            service_name: config.service_name.clone(),
            spool_depth: spool.len(),
            otlp_endpoint: exporter.endpoint().to_string(),
            spool_dir: spool.root_dir.display().to_string(),
            heartbeat_seconds: config.heartbeat_seconds,
        }
    }
}
