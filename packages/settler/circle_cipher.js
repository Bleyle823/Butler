const crypto = require("crypto");
const https = require("https");

const apiKey = process.argv[2] || "";
const secret = process.argv[3] || "";
const host = (process.argv[4] || "https://api.circle.com").replace(/^https?:\/\//, "");

function getPublicKey() {
  return new Promise((resolve, reject) => {
    const req = https.request(
      {
        hostname: host,
        path: "/v1/w3s/config/entity/publicKey",
        method: "GET",
        headers: {
          Authorization: `Bearer ${apiKey}`,
          Accept: "application/json",
          "User-Agent": "butler-check/1.0",
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
            parsed = {};
          }
          const pem = parsed.data && parsed.data.publicKey;
          if (res.statusCode !== 200 || !pem) {
            reject(new Error(`publicKey HTTP ${res.statusCode}`));
            return;
          }
          resolve(pem);
        });
      }
    );
    req.on("error", reject);
    req.end();
  });
}

getPublicKey()
  .then((pem) => {
    const ciphertext = crypto
      .publicEncrypt(
        {
          key: pem,
          padding: crypto.constants.RSA_PKCS1_OAEP_PADDING,
          oaepHash: "sha256",
        },
        Buffer.from(secret, "hex")
      )
      .toString("base64");
    process.stdout.write(ciphertext);
  })
  .catch((error) => {
    process.stderr.write(error.message || String(error));
    process.exit(1);
  });
