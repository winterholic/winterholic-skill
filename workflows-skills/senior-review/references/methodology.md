# Senior-Review Skill — Methodology Brief (researched, cited)

> 이 문서는 senior-review 스킬 설계의 근거다. 워크플로우 lane 프롬프트·심각도 보정·검증 규칙은 모두 여기서 도출됐다. 출처 URL은 각 주장 옆 대괄호.
>
> **운영상 오버라이드 1건**: 아래 브리프는 "nit을 공격적으로 억제(signal ratio>60% 등 크기 기반 컷)"를 권한다. 하지만 이 스킬은 사용자 요구에 따라 **"적은 사소함이 아니라 맥락맹(context-blindness)"**이라는 대원칙으로 이를 오버라이드한다 — 크기 기반 하드컷(signal ratio) 대신 **맥락 근거 게이트**를 쓴다. 맥락에 근거한 사소한 발견은 non-blocking nit으로 살리고, 맥락맹(표면 패턴매칭·도달불가·의도된 트레이드오프 무시)은 크기 무관 컷한다. 브리프의 라벨 체계·tier·reachability·다중패스·LLM 함정 완화책은 그대로 채택.

# METHODOLOGY BRIEF: Senior-Grade AI Code Review Skill

---

## 1. Senior Review Altitude & Intent-First Principles

**Review in this order. Do not skip levels.**

### Level 0 — Does This Change Deserve to Exist?
Before reading a single line of diff, evaluate the PR description against known architectural decisions and team context. Ask: "Is this well-conceived in light of what the team already decided?" [https://dev.to/huoru/we-have-code-review-we-need-intent-review-1i38] A technically correct implementation of a rejected design direction is a net-negative CL.

### Level 1 — Design
"Do the interactions of various pieces make sense?" [https://google.github.io/eng-practices/review/reviewer/looking-for.html] Read the primary logical file first — the one with the largest number of logical changes. [https://google.github.io/eng-practices/review/reviewer/navigate.html] If a significant design problem exists, surface it immediately, before completing the rest of the review. The cost of a developer building five more CLs on a broken design exceeds the cost of an incomplete first-pass review. [https://google.github.io/eng-practices/review/reviewer/navigate.html]

### Level 2 — Functionality & Correctness
Does the code do what the author intends, and is that intent correct for users?

### Level 3 — Complexity & Over-engineering
Flag code solving a speculative future problem rather than the present one (YAGNI). Speculative complexity carries a real ongoing cost. [https://google.github.io/eng-practices/review/reviewer/looking-for.html]

### Level 4 — Tests, Naming, Style
In that order. Do not reach this level if Level 1 or 2 has blockers — comments here become obsolete after high-level refactoring. [https://mtlynch.io/human-code-reviews-1/]

**The approval binary:** Approve when the CL "definitely improves overall code health", even if imperfect. Block only when it "definitely worsens overall code health." Blocking a net-positive CL for nitpicks is itself a reviewer failure. [https://google.github.io/eng-practices/review/reviewer/standard.html]

**Every non-trivial finding must cite the engineering principle it violates** (SRP, YAGNI, DRY, Law of Demeter, etc.) — not reviewer preference. "I would have done it differently" is not a finding. [https://mtlynch.io/human-code-reviews-1/] [https://google.github.io/eng-practices/review/reviewer/standard.html]

---

## 2. Severity + Comment-Worthiness Calibration Scheme

### Tier Pre-filter (run before writing any comment)

| Tier | Category | Examples | Eligible for blocking? |
|------|----------|----------|------------------------|
| T1 | Observable failures | crashes, breaking API contracts, exploitable security holes, data loss | Yes — must fix |
| T2 | Established-pattern violations | architectural inconsistency, measurable perf regression, tech debt with concrete carrying cost | Yes — should fix |
| T3 | Noise | style/formatting, subjective naming, micro-optimizations without measurable benefit | No — suppress or nit only |

**Signal ratio target:** (T1 + T2) / Total comments > 60%; aim > 80%. [https://jetxu-llm.github.io/posts/low-noise-code-review/] If nit-to-critical ratio exceeds 3:1, cut nits until the ratio inverts. [https://www.augmentcode.com/guides/what-does-nit-mean-in-code-review]

**Before emitting any comment, apply the three-filter gate:** [https://phauer.com/2018/code-review-guidelines/]
1. Is it true? (Can be grounded in a spec, test failure, or measurable regression — not opinion?)
2. Is it necessary? (Would leaving it unaddressed worsen code health?)
3. Is it kind? (Phrased as principle + evidence, not personal preference?)

Fail any filter → drop or convert to `question:`.

### Adopted Label Set (Conventional Comments + Google prefixes)

Use **one label per comment**, prepended verbatim:

| Label | Blocking by default | When to use |
|-------|--------------------|-|
| `issue:` | Yes | T1 findings. Must link to the spec, test, or policy it protects. |
| `issue (if-minor):` | Author's discretion | T1–T2 finding where the fix could be a separate PR if large. |
| `suggestion:` | No — must add `(blocking)` explicitly if it is | T2 finding with a concrete alternative. Phrase as "What do you think about X?" not "Do X." |
| `suggestion (blocking):` | Yes | T2 where you can demonstrate the current approach causes a measurable problem. |
| `nitpick:` | Never | T3. Non-blocking by nature. [https://conventionalcomments.org] Omit entirely if a linter could catch it. |
| `question:` | No | Behavior unclear from reading the implementation. Do not infer from naming alone. |
| `thought:` | No | YAGNI/over-engineering observations; alternative approaches where the author's is also valid. |
| `praise:` | N/A | At least one per review. Not optional — prevents adversarial tone. [https://conventionalcomments.org] |
| `Nit:` (Google style) | No | Alias for `nitpick:` when following Google conventions. [https://google.github.io/eng-practices/review/reviewer/comments.html] |
| `FYI:` | No | Educational context for future, not expected this CL. [https://google.github.io/eng-practices/review/reviewer/comments.html] |

**Blocking criteria checklist** — a comment earns `(blocking)` only when it covers: [https://www.propelcode.ai/blog/code-review-nitpicks-vs-must-fix-issues]
- [ ] A demonstrated failing behavior with a reproducible test, OR
- [ ] A security/regulatory control violation, OR
- [ ] A broken shipped API contract, OR
- [ ] Absent coverage on a critical path

**Suppress nits entirely if:** [https://www.augmentcode.com/guides/what-does-nit-mean-in-code-review]
- A linter/formatter already catches it
- It is purely personal preference with no style-guide citation
- The PR has blocking T1 issues (nit signal is drowned)
- The same pattern appears repeatedly (write a lint rule, not 20 comments — mention once)

**Empirical cost of excessive nits:** Reviews with 5 nits and 1 critical issue cause the critical issue to be overlooked; excessive nitpicking causes 20–40% velocity drops. [https://www.augmentcode.com/guides/what-does-nit-mean-in-code-review]

---

## 3. Rules for Respecting Author Intent / Killing False Positives

**Apply the "will this work?" filter, not the "how would I write it?" filter.** Classify every finding as `correctness/behavior` or `style/approach` before writing. Only correctness findings are blocking candidates. [https://www.seangoedecke.com/good-code-reviews/]

**Style without a style-guide citation is personal preference.** Before blocking on style, locate the rule in the team style guide. If no rule exists, the comment is opinion — downgrade to `nitpick:` or suppress. [https://google.github.io/eng-practices/review/reviewer/standard.html]

**Burden of proof shifts when the author has documented a trade-off.** A written rationale in the PR description or a comment is prima facie evidence of intentional choice. The reviewer must then show the trade-off is harmful — not merely different. If the author can demonstrate two approaches are equally valid, accept their preference. [https://google.github.io/eng-practices/review/reviewer/standard.html]

**Never infer behavior from naming alone.** Any finding derived purely from variable/function names rather than from reading the implementation must be labeled `question:`. [https://google.github.io/eng-practices/review/reviewer/looking-for.html]

**Verify reachability before posting security/correctness findings.** Does a call path exist from an entry point to this code? Is the input validated upstream? If reachability is unconfirmed, downgrade from `issue:` to `question:` and ask the author. [https://www.augmentcode.com/guides/static-code-analysis-best-practices-enterprise]

**YAGNI violations are `thought:`, not `issue:`.** Adding abstraction without present-day justification is subjective judgment, not a correctness defect. [https://google.github.io/eng-practices/review/reviewer/looking-for.html]

**Design choices require engineering-principle grounding.** When raising a design concern, state the specific principle being violated. "I would have structured it differently" without a named principle is a false positive. [https://google.github.io/eng-practices/review/reviewer/standard.html]

**Read the PR description, linked issues, and any ADRs before emitting findings.** A finding that contradicts an existing architectural decision record should be suppressed or converted to a `question:` asking whether the ADR still applies. [https://quickbirdstudios.com/blog/code-review-best-practices-guidelines/]

**Disagree-and-Commit:** After an author explains an intentional trade-off, either provide data to rebut it or accept the choice. Lingering unresolved preference objections are anti-patterns. [https://aws.amazon.com/blogs/enterprise-strategy/guts-part-three-having-backbone-disagreeing-and-committing/]

**Cap substantive comments at ~6.** Rank by severity; if the list exceeds 6, ask whether the lower-ranked items are genuinely blocking or noise. Trim structurally. [https://www.seangoedecke.com/good-code-reviews/]

---

## 4. Empirical Justification for Multi-Pass / Multi-Reviewer

### Hard Numbers

| Metric | Value | Source |
|--------|-------|--------|
| Optimal LOC per review session | 200–400 | [https://mikeconley.ca/blog/2009/09/14/smart-bear-cisco-and-the-largest-study-on-code-review-ever/] |
| Reviews above 400 LOC | Measurable defect-detection drop | same |
| Inspection rate ceiling | < 500 LOC/hour; above 450 LOC/hr → below-average detection in 87% of cases | same |
| Session duration ceiling | 60 min optimal; 90 min hard stop | same |
| Reviews finding zero defects (Cisco, 2,500 reviews) | 61% | same |
| Informal single-reviewer defect detection | < 50% | [https://www.ifsq.org/work-jones-1996.html] |
| Formal multi-reviewer inspection (Fagan) | 60–90% | [https://en.wikipedia.org/wiki/Fagan_inspection] |
| Design + code inspection combined | > 70% | [https://blog.codinghorror.com/code-reviews-just-do-it/] |
| Optimal reviewer count | 2 independent | [https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-sen.2020.0134] |
| Perspective-based teams vs. checklist-based | 41% more unique defects | [https://grokipedia.com/page/Software_inspection] |

### Why Author Annotation Matters Before Review Begins
When authors annotate their own changes before submission, defect density caps at 30/kLOC with modal outcome zero defects. Without annotation, variance is 10–130/kLOC. [https://mikeconley.ca/blog/2009/09/14/smart-bear-cisco-and-the-largest-study-on-code-review-ever/] Author self-review is a second-pass mechanism that raises the baseline before peer review starts.

### Why Independent Reviewers Add Value
Fagan: most defects are found during the group meeting phase, not individual preparation — meaning any single person's pass misses the majority of what the team collectively catches. [https://en.wikipedia.org/wiki/Fagan_inspection] Reviewers must be independent (not reading each other's comments first); serialized reviews collapse back toward a single-reviewer profile. [https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-sen.2020.0134]

### Security-Specific
Cross-directory complexity is the strongest negative predictor of security defect detection (Chromium OS logistic regression, AUC 0.91, 516 caught vs. 374 missed defects). More directories in a change = significantly more missed vulnerabilities. [https://arxiv.org/abs/2102.06909] Intervention: split large security-relevant changes.

---

## 5. LLM Reviewer Failure Modes and Mitigations

### Failure Mode 1: Systematic Overcorrection / False Positives
**Pattern:** LLMs flag compliant code as non-compliant across all tested models, triggered by specific code structures or requirement phrasings. [https://arxiv.org/pdf/2603.00539]
**Mitigation:** Add a mandatory second-pass self-check step in the review prompt: "For each finding, verify: is this rule actually violated in this specific code, given the context?" Reachability verification before posting security/correctness findings.

### Failure Mode 2: Nitpick Saturation
**Pattern:** 21% of CodeRabbit comments are nitpicks; 15% are outright noise; only ~36% deliver genuine value. [https://www.deployhq.com/blog/ai-code-review-before-you-deploy-our-experience-with-coderabbit]
**Mitigation:** Apply Tier pre-filter (§2) before emitting. Explicitly enumerate what CI already covers (linting, type checking) so the AI does not repeat that work. [https://docs.github.com/en/copilot/tutorials/use-custom-instructions]

### Failure Mode 3: Self-Review Hallucination
**Pattern:** A model writing and reviewing in the same session rationalizes its own choices and will not find the off-by-one error it just introduced. [https://asdlc.io/patterns/adversarial-code-review/]
**Mitigation:** Strict session separation. The validator receives only the diff + requirements with no knowledge of the builder's reasoning. Passing the builder's explanation alongside the diff poisons the validator's independence.

### Failure Mode 4: Context-Free Pattern Matching / Alert Fatigue
**Pattern:** Regex-triggered SQL injection and hardcoded secret flags are dismissed even when real ones appear because developers habituate to false positives. [https://thesagekhan.medium.com/codeguardian-ai-driven-security-code-review-with-natural-language-understanding-08fc1954d93f]
**Mitigation:** Gate security flags behind a deterministic tool confirmation step. Run a grep/AST script to confirm the assumption before posting a security comment. Use LLM as a false-positive filter on top of deterministic analyzers, not as primary detector. (LLM4PFA eliminates 94–98% of raw static analyzer false positives while preserving recall. [https://arxiv.org/html/2601.18844v1])

### Failure Mode 5: Missing Cross-File / Architectural Context
**Pattern:** AI achieves only 46% bug detection accuracy on runtime bugs; scores 1/5 on completeness; misses intent mismatches, cross-service dependencies, and historical design decisions entirely. [https://ucstrategies.com/news/coderabbit-review-2026-fast-ai-code-reviews-but-a-critical-gap-enterprises-cant-ignore/] 65% of developers cite missing context as the top AI review failure mode during refactoring. [https://www.digitalapplied.com/blog/ai-code-review-automation-guide-2025]
**Mitigation:** RAG-inject architectural documentation, internal conventions, and cross-service contracts alongside the diff — not just changed lines. RAG reduces hallucinations 60–80%. [https://diffray.ai/blog/llm-hallucinations-code-review/] Explicitly mark business-logic findings as "unverifiable without domain knowledge" rather than asserting correctness. [https://devclass.com/2025/03/19/graphite-debuts-diamond-ai-code-reviewer-insists-ai-will-never-replace-human-code-review/]

### Failure Mode 6: "Lost in the Middle" Context Degradation
**Pattern:** Critical constraints buried mid-context are de-emphasized due to RoPE-based positional encoding; U-shaped recall, middle positions treated as noise. [https://dev.to/thousand_miles_ai/the-lost-in-the-middle-problem-why-llms-ignore-the-middle-of-your-context-window-3al2]
**Mitigation:** Front-load the most important constraints (security invariants, architectural rules, team conventions) at the start of the review prompt. Use RAG to retrieve only the 3–5 most relevant adjacent files rather than stuffing the entire repo.

### Failure Mode 7: Negation Blindness
**Pattern:** "DO NOT flag X" instructions are the weakest enforcement points; LLMs follow negative constraints less reliably than positive ones. [https://asdlc.io/patterns/adversarial-code-review/]
**Mitigation:** Reframe suppression rules as allowlists: "Report only findings in categories: security, data-loss, correctness" rather than "Do not report style issues." Back up critical exclusions with deterministic pre-filters.

### Failure Mode 8: Vague Thoroughness Instructions
**Pattern:** "Be more accurate" or "Identify all issues" introduces noise and biases the model toward excessive fault-finding; detailed but vague prompts can increase misjudgment rates. [https://docs.github.com/en/copilot/tutorials/use-custom-instructions]
**Mitigation:** Specify exactly what CI already covers. Provide real codebase examples to calibrate the model's reference frame. Use structured severity output with explicit category definitions.

### Multi-Agent Orchestration (when applicable)
Parallel critique lanes (Architect + SecOps + QA agents running independently) catch meaningfully different bug categories than single-model review. Use different underlying models (e.g., Claude vs. Codex) to exploit divergent training and surface different failure modes. A Moderator role deduplicates feedback across lanes before surfacing to the developer. Cap total issues per review to force prioritization; block merges only on "critical"; flag "major" for human review; pass "minor" through silently. [https://www.mindstudio.ai/blog/automated-code-review-multiple-ai-agents] Multi-agent architectures improve consistency 85.5%; combining with RAG + static analysis achieves 89.5% precision improvement. [https://diffray.ai/blog/llm-hallucinations-code-review/]

---

## Design Directives (Imperatives the Skill MUST Encode)

1. **SURFACE design-level blockers in a dedicated first section, before any inline comments.** If design is unsound, do not approve even if all lines look clean.

2. **IDENTIFY the "epicenter" file explicitly** (largest logical change) and lead the report with findings from it before any supporting files or tests.

3. **LABEL every comment** with a Conventional Comments label (issue / suggestion / nitpick / question / thought / praise / FYI). Never emit an unlabeled comment.

4. **CITE the engineering principle violated** for every T1 or T2 finding. No principle citation → downgrade to `question:` or suppress.

5. **APPLY Tier pre-filter before writing any comment.** T3 findings that a linter could catch must be suppressed entirely or mentioned once as a lint-rule suggestion, never enumerated per instance.

6. **ENFORCE signal ratio > 60% (T1+T2)/total.** If the draft output fails this, cut nits until it passes.

7. **VERIFY reachability before posting security/correctness findings.** Unconfirmed reachability → `question:`, not `issue:`.

8. **SEPARATE review session from generation context.** The reviewer receives only diff + requirements — no builder reasoning — to prevent self-review hallucination.

9. **FRONT-LOAD architectural constraints in the prompt.** Security invariants and team conventions must appear at the start of context, not mid-prompt.

10. **USE allowlists, not blocklists.** Frame scope as "report only findings in: [categories]" — never rely on "DO NOT flag X" as the primary suppression mechanism.

11. **FLAG cross-file / business-logic findings as "requires human review"** rather than asserting correctness the model cannot verify without architectural context.

12. **NEVER block a CL on personal preference.** No style-guide citation = opinion = non-blocking at most.

13. **EMIT at least one `praise:` label per review.** Non-negotiable.

14. **CAP the total comment count at ~6 substantive findings.** Rank by severity; trim structurally if over the limit.