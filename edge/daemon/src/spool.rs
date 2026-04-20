use std::{collections::VecDeque, path::PathBuf};

use crate::{blob::BlobReference, policy::PolicyDecision};

#[derive(Clone, Debug)]
pub struct SpoolRecord {
    pub trace_id: String,
    pub policy_action: String,
    pub blob_ref: String,
}

pub struct Spool {
    pub root_dir: PathBuf,
    queue: VecDeque<SpoolRecord>,
}

impl Spool {
    pub fn new(root_dir: PathBuf) -> Self {
        Self {
            root_dir,
            queue: VecDeque::new(),
        }
    }

    pub fn enqueue(&mut self, trace_id: &str, decision: &PolicyDecision, blob: &BlobReference) {
        self.queue.push_back(SpoolRecord {
            trace_id: trace_id.to_string(),
            policy_action: decision.action.clone(),
            blob_ref: blob.storage_ref.clone(),
        });
    }

    pub fn len(&self) -> usize {
        self.queue.len()
    }

    pub fn drain_snapshot(&self) -> Vec<SpoolRecord> {
        self.queue.iter().cloned().collect()
    }
}
