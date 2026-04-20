#[derive(Clone, Debug)]
pub struct EdgeEvent {
    pub trace_id: String,
    pub step_type: String,
    pub payload: String,
}

impl EdgeEvent {
    pub fn sample() -> Self {
        Self {
            trace_id: "22222222-2222-4222-8222-222222222222".to_string(),
            step_type: "response_synthesis".to_string(),
            payload: "production remediation guidance".to_string(),
        }
    }
}

#[derive(Clone, Debug)]
pub struct PolicyDecision {
    pub action: String,
    pub reason: String,
}

#[derive(Default)]
pub struct PolicyEngine;

impl PolicyEngine {
    pub fn evaluate(&self, event: &EdgeEvent) -> PolicyDecision {
        if event.payload.contains("production") {
            PolicyDecision {
                action: "flag".to_string(),
                reason: "payload references production changes".to_string(),
            }
        } else {
            PolicyDecision {
                action: "allow".to_string(),
                reason: "no elevated production signal".to_string(),
            }
        }
    }
}
