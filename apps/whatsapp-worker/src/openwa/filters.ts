export interface FilterInputMessage {
  id: string;
  groupId: string;
  senderId: string;
  senderIsAdmin: boolean;
  fromMe: boolean;
  type: string;
  body?: string;
  caption?: string;
  isStatus: boolean;
  isReaction: boolean;
  isEdit: boolean;
  isDeletion: boolean;
  isSystem: boolean;
}

export interface FilterResult {
  isAccepted: boolean;
  rejectReason?: string;
  extractedText?: string;
  messageType?: "TEXT" | "CAPTION";
}

export function filterIncomingMessage(
  msg: FilterInputMessage,
  approvedGroupId: string | null,
  approvedAdminId: string | null,
  requireAdminRole: boolean = true,
  selfAccountId: string | null = null
): FilterResult {
  if (!approvedGroupId) {
    return { isAccepted: false, rejectReason: "APPROVED_GROUP_NOT_CONFIGURED" };
  }

  if (!approvedAdminId) {
    return { isAccepted: false, rejectReason: "APPROVED_ADMIN_NOT_CONFIGURED" };
  }

  if (msg.groupId !== approvedGroupId) {
    return { isAccepted: false, rejectReason: "NOT_APPROVED_GROUP" };
  }

  if (msg.senderId !== approvedAdminId) {
    return { isAccepted: false, rejectReason: "NOT_APPROVED_ADMIN" };
  }

  if (requireAdminRole && !msg.senderIsAdmin) {
    return { isAccepted: false, rejectReason: "SENDER_NOT_ADMIN_ROLE" };
  }

  if (msg.fromMe || (selfAccountId && msg.senderId === selfAccountId)) {
    return { isAccepted: false, rejectReason: "SELF_MESSAGE_IGNORED" };
  }

  if (msg.isStatus) {
    return { isAccepted: false, rejectReason: "STATUS_UPDATE_IGNORED" };
  }

  if (msg.isReaction) {
    return { isAccepted: false, rejectReason: "REACTION_IGNORED" };
  }

  if (msg.isEdit) {
    return { isAccepted: false, rejectReason: "EDIT_EVENT_IGNORED" };
  }

  if (msg.isDeletion) {
    return { isAccepted: false, rejectReason: "DELETION_EVENT_IGNORED" };
  }

  if (msg.isSystem) {
    return { isAccepted: false, rejectReason: "SYSTEM_NOTIFICATION_IGNORED" };
  }

  // Extract text body
  let text = msg.body;
  let msgType: "TEXT" | "CAPTION" = "TEXT";

  if (!text || text.trim().length === 0) {
    if (msg.caption && msg.caption.trim().length > 0) {
      text = msg.caption;
      msgType = "CAPTION";
    } else {
      return { isAccepted: false, rejectReason: "UNSUPPORTED_MEDIA_WITHOUT_TEXT" };
    }
  }

  // Normalize text line endings & outer trim
  const normalizedText = text.replace(/\r\n/g, "\n").trim();

  if (normalizedText.length > 10000) {
    return { isAccepted: false, rejectReason: "MESSAGE_TEXT_TOO_LARGE" };
  }

  return {
    isAccepted: true,
    extractedText: normalizedText,
    messageType: msgType
  };
}
