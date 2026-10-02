const HOSTS: Record<string, string> = {
  sandbox: "https://api-sandbox.circle.com",
  production: "https://api.circle.com",
};

export async function testCircleWallets(credentials: Record<string, string>) {
  try {
    const apiKey = credentials.CIRCLE_API_KEY;
    if (!apiKey) {
      return { success: false, error: "CIRCLE_API_KEY is required" };
    }

    const env = (credentials.CIRCLE_ENV || "sandbox").toLowerCase();
    const base = HOSTS[env] ?? HOSTS.sandbox;

    // Do not send the entity secret on the test call.
    const response = await fetch(`${base}/v1/w3s/config/entity`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        return { success: false, error: "Invalid Circle API key" };
      }
      return { success: false, error: `HTTP ${response.status}` };
    }

    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}
