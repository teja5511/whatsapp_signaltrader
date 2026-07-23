class PlanningError(Exception):
    """Base domain exception for planning operations."""
    pass

class RiskValidationError(PlanningError):
    def __init__(self, issues: list):
        super().__init__(f"Planning blocked by risk engine: {len(issues)} issue(s) detected.")
        self.issues = issues

class ReplanNotAllowedError(PlanningError):
    def __init__(self, campaign_id: str, reason: str):
        super().__init__(f"Replan not allowed for campaign '{campaign_id}': {reason}")
        self.campaign_id = campaign_id
        self.reason = reason
