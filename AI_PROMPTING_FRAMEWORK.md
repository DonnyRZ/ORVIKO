# AI Prompting Framework for Action-Based Applications

This document outlines a general prompting framework for AI-powered applications where a user triggers an action through a button, form, workflow, or event. The goal is not to build a conversational assistant, but to design a reliable execution system for tasks like extraction, classification, transformation, drafting, review, scoring, and recommendation.

The framework is inspired by modular prompt architecture patterns used in agent systems, but it is intentionally adapted for non-conversational product features and internal automations.

## Why this is different from conversational AI

In a chat product, the primary unit of design is the conversation. In an action-based application, the primary unit of design is the task invocation.

That changes the prompting strategy:

- The system should optimize for task correctness, not open-ended dialogue.
- Inputs should be structured and explicit, not assumed from chat history.
- Outputs should be validated objects or constrained artifacts, not freeform prose by default.
- Prompt design should be tied to product behavior, workflow state, and business policy.
- Enforcement should live in code and policy layers, not only in prompt wording.

The core mental model is simple: treat the prompt as an execution contract for a specific application action.

## Core principles

### 1. Model AI features as Actions

Each AI capability should be defined as a named action with a clear contract. Avoid a single generic prompt that tries to handle every feature.

Examples:

- `extract_invoice_fields`
- `classify_support_ticket`
- `draft_release_notes`
- `review_policy_document`
- `recommend_next_best_action`

Each action should define:

- the business goal
- the expected inputs
- the required context
- the allowed level of inference
- the output schema
- the fallback behavior

### 2. Separate stable instructions from run-time payload

Do not mix long-lived guidance with per-request data.

Stable instructions include:

- role definition
- business rules
- glossary and terminology
- output formatting rules
- escalation and confidence rules
- examples that rarely change

Run-time payload includes:

- user-selected inputs
- record data
- document contents
- metadata
- feature flags
- temporary overrides

This separation improves maintainability, observability, and prompt caching behavior.

### 3. Treat prompt assembly as a first-class system

Prompt generation should be centralized in a builder layer, not scattered across controllers, UI handlers, or background jobs.

A prompt builder should be responsible for:

- selecting the correct action spec
- assembling prompt layers in a fixed order
- formatting structured context
- enforcing input size limits
- marking truncated context explicitly
- injecting output schema instructions
- producing debug metadata for logs and evaluation

### 4. Keep enforcement outside the prompt

Prompts guide the model. They do not reliably enforce policy on their own.

Critical controls should live elsewhere:

- schema validation
- deterministic business rules
- permission checks
- human approval gates
- confidence thresholds
- retry policy
- redaction and privacy controls
- post-processing validators

If an output would be unsafe or invalid for the business, code should block it even if the prompt told the model not to produce it.

### 5. Design for uncertainty, not just success

Many AI application failures come from overconfident guesses, not hard crashes.

Every action should define:

- when the model may infer missing information
- when it must return `unknown`
- when it must return `needs_human_review`
- what counts as sufficient evidence
- what missing inputs should be surfaced back to the system

Uncertainty handling should be explicit in both prompt instructions and output schema.

## Prompt layer framework

For action-based applications, a useful default is to build each prompt from five layers.

### 1. Role layer

Defines what the model is for this action.

Examples:

- "You are an information extraction engine."
- "You are a policy review assistant."
- "You are a document transformation engine."

This layer should be narrow and task-specific. Avoid broad personas unless they materially improve task performance.

### 2. Task layer

Defines what the model must do in this run.

This should include:

- the exact task objective
- the completion criteria
- any ranking or prioritization logic
- any required decision boundaries

Example:

> Extract only the invoice fields requested below. If a field is not explicitly present in the source, return `unknown` instead of guessing.

### 3. Policy layer

Defines the operational rules for the task.

This often includes:

- business rules
- regulatory or compliance constraints
- allowed inference level
- refusal conditions
- escalation rules
- confidence policy

Example:

> Do not infer legal entity names from email addresses alone. If evidence is weak or conflicting, set `status` to `needs_human_review`.

### 4. Context layer

Contains the run-time data and references the model needs.

This can include:

- source text
- selected records
- retrieved passages
- domain definitions
- current workflow state
- user-supplied parameters
- previous machine-generated artifacts when relevant

Context should be curated, not dumped blindly. The builder should prefer relevance over volume.

### 5. Output layer

Defines exactly how the model should respond.

This should specify:

- output schema or format
- required fields
- allowed status values
- explanation fields if needed
- confidence fields if needed
- failure and escalation encoding

Example:

```json
{
  "status": "success | partial | insufficient_input | needs_human_review",
  "result": {},
  "warnings": [],
  "missing_inputs": [],
  "confidence": "low | medium | high"
}
```

## Framework primitives

These primitives are conceptual building blocks for an AI application runtime.

### `ActionSpec`

Defines a reusable AI action contract.

Suggested contents:

- `actionId`
- `goal`
- `inputSchema`
- `requiredContext`
- `promptModules`
- `outputSchema`
- `executionModes`
- `policyRules`
- `qualityChecks`
- `fallbackBehavior`

### `ActionRequest`

Represents one invocation of an action.

Suggested contents:

- `actionId`
- `trigger`
- `actor`
- `input`
- `context`
- `metadata`
- `mode`
- `requestId`

### `PromptModule`

A reusable prompt fragment with a stable purpose.

Examples:

- role definition
- output contract
- domain glossary
- confidence policy
- safety and compliance rules
- formatting examples

Prompt modules should be versioned and traceable.

### `PromptBuildResult`

The output of the prompt builder.

Suggested contents:

- `systemInstructions`
- `runtimeContext`
- `assembledPrompt`
- `promptVersion`
- `moduleVersions`
- `truncationInfo`
- `debugMetadata`

### `ActionResult`

The structured result produced by the model before or after validation.

Suggested contents:

- `status`
- `result`
- `warnings`
- `missingInputs`
- `confidence`
- `explanation`
- `evidence`

### `ValidationResult`

Describes whether the action result is safe and usable.

Suggested contents:

- `isValid`
- `schemaValid`
- `policyValid`
- `requiresRetry`
- `requiresHumanReview`
- `errors`

### `ExecutionPolicy`

Defines runtime behavior outside the prompt.

Suggested contents:

- allowed model profile
- strictness mode
- retry strategy
- validation requirements
- confidence threshold
- human review threshold
- timeout budget
- cost budget

## Action types and when to use them

Most AI application features fall into a small number of action families.

### Generate

Use when the product needs a new artifact.

Examples:

- draft an email
- generate a summary
- write release notes

Best practice:

- clearly define audience and tone
- constrain structure if downstream systems depend on it
- keep creative freedom explicit rather than implied

### Transform

Use when the product changes an existing artifact into another form.

Examples:

- rewrite for clarity
- convert notes into a template
- normalize text into a structured format

Best practice:

- define what must be preserved
- define what may change
- include formatting constraints

### Extract

Use when the product needs to pull structured fields from unstructured input.

Examples:

- extract invoice metadata
- extract contract clauses
- extract entities from support tickets

Best practice:

- bias toward evidence over completion
- require `unknown` for missing fields
- avoid silent guessing

### Classify

Use when the product needs categories, labels, priority, or routing.

Examples:

- assign issue type
- determine urgency
- route requests to queues

Best practice:

- define label taxonomy precisely
- include tie-breaking rules
- encode abstain or review states

### Review

Use when the product needs findings, risks, or quality judgments.

Examples:

- review a draft for policy issues
- assess a document for missing sections
- detect likely defects in generated output

Best practice:

- define what counts as a finding
- prioritize severity
- require evidence or references where possible

### Recommend

Use when the product needs options and suggested next actions.

Examples:

- recommend a response strategy
- suggest a next workflow step
- propose a remediation path

Best practice:

- separate recommendation from justification
- capture assumptions
- represent confidence explicitly

## Output contract and validation model

Application actions should default to structured output even when the user-facing experience later turns that output into prose.

### Recommended output shape

Use a top-level result envelope with explicit states.

Suggested pattern:

- `success`
- `partial`
- `insufficient_input`
- `needs_human_review`
- `failed_policy`

The result should distinguish between:

- the business result
- the model's confidence
- the reasons for uncertainty
- missing fields or missing evidence
- warnings for downstream systems

### Validation layers

Run at least three validation layers after model output:

1. **Schema validation**
   Ensure the output is structurally valid.

2. **Policy validation**
   Ensure output respects business rules and inference limits.

3. **Quality validation**
   Check for missing required fields, unsupported claims, low-confidence states, or formatting problems.

If validation fails, the system can:

- retry with a repair prompt
- downgrade to partial result
- escalate to human review
- reject the run

## Observability and evaluation

Treat prompting as an observable system, not hidden glue.

### Recommended run metadata

Log these fields for every action execution:

- `actionId`
- prompt spec version
- model and settings
- prompt module versions
- request size and truncation flags
- validation outcome
- retry count
- final system outcome

### Recommended debug surfaces

Provide internal tools for:

- prompt preview
- prompt diff between versions
- output validation report
- replay of failed cases
- benchmark runs against saved evaluation cases

### Evaluation set design

Create test cases per action family:

- happy path
- incomplete input
- conflicting evidence
- noisy input
- ambiguous input
- adversarial formatting
- low-confidence scenarios
- mandatory human-review scenarios

Evaluate not only correctness, but also:

- schema validity rate
- hallucination rate
- abstain behavior
- escalation accuracy
- stability across prompt revisions

## Implementation checklist

Use this checklist when adding a new AI-powered feature.

- Define the feature as an `ActionSpec`.
- Write the business goal in one sentence.
- Define explicit input and output contracts.
- Decide what the model may and may not infer.
- Split stable instructions from run-time payload.
- Build the prompt through a centralized prompt builder.
- Add schema validation for the output.
- Add policy validation for business constraints.
- Decide retry, fallback, and human-review behavior.
- Add observability fields and prompt versioning.
- Add evaluation cases before broad rollout.
- Monitor real-world failure modes and update the action spec, not only the surface prompt text.

## Practical guidance

If you are designing an AI application feature, start with the action contract before writing any prompt text. Define what the system is trying to achieve, what evidence is allowed, what a correct result looks like, and what should happen when certainty is too low. Only then write prompt modules and assemble them with a builder.

That discipline makes AI features easier to test, safer to ship, cheaper to run, and easier to evolve over time.
