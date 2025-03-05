# app/db/models.py
from sqlalchemy import Column, String, ForeignKey, Date, Boolean, DateTime, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True)  # UUID length
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    department_id = Column(String(36), ForeignKey("departments.id"))
    role_id = Column(String(36), ForeignKey("roles.id"))
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    joining_date = Column(Date, default=datetime.utcnow)
    status = Column(String(20), default="active")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    subordinates = relationship("User", 
                              backref="manager", 
                              remote_side=[id])
    leaves = relationship("Leave", back_populates="user")
    attendance = relationship("Attendance", back_populates="user")
    

class Department(Base):
    __tablename__ = "departments"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="department")

class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")

class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(String(36), primary_key=True, index=True)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="role_permissions")

class Leave(Base):
    __tablename__ = "leaves"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    leave_type = Column(String(50), nullable=False)  # annual, sick, etc.
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    reason = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    leave_type_id = Column(String(36), ForeignKey("leave_types.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="leaves")
    leave_type = relationship("LeaveType", back_populates="leaves")  # Add this line

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    status = Column(String(20))  # present, absent, half-day
    work_hours = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="attendance")


class LeaveType(Base):
    __tablename__ = "leave_types"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    default_days = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    leaves = relationship("Leave", back_populates="leave_type")

class LeaveBalance(Base):
    __tablename__ = "leave_balances"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    leave_type_id = Column(String(36), ForeignKey("leave_types.id"), nullable=False)
    year = Column(Integer, nullable=False)
    total_days = Column(Integer, default=0)
    used_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="leave_balances")
    leave_type = relationship("LeaveType")

# Update User model to include leave balances
User.leave_balances = relationship("LeaveBalance", back_populates="user")







class Salary(Base):
    __tablename__ = "salaries"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    basic_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0)
    deductions = Column(Float, default=0)
    gross_salary = Column(Float, nullable=False)
    net_salary = Column(Float, nullable=False)
    effective_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="salaries")

class Payslip(Base):
    __tablename__ = "payslips"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    basic_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0)
    deductions = Column(Float, default=0)
    gross_salary = Column(Float, nullable=False)
    net_salary = Column(Float, nullable=False)
    tax_deducted = Column(Float, default=0)
    status = Column(String(20), default="draft")  # draft, generated, approved
    generated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="payslips")

class TaxInfo(Base):
    __tablename__ = "tax_info"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True)
    pan_number = Column(String(10))
    tax_regime = Column(String(20))  # old, new
    tax_declarations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="tax_info")

# Update User model to include relationships
User.salaries = relationship("Salary", back_populates="user")
User.payslips = relationship("Payslip", back_populates="user")
User.tax_info = relationship("TaxInfo", back_populates="user", uselist=False)


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    duration = Column(Integer)  # in hours
    category = Column(String(100))
    status = Column(String(20), default="active")  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship only once here
    enrollments = relationship("CourseEnrollment", back_populates="course")

class CourseEnrollment(Base):
    __tablename__ = "course_enrollments"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    course_id = Column(String(36), ForeignKey("courses.id"), nullable=False)
    status = Column(String(20), default="enrolled")  # enrolled, completed, dropped
    assigned_by = Column(String(36), ForeignKey("users.id"))
    completion_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Just define these relationships - remove the Course.enrollments line
User.enrollments = relationship("CourseEnrollment", foreign_keys=[CourseEnrollment.user_id], back_populates="user")
CourseEnrollment.user = relationship("User", foreign_keys=[CourseEnrollment.user_id], back_populates="enrollments")
CourseEnrollment.assigner = relationship("User", foreign_keys=[CourseEnrollment.assigned_by])

class CertificationType(Base):
    __tablename__ = "certification_types"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    issuing_organization = Column(String(200))
    validity_period = Column(Integer)  # in months
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    certifications = relationship("EmployeeCertification", back_populates="certification_type")

class EmployeeCertification(Base):
    __tablename__ = "employee_certifications"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    certification_type_id = Column(String(36), ForeignKey("certification_types.id"), nullable=False)
    certification_number = Column(String(100))
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    status = Column(String(20), default="active")  # active, expired, revoked
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="certifications")
    certification_type = relationship("CertificationType", back_populates="certifications")

# Update User model to include certifications relationship
User.certifications = relationship("EmployeeCertification", back_populates="user")



class OnboardingTask(Base):
    __tablename__ = "onboarding_tasks"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    department_id = Column(String(36), ForeignKey("departments.id"))
    role_id = Column(String(36), ForeignKey("roles.id"))
    priority = Column(String(20), default="medium")  # low, medium, high
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department")
    role = relationship("Role")

class OffboardingTask(Base):
    __tablename__ = "offboarding_tasks"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    department_id = Column(String(36), ForeignKey("departments.id"))
    priority = Column(String(20), default="medium")  # low, medium, high
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = relationship("Department")

class EmployeeOnboarding(Base):
    __tablename__ = "employee_onboarding"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("onboarding_tasks.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    completed_at = Column(DateTime)
    notes = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="onboarding_tasks")
    task = relationship("OnboardingTask")

class EmployeeOffboarding(Base):
    __tablename__ = "employee_offboarding"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("offboarding_tasks.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, in_progress, completed
    completed_at = Column(DateTime)
    notes = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="offboarding_tasks")
    task = relationship("OffboardingTask")

# Update User model to include relationships
User.onboarding_tasks = relationship("EmployeeOnboarding", back_populates="user")
User.offboarding_tasks = relationship("EmployeeOffboarding", back_populates="user")


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(2000))
    category = Column(String(100))  # HR, IT, Security, etc.
    version = Column(String(20))
    effective_date = Column(Date)
    status = Column(String(20), default="draft")  # draft, active, archived
    is_mandatory = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    acknowledgments = relationship("PolicyAcknowledgment", back_populates="policy")

class PolicyAcknowledgment(Base):
    __tablename__ = "policy_acknowledgments"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    policy_id = Column(String(36), ForeignKey("policies.id"), nullable=False)
    acknowledged_at = Column(DateTime, nullable=False)
    version_acknowledged = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="policy_acknowledgments")
    policy = relationship("Policy", back_populates="acknowledgments")

# Update User model to include policy acknowledgments
User.policy_acknowledgments = relationship("PolicyAcknowledgment", back_populates="user")


class Benefit(Base):
    __tablename__ = "benefits"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    type = Column(String(50))  # health, insurance, allowance, etc.
    amount = Column(Float)  # monetary value if applicable
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee_benefits = relationship("EmployeeBenefit", back_populates="benefit")

class EmployeeBenefit(Base):
    __tablename__ = "employee_benefits"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    benefit_id = Column(String(36), ForeignKey("benefits.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    status = Column(String(20), default="active")  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="benefits")
    benefit = relationship("Benefit", back_populates="employee_benefits")

# Update User model to include benefits relationship
User.benefits = relationship("EmployeeBenefit", back_populates="user")



class PerformanceRating(Base):
    __tablename__ = "performance_ratings"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    rated_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    rating = Column(Float, nullable=False)  # 1-5 scale
    category = Column(String(50))  # technical, soft skills, leadership, etc.
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    comments = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="ratings")
    rater = relationship("User", foreign_keys=[rated_by])

class PerformanceReview(Base):
    __tablename__ = "performance_reviews"

    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reviewer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    review_period = Column(String(50))  # Q1-2023, H1-2023, etc.
    overall_rating = Column(Float)
    achievements = Column(String(2000))
    areas_of_improvement = Column(String(1000))
    goals = Column(String(1000))
    status = Column(String(20), default="draft")  # draft, submitted, approved
    submitted_at = Column(DateTime)
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id])

# Update User model to include relationships
User.ratings = relationship("PerformanceRating", foreign_keys=[PerformanceRating.user_id], back_populates="user")
User.reviews = relationship("PerformanceReview", foreign_keys=[PerformanceReview.user_id], back_populates="user")




class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    client_name = Column(String(200))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20), default="active")  # active, completed, on_hold, cancelled
    priority = Column(String(20), default="medium")  # low, medium, high
    budget = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    assignments = relationship("ProjectAssignment", back_populates="project")

class ProjectAssignment(Base):
    __tablename__ = "project_assignments"

    id = Column(String(36), primary_key=True, index=True)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role = Column(String(50))  # project_manager, team_lead, developer, etc.
    assigned_by = Column(String(36), ForeignKey("users.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    allocation_percentage = Column(Integer, default=100)  # time allocation in percentage
    status = Column(String(20), default="active")  # active, completed, removed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="assignments")
    user = relationship("User", foreign_keys=[user_id], back_populates="project_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])

# Update User model to include project assignments
User.project_assignments = relationship("ProjectAssignment", foreign_keys=[ProjectAssignment.user_id], back_populates="user")