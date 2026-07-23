class CampaignError(Exception):
    """Base domain exception for campaign operations."""
    pass

class CampaignNotFoundError(CampaignError):
    def __init__(self, campaign_id: str):
        super().__init__(f"Campaign '{campaign_id}' was not found.")
        self.campaign_id = campaign_id

class InvalidStateTransitionError(CampaignError):
    def __init__(self, from_state: str, to_state: str, reason: str = ""):
        super().__init__(f"Invalid campaign state transition from '{from_state}' to '{to_state}'. {reason}".strip())
        self.from_state = from_state
        self.to_state = to_state

class DuplicateCampaignError(CampaignError):
    def __init__(self, duplicate_type: str, duplicate_key: str, existing_campaign_id: str):
        super().__init__(f"Duplicate campaign blocked [{duplicate_type}]: '{duplicate_key}'. Existing campaign: '{existing_campaign_id}'.")
        self.duplicate_type = duplicate_type
        self.duplicate_key = duplicate_key
        self.existing_campaign_id = existing_campaign_id

class ConcurrencyConflictError(CampaignError):
    def __init__(self, campaign_id: str, expected_version: int):
        super().__init__(f"Optimistic concurrency conflict on campaign '{campaign_id}' (expected version {expected_version}).")
        self.campaign_id = campaign_id
        self.expected_version = expected_version
