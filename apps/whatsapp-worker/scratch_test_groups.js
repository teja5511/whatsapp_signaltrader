const baileys = require("@whiskeysockets/baileys");
const path = require("path");

async function checkGroups() {
  const authPath = "./data/sessions/xauusd-bot_baileys";
  const { useMultiFileAuthState, fetchLatestBaileysVersion } = baileys;
  const { state } = await useMultiFileAuthState(authPath);
  const { version } = await fetchLatestBaileysVersion().catch(() => ({ version: [2, 3000, 1015901307] }));
  const logger = require("pino")({ level: "silent" });

  const makeWASocket = baileys.default || baileys.makeWASocket || baileys;
  const sock = makeWASocket({
    version,
    auth: state,
    printQRInTerminal: false,
    logger,
    browser: ["WhatsApp Trade Bot", "Chrome", "132.0.0.0"]
  });

  sock.ev.on("connection.update", async (update) => {
    const { connection } = update;
    if (connection === "open") {
      console.log("Connected to WhatsApp! Fetching participating groups...");
      try {
        const groups = await sock.groupFetchAllParticipating();
        console.log("groupFetchAllParticipating result keys:", Object.keys(groups));
        for (const [id, g] of Object.entries(groups)) {
          console.log(`- Group: "${g.subject || g.name}" | JID: ${id}`);
        }
      } catch (err) {
        console.error("Error fetching groups:", err);
      }
      setTimeout(() => process.exit(0), 1000);
    }
  });
}

checkGroups();
