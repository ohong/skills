# Model and quality selection

The user's preference is the newest available flagship GPT Image model and its highest supported quality setting.
Prioritize final image quality over generation speed. Apply this preference to variants and revisions too, unless the user changes it.

## Refresh the selection

Before generating, check the current [OpenAI image generation guide](https://developers.openai.com/api/docs/guides/image-generation)
and, when needed, the [model catalog](https://developers.openai.com/api/docs/models).
Verify the selected model is available through the actual execution route, not merely announced.
Prefer the current flagship for final artistic quality over a cheaper or faster variant.
Use the highest documented quality value; `auto` does not guarantee the maximum.
Do not derive model IDs from product names or assume quality enums remain unchanged.

As verified on October 12, 2026, the reference selection is `gpt-image-2.5-sunburst` with `quality=max`.
The guide lists `low`, `medium`, `high`, `xhigh`, `max`, and `auto` for GPT Image 2.5.
This is a dated starting point, not a permanent model pin. Replace it with a newer available flagship when official guidance supports that choice.

## Execution controls and limits

Use `$imagegen`, following its built-in default and its explicit CLI/API fallback rules.
Keep execution parameters separate from the art prompt.

| Execution route | Action |
|---|---|
| Built-in imagegen exposes model and quality selectors | Set the verified model and maximum quality using the actual supported arguments. |
| Built-in imagegen hides those selectors | Prepare the complete prompt and reference selection. Explain that backend-managed settings cannot be verified or forced through prompt wording. Resolve this limitation with the user before generation. |
| User explicitly authorizes imagegen's CLI/API fallback | Inspect the bundled CLI's supported arguments and validation. Use the verified model and maximum quality only if that CLI supports both. |
| Bundled CLI rejects the required model or quality | Report the compatibility gap and stop that route. Follow imagegen's rule against modifying its script or replacing it with a one-off runner. |

When controls are hidden, offer two concrete choices: built-in generation with backend-managed settings, or imagegen's CLI/API path for explicit controls.
Explain any known CLI compatibility gap in that same request. Existing authorization for a route remains valid.
If the user accepts built-in generation, record model and quality as **backend-managed, unverified**.
Do not silently substitute an older model or a lower quality tier.

At creation time, the built-in `image_gen` tool has no model or quality arguments.
The installed imagegen CLI accepts GPT Image model names but validates quality only through `high`; it rejects `max`.
Recheck these capabilities at invocation time. Neither route currently proves the exact Sunburst/max requirement through this skill alone.

Record the generation route, verified model ID, quality setting, and documentation check date with the final prompt.
Describe only settings actually selected or reported by the tool.
