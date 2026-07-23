import http from "http";
import { URL } from "url";
import { WhatsAppMessageEnvelope } from "../contracts";

export interface DeliveryResult {
  isSuccess: boolean;
  isPermanentFailure: boolean;
  statusCode?: number;
  reasonCode: string;
  errorMessage?: string;
  responseBody?: any;
}

export class TradingServiceDeliveryClient {
  constructor(
    private tradingServiceUrl: string = "http://127.0.0.1:8000",
    private localApiToken: string = "dev-local-secret-token",
    private deliveryTimeoutMs: number = 10000
  ) {}

  async deliverEnvelope(envelope: WhatsAppMessageEnvelope): Promise<DeliveryResult> {
    const targetUrl = new URL("/api/v1/parser/messages", this.tradingServiceUrl);

    // Map worker envelope to parser endpoint input payload
    const payload = {
      messageId: envelope.whatsapp_message_id,
      groupId: envelope.group_id,
      senderId: envelope.sender_id,
      text: envelope.text,
      quotedMessageId: envelope.quoted_whatsapp_message_id,
      isReply: envelope.is_reply
    };

    const bodyData = JSON.stringify(payload);

    return new Promise((resolve) => {
      const req = http.request(
        targetUrl,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${this.localApiToken}`,
            "X-Worker-Id": envelope.worker_id,
            "X-Correlation-Id": envelope.correlation_id,
            "X-Idempotency-Key": envelope.whatsapp_message_id
          },
          timeout: this.deliveryTimeoutMs
        },
        (res) => {
          let resData = "";
          res.on("data", chunk => { resData += chunk; });
          res.on("end", () => {
            const status = res.statusCode || 500;
            let parsedBody: any = null;
            try { parsedBody = JSON.parse(resData); } catch {}

            if (status === 200 || status === 201) {
              resolve({
                isSuccess: true,
                isPermanentFailure: false,
                statusCode: status,
                reasonCode: "DELIVERED",
                responseBody: parsedBody
              });
            } else if (status === 401 || status === 403) {
              resolve({
                isSuccess: false,
                isPermanentFailure: true,
                statusCode: status,
                reasonCode: "TRADING_SERVICE_AUTH_FAILED",
                errorMessage: `Authentication failed on trading service (HTTP ${status}).`
              });
            } else if (status === 422 || status === 400) {
              resolve({
                isSuccess: false,
                isPermanentFailure: true,
                statusCode: status,
                reasonCode: "TRADING_SERVICE_VALIDATION_FAILED",
                errorMessage: `Validation failed on trading service (HTTP ${status}).`
              });
            } else {
              resolve({
                isSuccess: false,
                isPermanentFailure: false,
                statusCode: status,
                reasonCode: "TRADING_SERVICE_TRANSIENT_ERROR",
                errorMessage: `Trading service returned error status HTTP ${status}.`
              });
            }
          });
        }
      );

      req.on("error", (err) => {
        resolve({
          isSuccess: false,
          isPermanentFailure: false,
          reasonCode: "TRADING_SERVICE_UNREACHABLE",
          errorMessage: `Network error delivering to trading service: ${err.message}`
        });
      });

      req.on("timeout", () => {
        req.destroy();
        resolve({
          isSuccess: false,
          isPermanentFailure: false,
          reasonCode: "DELIVERY_TIMEOUT",
          errorMessage: "Timeout delivering message to trading service."
        });
      });

      req.write(bodyData);
      req.end();
    });
  }
}
