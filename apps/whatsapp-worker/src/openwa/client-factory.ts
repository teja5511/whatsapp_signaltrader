import { OpenWAAdapterInterface } from "./adapter";
import { FakeOpenWAAdapter } from "./fake-adapter";
import { RealOpenWAAdapter } from "./real-adapter";
import { MODE_REAL } from "../constants";

export function createOpenWAAdapter(
  mode: string = "fake",
  sessionName: string = "xauusd-bot",
  sessionDir?: string,
  qrCallback?: (qrPayload: string) => void
): OpenWAAdapterInterface {
  if (mode === MODE_REAL) {
    return new RealOpenWAAdapter(sessionName, sessionDir, qrCallback);
  }
  return new FakeOpenWAAdapter();
}
