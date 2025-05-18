export async function logPromptUsage({ slug, title, context, input, output }) {
  try {
    const res = await fetch("http://localhost:8000/api/mcp/prompt-usage/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt_slug: slug,
        prompt_title: title,
        used_by: context,
        input_context: input, // ← now a proper string
        rendered_prompt: output,
        result_output: "",
      }),
    });

    if (!res.ok) {
      const error = await res.text();
      console.warn("❌ Failed to log prompt usage", error);
    }
  } catch (err) {
    console.error("❌ Log prompt usage error", err);
  }
}
