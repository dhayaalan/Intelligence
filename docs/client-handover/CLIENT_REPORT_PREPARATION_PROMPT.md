# Reusable Prompt: Prepare a Client Overview & Demo Plan

**How to use:** Copy the prompt below and provide it to Antigravity whenever a new client needs a customized, professional, 2–3 page platform overview and demonstration plan.

---

```markdown
# TASK: PREPARE A CLIENT-FACING OVERVIEW AND DEMO PLAN

## Project Context
- **Repository Location:** `/home/songoku/Pictures/Intelligence`
- **Template Reference:** `docs/client-handover/CLIENT_OVERVIEW_TEMPLATE.md`
- **Target Output File:** `docs/client-handover/CLIENT_OVERVIEW_[CLIENT_NAME].md`

## Client Information
- **Client Name:** [Insert Client Name, e.g., Apex Risk Consulting]
- **Primary Business Objective:** [e.g., Corporate fraud investigation and third-party vendor due diligence]
- **Most Critical Target Types:** [e.g., Corporate entities, domain names, executive profiles]
- **Required Sources / Regions:** [e.g., US SEC EDGAR corporate filings, Global News, Web Archives, OpenSanctions]
- **Commercial API Subscriptions Available:** [e.g., None - use public tools only / Client has Shodan API key]
- **Preferred Report Deliverable Format:** [e.g., PDF Executive Dossier]
- **Hosting Preference:** [e.g., Managed Cloud SaaS / Private On-Premises Docker Stack]
- **Agreed Demonstration Target:** [e.g., apple.com or safe public corporate target]

## Instructions for Antigravity

1. **Inspect and Verify the Actual Codebase:**
   - Review current capabilities in the repository without making code changes.
   - Verify that the features planned for the demo (search, case creation, entity graph, evidence vault, dossier export) are operational.
   - Ensure the recommended demo target works cleanly.

2. **Generate the Client Document:**
   - Copy the structure from `docs/client-handover/CLIENT_OVERVIEW_TEMPLATE.md`.
   - Replace all placeholders with the client details above.
   - Write in simple, polished professional English suitable for business executives, investigators, and managers.
   - Keep the length to approximately 2–3 pages.

3. **Strict Client-Facing Rules:**
   - DO NOT include internal file paths (e.g., no `backend/app/...` or `frontend/src/...`).
   - DO NOT include code snippets, test logs, or developer task lists.
   - DO NOT expose API keys, passwords, or credentials.
   - DO NOT make unverified claims. Clearly disclose any required API keys or public rate limits.
   - DO NOT overwrite the master template (`CLIENT_OVERVIEW_TEMPLATE.md`).

4. **Required Document Structure:**
   - **Page 1 — Understanding the Client's Needs:**
     - Purpose of the Platform
     - What the Client Can Achieve
     - Who Will Use the Platform (User Personas)
   - **Page 2 — How the Demo Will Work:**
     - Proposed Investigation Workflow (7-step diagram)
     - Proposed Demo Plan (20–30 minute agenda with safe inputs and clear takeaways)
     - Expected Outcome
   - **Page 3 — Client Confirmation and Next Steps:**
     - Requirements to Confirm (focused questions)
     - Recommended Next Steps (5-step rollout)
     - Professional Closing Statement

5. **Optional Document Conversion:**
   - If suitable document tools are available, also generate:
     - `docs/client-handover/CLIENT_OVERVIEW_[CLIENT_NAME].docx`
     - `docs/client-handover/CLIENT_OVERVIEW_[CLIENT_NAME].pdf`

6. **Final Summary:**
   - Confirm the created files, summarize how the plan matches the client's goals, and state any items requiring client clarification.
```
