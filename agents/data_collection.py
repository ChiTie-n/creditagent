"""
data_collection.py
DataCollectionAgent — fetch mock borrower data from personas.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mock_data.personas import PERSONAS


class InsufficientDataError(Exception):
    pass


class DataCollectionAgent:
    """Fetch and validate borrower data from mock data store."""

    def run(self, borrower_id: str) -> dict:
        """
        Parameters
        ----------
        borrower_id : str — e.g. "borrower_001"

        Returns
        -------
        dict with keys: raw_data, data_completeness, sources_available
        """
        if borrower_id not in PERSONAS:
            raise ValueError(f"Unknown borrower_id: {borrower_id}")

        persona = PERSONAS[borrower_id]

        # Count available data sources
        sources = {
            "bank_data": persona.get("bank_data") is not None,
            "utility_data": persona.get("utility_data") is not None,
            "mobile_data": persona.get("mobile_data") is not None,
        }
        available = sum(sources.values())
        data_completeness = available / 3.0

        if data_completeness < 0.33:
            raise InsufficientDataError(
                f"Borrower {borrower_id} has insufficient data "
                f"(completeness={data_completeness:.0%}). "
                "At least 1 data source required."
            )

        return {
            "borrower_id": borrower_id,
            "name": persona.get("name", f"Unknown Name ({borrower_id})"),
            "scenario": persona.get("scenario", "Custom scenario"),
            "loan_amount_requested": float(persona.get("loan_amount_requested", 0.0)),
            "bank_data": persona.get("bank_data"),
            "utility_data": persona.get("utility_data"),
            "mobile_data": persona.get("mobile_data"),
            "profile": persona.get("profile", {}),
            "data_completeness": data_completeness,
            "sources_available": sources,
        }
