const crypto = require("crypto");
const fs = require("fs");
const https = require("https");

const envPath = "C:\\Users\\Omen\\Desktop\\keeperhub-staging\\.env";
const outPath = "C:\\Users\\Omen\\Desktop\\Butler\\config\\wallets.json";
const examplePath = "C:\\Users\\Omen\\Desktop\\Butler\\config\\wallets.example.json";
const labels = [
  "guest-bob",
  "servebot-1",
  "servebot-2",
  "servebot-3",
  "vending",
  "operator",
  "manufacturer",
  "settler",
];

function readEnv(path) {
  const values = {};
  for (const line of fs.readFileSync(path, "utf8").split(/\r?\n/)) {
    const stripped = line.trim();
    if (!stripped || stripped.startsWith("#") || !stripped.includes("=")) continue;
    const idx = stripped.indexOf("=");
    values[stripped.slice(0, idx).trim()] = stripped.slice(idx + 1).trim().replace(/^"|"$/g, "");
  }
  return values;
}

function request(apiKey, method, path, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = https.request(
      {
        hostname: "api.circle.com",
        path,
        method,
        headers: {
          Authorization: `Bearer ${apiKey}`,
          Accept: "application/json",
          "User-Agent": "butler-check/1.0",
          ...(data
            ? { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) }
            : {}),
        },
      },
      (res) => {
        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const raw = Buffer.concat(chunks).toString("utf8");
          let parsed = {};
          try {
            parsed = raw ? JSON.parse(raw) : {};
          } catch {
            parsed = { message: "non-json" };
          }
          resolve({ status: res.statusCode, parsed });
        });
      }
    );
    req.on("error", reject);
    if (data) req.write(data);
    req.end();
  });
}

async function ciphertext(apiKey, secret) {
  const keyResponse = await request(apiKey, "GET", "/v1/w3s/config/entity/publicKey");
  const pem = keyResponse.parsed?.data?.publicKey;
  if (keyResponse.status !== 200 || !pem) {
    throw new Error(`publicKey HTTP ${keyResponse.status} ${keyResponse.parsed?.message || ""}`);
  }
  return crypto
    .publicEncrypt(
      { key: pem, padding: crypto.constants.RSA_PKCS1_OAEP_PADDING, oaepHash: "sha256" },
      Buffer.from(secret, "hex")
    )
    .toString("base64");
}

async function main() {
  const env = readEnv(envPath);
  const apiKey = env.CIRCLE_API_KEY || "";
  const secret = env.CIRCLE_ENTITY_SECRET || "";
  if (!apiKey || !/^[0-9a-fA-F]{64}$/.test(secret)) {
    console.log("blocked circle credentials");
    process.exit(2);
  }

  const sets = await request(apiKey, "GET", "/v1/w3s/walletSets?pageSize=10");
  if (sets.status !== 200) {
    console.log(`walletSets HTTP ${sets.status} ${sets.parsed?.message || ""}`);
    process.exit(2);
  }
  const existingSets = sets.parsed?.data?.walletSets || [];
  let walletSetId = existingSets.find((set) => set.name === "butler-hotel" || set.name === "butler-secret-check")?.id;
  if (!walletSetId && existingSets.length === 1) walletSetId = existingSets[0].id;
  if (!walletSetId) {
    const created = await request(apiKey, "POST", "/v1/w3s/developer/walletSets", {
      name: "butler-hotel",
      idempotencyKey: crypto.randomUUID(),
      entitySecretCiphertext: await ciphertext(apiKey, secret),
    });
    walletSetId = created.parsed?.data?.walletSet?.id;
    if (!walletSetId) {
      console.log(`create wallet set HTTP ${created.status} ${created.parsed?.message || ""}`);
      process.exit(2);
    }
    console.log("created wallet set");
  } else {
    console.log("reused wallet set", existingSets.length);
  }

  const listed = await request(apiKey, "GET", "/v1/w3s/wallets?blockchain=ARC-TESTNET&pageSize=50");
  if (listed.status !== 200) {
    console.log(`wallets HTTP ${listed.status} ${listed.parsed?.message || ""}`);
    process.exit(2);
  }
  const byRef = new Map();
  for (const wallet of listed.parsed?.data?.wallets || []) {
    if (wallet.refId) byRef.set(wallet.refId, wallet);
    if (wallet.name) byRef.set(wallet.name, wallet);
  }

  const actors = [];
  for (const label of labels) {
    let wallet = byRef.get(label);
    if (!wallet) {
      const created = await request(apiKey, "POST", "/v1/w3s/developer/wallets", {
        idempotencyKey: crypto.randomUUID(),
        entitySecretCiphertext: await ciphertext(apiKey, secret),
        walletSetId,
        blockchains: ["ARC-TESTNET"],
        count: 1,
        accountType: "EOA",
        metadata: [{ name: label, refId: label }],
      });
      wallet = created.parsed?.data?.wallets?.[0];
      if (!wallet) {
        console.log(`create ${label} HTTP ${created.status} ${created.parsed?.message || ""}`);
        process.exit(2);
      }
      console.log("created", label, wallet.blockchain, wallet.state);
    } else {
      console.log("exists", label, wallet.blockchain, wallet.state);
    }
    actors.push({
      label,
      circleWalletId: wallet.id,
      arcAddress: wallet.address,
      peaqMachineId: label.startsWith("servebot") ? "" : null,
    });
  }

  const operator = actors.find((actor) => actor.label === "operator");
  const settler = actors.find((actor) => actor.label === "settler");
  if (!operator?.arcAddress || operator.arcAddress.toLowerCase() === settler?.arcAddress?.toLowerCase()) {
    console.log("settler matches operator");
    process.exit(2);
  }

  const example = JSON.parse(fs.readFileSync(examplePath, "utf8"));
  example.escrow.address = "0xREPLACE_AFTER_DEPLOY";
  example.actors = actors;
  fs.writeFileSync(outPath, `${JSON.stringify(example, null, 2)}\n`);
  console.log("wrote config/wallets.json", actors.length);

  for (const label of ["guest-bob", "servebot-1"]) {
    const actor = actors.find((item) => item.label === label);
    const drip = await request(apiKey, "POST", "/v1/faucet/drips", {
      address: actor.arcAddress,
      blockchain: "ARC-TESTNET",
      usdc: true,
    });
    console.log(`faucet ${label} HTTP ${drip.status} ${drip.parsed?.message || drip.parsed?.data?.status || "ok"}`);
  }
}

main().catch((error) => {
  console.log("failed", error.message);
  process.exit(1);
});
