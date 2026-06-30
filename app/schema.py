# app/schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Metadata(BaseModel):
    report_id: str = Field(description="Unique report ID.")
    schema_version: str = Field(description="Schema version.")
    hoa_name: str = Field(description="Name of the HOA.")

class OverallVerdict(BaseModel):
    verdict: str = Field(description="Overall verdict (e.g., CAUTION, APPROVED, WARNING).")
    verdict_reason: str = Field(description="Detailed reason for the overall verdict.")
    highest_urgency_risk_id: str = Field(description="ID of the highest urgency risk found.")
    total_financial_exposure: Optional[float] = Field(None, description="Total financial exposure, if calculated or explicitly mentioned.")

class Finding(BaseModel):
    risk_id: str = Field(description="Unique identifier for the risk finding (e.g. XR-1-1).")
    risk_category_id: str = Field(description="Category of the risk (e.g., financial, reserves, restrictions, legal).")
    label: Optional[str] = Field(None, description="Short label summarizing the risk.")
    urgency: str = Field(description="Urgency level (e.g., HIGH, MEDIUM, LOW).")
    finding: str = Field(description="Detailed description of the finding.")
    source_document: Optional[str] = Field(None, description="Source file name.")
    source_section: Optional[str] = Field(None, description="Section in the source document.")
    lender_flag: Optional[bool] = Field(None, description="True if this is a concern for mortgage lenders.")
    buyer_note: Optional[str] = Field(None, description="Plain English description of out-of-pocket cost impact.")

class Risks(BaseModel):
    findings: List[Finding] = Field(description="List of identified risk findings.")
    notable_absences: List[str] = Field(description="List of notable absences required by state regulations.")

class MonthlyFees(BaseModel):
    current_monthly_fee: Optional[float] = Field(None, description="Current monthly HOA fee amount.")
    source_document: Optional[str] = Field(None, description="Source document reference.")

class ReserveFund(BaseModel):
    has_reserve_study: Optional[bool] = Field(None, description="True if a reserve study exists.")
    current_percent_funded: Optional[float] = Field(None, description="Current funded percentage of reserve study.")
    shortfall_amount: Optional[float] = Field(None, description="Reserve study shortfall amount.")
    risk_id: Optional[str] = Field(None, description="Linked risk ID reference.")

class FinancialOutlook(BaseModel):
    monthly_fees: Optional[MonthlyFees] = Field(None, description="Details on monthly fees.")
    reserve_fund: Optional[ReserveFund] = Field(None, description="Details on reserve funding.")

class ActionItem(BaseModel):
    action_id: int = Field(description="Sequential ID of the action item.")
    priority: str = Field(description="Priority level (e.g., High, Medium, Low).")
    action: str = Field(description="Description of recommended action.")
    risk_id: str = Field(description="Linked risk ID reference.")

class HOAAuditReport(BaseModel):
    metadata: Metadata
    overall_verdict: OverallVerdict
    risks: Risks
    financial_outlook: Optional[FinancialOutlook] = Field(None)
    action_items: List[ActionItem]