export async function testPeaqos(credentials: Record<string, string>) {
  try {
    const mcr = credentials.PEAQOS_MCR_URL || "https://mcr.peaq.xyz";
    const response = await fetch(`${mcr.replace(/\/$/, "")}/health`, {
      method: "GET",
    });
    if (response.status === 404) {
      // Health path varies; a reachable host is enough for Test Connection.
      return { success: true };
    }
    if (!response.ok && response.status >= 500) {
      return { success: false, error: `MCR HTTP ${response.status}` };
    }
    return { success: true };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error),
    };
  }
}
