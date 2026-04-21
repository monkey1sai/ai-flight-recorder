use crate::spool::SpoolRecord;

#[derive(Clone, Debug)]
pub struct OtlpExporter {
    endpoint: String,
    service_name: String,
}

impl OtlpExporter {
    pub fn new(endpoint: String, service_name: String) -> Self {
        Self {
            endpoint,
            service_name,
        }
    }

    pub fn endpoint(&self) -> &str {
        &self.endpoint
    }

    pub fn preview_payload(&self, records: &[SpoolRecord]) -> String {
        let preview = records
            .first()
            .map(|record| {
                format!(
                    "first_trace={} action={} blob={}",
                    record.trace_id, record.policy_action, record.blob_ref
                )
            })
            .unwrap_or_else(|| "first_trace=none".to_string());
        format!(
            "service={} endpoint={} records={} {}",
            self.service_name,
            self.endpoint,
            records.len(),
            preview
        )
    }
}
