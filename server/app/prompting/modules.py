from __future__ import annotations

from app.prompting.contracts import PromptModule


PROMPT_MODULES: dict[str, PromptModule] = {
  "refiner_role": PromptModule(
    name="refiner_role",
    layer="role",
    content="You are a visual slide design strategist.",
  ),
  "refiner_task": PromptModule(
    name="refiner_task",
    layer="task",
    content="Turn the user's slide text, notes, and embed hints into a concise production brief for an image generation model.",
  ),
  "refiner_policy": PromptModule(
    name="refiner_policy",
    layer="policy",
    content="The slide text is the only text allowed to appear visibly in the final image and must be used exactly and completely. User notes are guidance only and must never appear as visible text. The design direction must feel extraordinary, highly creative, polished, and visually distinctive by default, not bland, generic, or template-like. Plan a clean composition for the requested canvas aspect ratio with strong readability, bold hierarchy, intentional spacing, and a strong art direction that matches the meaning and tone of the slide text. Keep background noise controlled, but avoid flat or boring compositions. Favor an editorial, high-impact, visually memorable result with creative composition, clarity, color harmony, selective depth, and supportive visual storytelling when appropriate. Strong contrast or impact does not require a dark, moody, cinematic, or low-key palette by default. High-quality visuals may be bright, airy, fresh, luminous, colorful, or clean when that better fits the slide. Derive brightness, palette, and lighting from the slide meaning, readability needs, and any user notes rather than from a generic dramatic bias. If there is no strong signal toward a darker mood, prefer a balanced-light, readable, non-gloomy direction. Important content must be kept safely away from the extreme top and bottom edges. If embed images are provided, explain how each should be integrated contextually. If no embeds are provided, suggest simple supportive visuals only.",
  ),
  "refiner_output": PromptModule(
    name="refiner_output",
    layer="output",
    content="Return only a concise production brief with sections for Composition, Text Treatment, Visual Style, Background, Embed Usage, and Constraints. In Visual Style and/or Background, explicitly state the intended brightness or mood as light, balanced, or dark based on the slide meaning and notes. Default to balanced-light when there is no strong reason to go dark. Do not include chatty commentary.",
  ),
  "image_role": PromptModule(
    name="image_role",
    layer="role",
    content="You are generating a clean slide image for the requested canvas ratio.",
  ),
  "image_task": PromptModule(
    name="image_task",
    layer="task",
    content="Use the provided production brief, the exact slide text, and any supplied reference images.",
  ),
  "image_policy": PromptModule(
    name="image_policy",
    layer="policy",
    content="Render only the provided slide text as visible text. The final design should feel extraordinary, highly creative, polished, visually striking, and non-generic. Favor strong hierarchy, intentional composition, distinctive shapes, selective depth, color harmony, and high visual impact that matches the meaning and tone of the slide text. Avoid bland, repetitive, stock-like, or template-style layouts. Strong contrast does not mean low-key lighting or a dark palette by default. High-quality visuals may be bright, clean, airy, colorful, luminous, or balanced when that better supports the content. Choose brightness, palette, and lighting from the slide meaning, readability, and production brief rather than a generic cinematic bias. Unless the brief or user notes clearly call for a dark mood, avoid unnecessarily dark or gloomy styling and keep the result open, readable, and balanced. Do not render user notes, instruction text, measurement text, percentages, labels, interface elements, watermarks, platform-specific layouts, or branding unless they are explicitly part of the provided slide text. Keep the composition centered, readable, and comfortably away from the top and bottom edges.",
  ),
  "image_output": PromptModule(
    name="image_output",
    layer="output",
    content="Produce an image response for the provided slide.",
  ),
}
