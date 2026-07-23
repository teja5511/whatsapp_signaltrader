import test from "node:test";
import assert from "node:assert/strict";
import { filterIncomingMessage } from "../src/openwa/filters";

test("filterIncomingMessage should accept valid approved admin group message", () => {
  const input = {
    id: "wamid-123",
    groupId: "group-xauusd-vip",
    senderId: "admin-master-1",
    senderIsAdmin: true,
    fromMe: false,
    type: "chat",
    body: "Gold Sell\n3990-3998\nsl - 4008\ntp - 3960",
    isStatus: false,
    isReaction: false,
    isEdit: false,
    isDeletion: false,
    isSystem: false
  };

  const res = filterIncomingMessage(input, "group-xauusd-vip", "admin-master-1", true);
  assert.equal(res.isAccepted, true);
  assert.equal(res.extractedText, "Gold Sell\n3990-3998\nsl - 4008\ntp - 3960");
  assert.equal(res.messageType, "TEXT");
});

test("filterIncomingMessage should reject non-approved group message", () => {
  const input = {
    id: "wamid-124",
    groupId: "group-other",
    senderId: "admin-master-1",
    senderIsAdmin: true,
    fromMe: false,
    type: "chat",
    body: "Gold Sell",
    isStatus: false,
    isReaction: false,
    isEdit: false,
    isDeletion: false,
    isSystem: false
  };

  const res = filterIncomingMessage(input, "group-xauusd-vip", "admin-master-1", true);
  assert.equal(res.isAccepted, false);
  assert.equal(res.rejectReason, "NOT_APPROVED_GROUP");
});

test("filterIncomingMessage should reject non-admin sender message", () => {
  const input = {
    id: "wamid-125",
    groupId: "group-xauusd-vip",
    senderId: "user-regular",
    senderIsAdmin: false,
    fromMe: false,
    type: "chat",
    body: "Gold Sell",
    isStatus: false,
    isReaction: false,
    isEdit: false,
    isDeletion: false,
    isSystem: false
  };

  const res = filterIncomingMessage(input, "group-xauusd-vip", "admin-master-1", true);
  assert.equal(res.isAccepted, false);
  assert.equal(res.rejectReason, "NOT_APPROVED_ADMIN");
});

test("filterIncomingMessage should reject status updates and reaction events", () => {
  const inputReaction = {
    id: "wamid-126",
    groupId: "group-xauusd-vip",
    senderId: "admin-master-1",
    senderIsAdmin: true,
    fromMe: false,
    type: "reaction",
    body: "👍",
    isStatus: false,
    isReaction: true,
    isEdit: false,
    isDeletion: false,
    isSystem: false
  };

  const res = filterIncomingMessage(inputReaction, "group-xauusd-vip", "admin-master-1", true);
  assert.equal(res.isAccepted, false);
  assert.equal(res.rejectReason, "REACTION_IGNORED");
});

test("filterIncomingMessage should reject oversized message text > 10,000 chars", () => {
  const hugeText = "A".repeat(10001);
  const inputHuge = {
    id: "wamid-127",
    groupId: "group-xauusd-vip",
    senderId: "admin-master-1",
    senderIsAdmin: true,
    fromMe: false,
    type: "chat",
    body: hugeText,
    isStatus: false,
    isReaction: false,
    isEdit: false,
    isDeletion: false,
    isSystem: false
  };

  const res = filterIncomingMessage(inputHuge, "group-xauusd-vip", "admin-master-1", true);
  assert.equal(res.isAccepted, false);
  assert.equal(res.rejectReason, "MESSAGE_TEXT_TOO_LARGE");
});
