import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync } from "node:fs";
import { join } from "node:path";

export default function (pi: ExtensionAPI) {
  // Load .env from repository root or current directory if present
  if (typeof process.loadEnvFile === "function") {
    for (const envPath of [join(process.cwd(), ".env"), join(process.cwd(), "..", ".env")]) {
      if (existsSync(envPath)) {
        try {
          process.loadEnvFile(envPath);
        } catch {}
      }
    }
  }

  const host = process.env.OLLAMA_HOST;
  const baseUrl11434 = process.env.OLLAMA_BASE_URL || (host ? `http://${host}:11434/v1` : undefined);
  const baseUrl11435 = process.env.OLLAMA_BASE_URL_11435 || (host ? `http://${host}:11435/v1` : undefined);

  if (baseUrl11434) {
    pi.registerProvider("ollama-11434", { baseUrl: baseUrl11434 });
  }
  if (baseUrl11435) {
    pi.registerProvider("ollama-11435", { baseUrl: baseUrl11435 });
  }
}
