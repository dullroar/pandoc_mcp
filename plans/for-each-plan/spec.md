# Specification

State the goal and exclusions. Mark each rule as documented or inferred. Give the source
for a documented rule. Ask the owner to confirm any inferred rule.

## Requirements

Give each requirement an ID. Cite the ID in the step's `requirements` field.

### R1. <Required behavior>

- Source or assumption.
- Example input and expected result.
- Protected acceptance check.

## Constraints and delegated authority

Record constraints, assumptions and who can confirm them. Check exceptions, unusual combinations
and values that look impossible. Record the owner's decision for each open rule.

Record the owner's approval and its date. List the files, commands and decisions within scope.
Escalate contradictions, scope changes, actions outside that authority and protected checks
that cannot pass as written.

## Acceptance and evidence

List the protected checks and the command for combined validation after parallel steps merge.
Record results in each step's `evidence` field.

## Exceptions and retirements

Record whether the test was wrong, the documentation needed correction, the owner retired the
rule, or the owner accepted a violation of a rule that still applies. For a tolerated violation,
record the reason, decision owner, affected parties, how to measure the violation, and the review
date or trigger. See the [exception record template](../archive/legacy-template/exception-record.md).
