use std::{env, path::PathBuf};

#[derive(Clone, Debug)]
pub struct EdgeConfig {
    pub service_name: String,
    pub otlp_endpoint: String,
    pub spool_dir: PathBuf,
    pub blob_dir: PathBuf,
    pub heartbeat_seconds: u64,
}

impl EdgeConfig {
    pub fn from_env() -> Self {
        Self {
            service_name: env::var("AERIS_EDGE_SERVICE")
                .unwrap_or_else(|_| "aeris-edge-daemon".to_string()),
            otlp_endpoint: env::var("AERIS_OTLP_ENDPOINT")
                .unwrap_or_else(|_| "http://otel-collector:4318/v1/traces".to_string()),
            spool_dir: env::var("AERIS_SPOOL_DIR")
                .map(PathBuf::from)
                .unwrap_or_else(|_| PathBuf::from("./var/spool")),
            blob_dir: env::var("AERIS_BLOB_DIR")
                .map(PathBuf::from)
                .unwrap_or_else(|_| PathBuf::from("./var/blob")),
            heartbeat_seconds: env::var("AERIS_EDGE_HEARTBEAT_SECONDS")
                .ok()
                .and_then(|value| value.parse().ok())
                .unwrap_or(30),
        }
    }
}
