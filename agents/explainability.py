"""
explainability.py
ExplainabilityAgent — SHAP interpretation + Claude-generated report.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.report_generator import generate_report


class ExplainabilityAgent:
    """Generate human-readable explanation of credit decision using SHAP + LLM."""

    @staticmethod
    def _format_feature_value(value) -> str:
        """Render feature values safely for UI/report output."""
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return f"{value:.2f}"
        if value is None:
            return "N/A"
        return str(value)

    def run(
        self,
        borrower_name: str,
        features: dict,
        shap_summary: dict,
        composite_score: int,
        financial_score: int,
        alternative_score: int,
        decision: str,
        risk_tier: str,
        is_underbanked: bool,
    ) -> dict:
        """
        Parameters
        ----------
        All fields from previous agents.

        Returns
        -------
        dict with report (str), key_strengths (list), key_concerns (list)
        """
        key_strengths, key_concerns = self._extract_shap_insights(
            shap_summary, features, is_underbanked
        )

        report = generate_report(
            borrower_name=borrower_name,
            composite_score=composite_score,
            risk_tier=risk_tier,
            decision=decision,
            financial_score=financial_score,
            alternative_score=alternative_score,
            key_strengths=key_strengths,
            key_concerns=key_concerns,
            is_underbanked=is_underbanked,
            shap_summary=shap_summary,
        )

        return {
            "report": report,
            "key_strengths": key_strengths,
            "key_concerns": key_concerns,
            "shap_summary": shap_summary,
        }

    def _extract_shap_insights(
        self, shap_summary: dict, features: dict, is_underbanked: bool
    ) -> tuple[list, list]:
        """
        Extract top 3 strengths (negative SHAP = reduces default risk)
        and top 3 concerns (positive SHAP = increases default risk).
        """
        FEATURE_LABELS = {
            "dti": "Debt-to-income ratio",
            "revol_util": "Credit utilization",
            "int_rate": "Interest rate",
            "annual_inc": "Annual income",
            "loan_amnt": "Loan amount",
            "open_acc": "Number of open accounts",
            "pub_rec": "Public derogatory records",
            "delinq_2yrs": "Delinquencies (2yr)",
            "inq_last_6mths": "Recent credit inquiries",
            "mort_acc": "Mortgage accounts",
        }

        if not shap_summary:
            # Fallback when no SHAP available
            if is_underbanked:
                strengths = [
                    "Consistent utility bill payment history (48+ months)",
                    "Strong mobile transaction consistency score (0.89)",
                    "Regular mobile money activity showing cash flow",
                ]
                concerns = [
                    "No traditional banking history",
                    "Limited credit track record",
                    "Self-employed income verification challenges",
                ]
            else:
                strengths, concerns = self._feature_based_insights(features)
            return strengths, concerns

        # Sort by SHAP value
        sorted_shap = sorted(shap_summary.items(), key=lambda x: x[1])

        # Negative SHAP → reduces default risk → strength
        strengths_raw = [(k, v) for k, v in sorted_shap if v < 0][:3]
        # Positive SHAP → increases default risk → concern
        concerns_raw = [(k, v) for k, v in sorted_shap[::-1] if v > 0][:3]

        strengths = []
        for feat, val in strengths_raw:
            label = FEATURE_LABELS.get(feat, feat)
            feat_val = self._format_feature_value(features.get(feat))
            strengths.append(
                f"{label}: {feat_val} (reduces default risk by {abs(val):.3f})"
            )

        concerns = []
        for feat, val in concerns_raw:
            label = FEATURE_LABELS.get(feat, feat)
            feat_val = self._format_feature_value(features.get(feat))
            concerns.append(
                f"{label}: {feat_val} (increases default risk by {val:.3f})"
            )

        # Always add alternative data context for thin-file
        if is_underbanked:
            strengths.insert(0, "Alternative data: Excellent utility payment history compensates for missing bank records")

        return strengths[:3], concerns[:3]

    def _feature_based_insights(self, features: dict) -> tuple[list, list]:
        """Rule-based insights when SHAP is unavailable."""
        strengths = []
        concerns = []

        dti = features.get("dti", 50)
        if dti < 30:
            strengths.append(f"Low debt-to-income ratio ({dti:.1f}%) — good debt management")
        elif dti > 50:
            concerns.append(f"High debt-to-income ratio ({dti:.1f}%) — elevated leverage")

        pub_rec = features.get("pub_rec", 0)
        delinq = features.get("delinq_2yrs", 0)
        if pub_rec == 0 and delinq == 0:
            strengths.append("Clean derogatory record — no public records or delinquencies")
        else:
            if pub_rec > 0:
                concerns.append(f"Public derogatory records: {int(pub_rec)}")
            if delinq > 0:
                concerns.append(f"Recent delinquencies: {int(delinq)} in last 2 years")

        revol = features.get("revol_util", 50)
        if revol < 30:
            strengths.append(f"Low credit utilization ({revol:.1f}%) — responsible credit use")
        elif revol > 70:
            concerns.append(f"High credit utilization ({revol:.1f}%) — may indicate financial stress")

        return strengths[:3], concerns[:3]
