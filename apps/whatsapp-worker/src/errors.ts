export class WhatsAppWorkerError extends Error {
  constructor(message: string, public readonly code: string = "WORKER_ERROR") {
    super(message);
    this.name = "WhatsAppWorkerError";
  }
}

export class SessionAlreadyInUseError extends WhatsAppWorkerError {
  constructor(message: string = "WhatsApp session lock is already owned by another active worker process.") {
    super(message, "WHATSAPP_SESSION_ALREADY_IN_USE");
    this.name = "SessionAlreadyInUseError";
  }
}

export class UnauthorizedLocalApiError extends WhatsAppWorkerError {
  constructor(message: string = "Unauthorized local API token.") {
    super(message, "UNAUTHORIZED_LOCAL_API");
    this.name = "UnauthorizedLocalApiError";
  }
}

export class InvalidResetConfirmationError extends WhatsAppWorkerError {
  constructor(message: string = "Invalid session reset confirmation phrase.") {
    super(message, "INVALID_RESET_CONFIRMATION");
    this.name = "InvalidResetConfirmationError";
  }
}

export class GroupNotConfiguredError extends WhatsAppWorkerError {
  constructor(message: string = "Approved group ID is not configured.") {
    super(message, "APPROVED_GROUP_NOT_CONFIGURED");
    this.name = "GroupNotConfiguredError";
  }
}

export class AdminNotConfiguredError extends WhatsAppWorkerError {
  constructor(message: string = "Approved admin ID is not configured.") {
    super(message, "APPROVED_ADMIN_NOT_CONFIGURED");
    this.name = "AdminNotConfiguredError";
  }
}
