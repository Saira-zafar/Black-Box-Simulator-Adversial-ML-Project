"""
Results and Severity Analyzer.

Evaluates simulation step results, compares expected vs observed behavior,
computes overall security verdict, and assigns severity based on predefined rules.
"""

from typing import List, Dict, Any, Tuple


def evaluate_simulation_results(
    scenario: Dict[str, Any],
    step_results: List[Dict[str, Any]],
    simulation_status: str
) -> Tuple[str, str, str]:
    """
    Evaluates step results and returns:
    (overall_verdict, calculated_severity, summary)
    
    Verdicts:
    - SECURE (all steps passed expected security baseline)
    - VULNERABLE (one or more steps failed, indicating security flaw)
    - SAFETY_BLOCKED (attempted to target non-local host)
    - ERROR (connection or unexpected runtime failure)
    """
    if simulation_status == "SAFETY_BLOCKED":
        return (
            "SAFETY_BLOCKED",
            "INFO",
            "Simulation was aborted by Safety Guardrail. The target host is outside the authorized local sandbox."
        )

    if not step_results:
        return ("ERROR", "INFO", "No test steps were executed.")

    failed_steps = [s for s in step_results if s.get("verdict") == "FAIL"]
    total_steps = len(step_results)

    if not failed_steps:
        overall_verdict = "SECURE"
        calculated_severity = "INFO"
        summary = (
            f"All {total_steps} educational security checks passed. The target application "
            f"demonstrated resilient security controls for {scenario.get('name')}."
        )
    else:
        overall_verdict = "VULNERABLE"
        calculated_severity = scenario.get("severity_default", "MEDIUM")
        summary = (
            f"VULNERABILITY CONFIRMED: {len(failed_steps)} of {total_steps} checks failed. "
            f"Target exhibited insecure behavior corresponding to {scenario.get('cwe_id')} "
            f"({scenario.get('owasp_category')}) with assigned severity {calculated_severity}."
        )

    return overall_verdict, calculated_severity, summary
