use std::sync::RwLock;

pub struct SecureTokenStore {
    token: RwLock<Option<String>>,
}

impl SecureTokenStore {
    pub fn new() -> Self {
        Self {
            token: RwLock::new(None),
        }
    }

    pub fn set_token(&self, token: String) {
        if let Ok(mut lock) = self.token.write() {
            *lock = Some(token);
        }
    }

    pub fn exists(&self) -> bool {
        if let Ok(lock) = self.token.read() {
            lock.is_some()
        } else {
            false
        }
    }

    pub fn clear(&self) {
        if let Ok(mut lock) = self.token.write() {
            *lock = None;
        }
    }

    pub fn get_token(&self) -> Option<String> {
        if let Ok(lock) = self.token.read() {
            lock.clone()
        } else {
            None
        }
    }
}
