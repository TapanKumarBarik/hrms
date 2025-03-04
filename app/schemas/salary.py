# app/schemas/salary.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class SalaryBase(BaseModel):
    basic_salary: float
    allowances: float = 0
    deductions: float = 0
    effective_date: date

class SalaryCreate(SalaryBase):
    user_id: str

class SalaryUpdate(BaseModel):
    basic_salary: Optional[float] = None
    allowances: Optional[float] = None
    deductions: Optional[float] = None
    effective_date: Optional[date] = None

class SalaryResponse(SalaryBase):
    id: str
    gross_salary: float
    net_salary: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class PayslipBase(BaseModel):
    month: int
    year: int

class PayslipCreate(PayslipBase):
    user_id: str

class PayslipResponse(PayslipBase):
    id: str
    basic_salary: float
    allowances: float
    deductions: float
    gross_salary: float
    net_salary: float
    tax_deducted: float
    status: str
    generated_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TaxInfoBase(BaseModel):
    pan_number: str
    tax_regime: str
    tax_declarations: dict

class TaxInfoCreate(TaxInfoBase):
    user_id: str

class TaxInfoUpdate(BaseModel):
    pan_number: Optional[str] = None
    tax_regime: Optional[str] = None
    tax_declarations: Optional[dict] = None

class TaxInfoResponse(TaxInfoBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True