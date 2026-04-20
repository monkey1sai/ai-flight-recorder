use std::path::PathBuf;

#[derive(Clone, Debug)]
pub struct BlobReference {
    pub storage_ref: String,
}

pub struct BlobWriter {
    root_dir: PathBuf,
}

impl BlobWriter {
    pub fn new(root_dir: PathBuf) -> Self {
        Self { root_dir }
    }

    pub fn stage(&self, trace_id: &str, payload: &str) -> BlobReference {
        let filename = format!("{trace_id}-{}.txt", payload.len());
        let path = self.root_dir.join(filename);
        BlobReference {
            storage_ref: path.display().to_string(),
        }
    }
}
