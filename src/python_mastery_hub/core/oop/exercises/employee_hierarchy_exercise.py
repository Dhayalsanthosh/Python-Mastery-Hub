"""
Employee Hierarchy exercise for the OOP module.
Design an inheritance-based employee management system.
"""

from typing import Dict, Any


def get_employee_hierarchy_exercise() -> Dict[str, Any]:
    """Get the Employee Hierarchy exercise."""
    return {
        "title": "Employee Hierarchy System",
        "difficulty": "medium",
        "estimated_time": "1.5-2 hours",
        "instructions": """
Design a comprehensive employee management system using inheritance to model
different types of employees with varying responsibilities, benefits, and
compensation structures.

This exercise focuses on inheritance, method overriding, and polymorphism
to create a realistic employee hierarchy system.
""",
        "learning_objectives": [
            "Apply inheritance to model real-world hierarchies",
            "Practice method overriding for specialized behavior",
            "Implement polymorphic methods for different employee types",
            "Use super() to extend parent class functionality",
            "Design class hierarchies with proper abstraction"
        ],
        "tasks": [
            {
                "step": 1,
                "title": "Create Base Employee Class",
                "description": "Design the foundation Employee class",
                "requirements": [
                    "Store employee ID, name, department, hire date, base salary",
                    "Implement calculate_pay() method for basic salary calculation",
                    "Add get_employee_info() method for employee details",
                    "Include years_of_service() method using hire date"
                ]
            },
            {
                "step": 2,
                "title": "Create Manager Class",
                "description": "Design Manager class inheriting from Employee",
                "requirements": [
                    "Add team_size and direct_reports list",
                    "Override calculate_pay() to include management bonus",
                    "Add methods to add/remove team members",
                    "Implement performance review methods for team"
                ]
            },
            {
                "step": 3,
                "title": "Create Developer Class",
                "description": "Design Developer class with programming skills",
                "requirements": [
                    "Add programming_languages list and skill_level",
                    "Override calculate_pay() to include skill bonuses",
                    "Add methods to add/update programming skills",
                    "Implement code review and project assignment methods"
                ]
            },
            {
                "step": 4,
                "title": "Create SalesRep Class",
                "description": "Design SalesRep class with commission structure",
                "requirements": [
                    "Add sales_target, sales_achieved, commission_rate",
                    "Override calculate_pay() to include commission",
                    "Add methods to record sales and track performance",
                    "Implement quota achievement calculation"
                ]
            },
            {
                "step": 5,
                "title": "Create Company Class",
                "description": "Design Company class to manage all employees",
                "requirements": [
                    "Maintain employee roster with polymorphic operations",
                    "Implement payroll calculation for all employee types",
                    "Add employee search and filtering methods",
                    "Generate company-wide reports and statistics"
                ]
            }
        ],
        "starter_code": '''
from datetime import datetime, date
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

class Employee:
    """Base employee class."""
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float):
        # TODO: Implement initialization with validation
        pass
    
    def calculate_pay(self) -> float:
        """Calculate total pay for the employee."""
        # TODO: Implement basic pay calculation
        pass
    
    def years_of_service(self) -> float:
        """Calculate years of service."""
        # TODO: Calculate years from hire date to now
        pass
    
    def get_employee_info(self) -> Dict[str, Any]:
        """Get comprehensive employee information."""
        # TODO: Return dictionary with employee details
        pass
    
    def __str__(self) -> str:
        # TODO: Return readable string representation
        pass

class Manager(Employee):
    """Manager class with team management capabilities."""
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float, team_size: int = 0):
        # TODO: Initialize Manager with team management features
        pass
    
    def calculate_pay(self) -> float:
        """Calculate pay including management bonus."""
        # TODO: Override to include management bonus
        pass
    
    def add_team_member(self, employee: Employee) -> str:
        """Add employee to direct reports."""
        # TODO: Implement team member addition
        pass
    
    def remove_team_member(self, employee_id: str) -> str:
        """Remove employee from direct reports."""
        # TODO: Implement team member removal
        pass

class Developer(Employee):
    """Developer class with programming skills."""
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float, 
                 programming_languages: List[str] = None, skill_level: str = "Junior"):
        # TODO: Initialize Developer with programming skills
        pass
    
    def calculate_pay(self) -> float:
        """Calculate pay including skill bonuses."""
        # TODO: Override to include skill-based bonuses
        pass
    
    def add_programming_language(self, language: str) -> str:
        """Add a programming language skill."""
        # TODO: Implement skill addition
        pass
    
    def update_skill_level(self, new_level: str) -> str:
        """Update developer skill level."""
        # TODO: Implement skill level update
        pass

class SalesRep(Employee):
    """Sales representative with commission structure."""
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float, 
                 sales_target: float, commission_rate: float = 0.05):
        # TODO: Initialize SalesRep with sales tracking
        pass
    
    def calculate_pay(self) -> float:
        """Calculate pay including commission."""
        # TODO: Override to include commission calculation
        pass
    
    def record_sale(self, amount: float) -> str:
        """Record a sale."""
        # TODO: Implement sale recording
        pass
    
    def get_quota_achievement(self) -> float:
        """Get quota achievement percentage."""
        # TODO: Calculate percentage of target achieved
        pass

class Company:
    """Company class to manage all employees."""
    
    def __init__(self, name: str):
        # TODO: Initialize company with employee management
        pass
    
    def hire_employee(self, employee: Employee) -> str:
        """Hire a new employee."""
        # TODO: Implement employee hiring
        pass
    
    def fire_employee(self, employee_id: str) -> str:
        """Fire an employee."""
        # TODO: Implement employee termination
        pass
    
    def calculate_total_payroll(self) -> float:
        """Calculate total payroll for all employees."""
        # TODO: Use polymorphism to calculate total payroll
        pass
    
    def get_employees_by_department(self, department: str) -> List[Employee]:
        """Get all employees in a department."""
        # TODO: Implement department filtering
        pass

# Test your implementation
if __name__ == "__main__":
    # Create company
    company = Company("TechCorp Inc.")
    
    # Create employees of different types
    manager = Manager("M001", "Alice Smith", "Engineering", 
                     date(2020, 1, 15), 90000, team_size=5)
    
    developer = Developer("D001", "Bob Jones", "Engineering", 
                         date(2021, 3, 10), 75000, 
                         ["Python", "JavaScript"], "Senior")
    
    sales_rep = SalesRep("S001", "Carol Brown", "Sales", 
                        date(2022, 6, 1), 50000, 
                        sales_target=100000, commission_rate=0.08)
    
    # Hire employees
    print(company.hire_employee(manager))
    print(company.hire_employee(developer))
    print(company.hire_employee(sales_rep))
    
    # Test polymorphic payroll calculation
    print(f"Total payroll: ${company.calculate_total_payroll():,.2f}")
''',
        "hints": [
            "Use super() to call parent class methods and extend functionality",
            "Consider using class variables for skill level multipliers",
            "Implement validation in constructors for realistic constraints",
            "Use polymorphism in Company class - all employees should work the same way",
            "Think about edge cases: negative salaries, invalid dates, etc.",
            "Consider using enums for fixed values like skill levels",
            "Make calculate_pay() work differently for each employee type"
        ],
        "solution": '''
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from enum import Enum

class SkillLevel(Enum):
    """Enumeration for developer skill levels."""
    JUNIOR = "Junior"
    MID = "Mid"
    SENIOR = "Senior"
    LEAD = "Lead"
    PRINCIPAL = "Principal"

class Employee:
    """Base employee class with common functionality."""
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float):
        if not employee_id or not employee_id.strip():
            raise ValueError("Employee ID cannot be empty")
        if not name or not name.strip():
            raise ValueError("Employee name cannot be empty")
        if not department or not department.strip():
            raise ValueError("Department cannot be empty")
        if hire_date > date.today():
            raise ValueError("Hire date cannot be in the future")
        if base_salary < 0:
            raise ValueError("Base salary cannot be negative")
        
        self.employee_id = employee_id.strip()
        self.name = name.strip()
        self.department = department.strip()
        self.hire_date = hire_date
        self.base_salary = base_salary
        self.is_active = True
    
    def calculate_pay(self) -> float:
        """Calculate total pay for the employee."""
        if not self.is_active:
            return 0.0
        
        # Base monthly salary
        monthly_salary = self.base_salary / 12
        
        # Add years of service bonus (1% per year, max 10%)
        years = self.years_of_service()
        service_bonus = min(years * 0.01, 0.10) * monthly_salary
        
        return monthly_salary + service_bonus
    
    def years_of_service(self) -> float:
        """Calculate years of service."""
        if not self.is_active:
            return 0.0
        
        today = date.today()
        service_days = (today - self.hire_date).days
        return round(service_days / 365.25, 2)  # Account for leap years
    
    def get_employee_info(self) -> Dict[str, Any]:
        """Get comprehensive employee information."""
        return {
            'employee_id': self.employee_id,
            'name': self.name,
            'department': self.department,
            'hire_date': self.hire_date.isoformat(),
            'base_salary': self.base_salary,
            'years_of_service': self.years_of_service(),
            'monthly_pay': self.calculate_pay(),
            'annual_pay': self.calculate_pay() * 12,
            'is_active': self.is_active,
            'employee_type': self.__class__.__name__
        }
    
    def terminate(self) -> str:
        """Terminate employee."""
        if not self.is_active:
            return f"Employee {self.name} is already terminated"
        
        self.is_active = False
        return f"Employee {self.name} has been terminated"
    
    def __str__(self) -> str:
        status = "Active" if self.is_active else "Terminated"
        return f"{self.name} ({self.employee_id}) - {self.department} - {status}"
    
    def __repr__(self) -> str:
        return f"Employee('{self.employee_id}', '{self.name}', '{self.department}', {self.hire_date!r}, {self.base_salary})"

class Manager(Employee):
    """Manager class with team management capabilities."""
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float, team_size: int = 0):
        super().__init__(employee_id, name, department, hire_date, base_salary)
        self.team_size = max(0, team_size)
        self.direct_reports: List[Employee] = []
        self.management_bonus_rate = 0.15  # 15% management bonus
    
    def calculate_pay(self) -> float:
        """Calculate pay including management bonus."""
        base_pay = super().calculate_pay()
        
        if not self.is_active:
            return 0.0
        
        # Management bonus based on team size
        management_bonus = base_pay * self.management_bonus_rate
        
        # Additional bonus for large teams
        if len(self.direct_reports) > 10:
            management_bonus *= 1.2
        elif len(self.direct_reports) > 5:
            management_bonus *= 1.1
        
        return base_pay + management_bonus
    
    def add_team_member(self, employee: Employee) -> str:
        """Add employee to direct reports."""
        if not isinstance(employee, Employee):
            return "Invalid employee object"
        
        if employee.employee_id == self.employee_id:
            return "Manager cannot report to themselves"
        
        if employee in self.direct_reports:
            return f"{employee.name} is already a direct report"
        
        self.direct_reports.append(employee)
        self.team_size = len(self.direct_reports)
        return f"Added {employee.name} to {self.name}'s team"
    
    def remove_team_member(self, employee_id: str) -> str:
        """Remove employee from direct reports."""
        for employee in self.direct_reports:
            if employee.employee_id == employee_id:
                self.direct_reports.remove(employee)
                self.team_size = len(self.direct_reports)
                return f"Removed {employee.name} from {self.name}'s team"
        
        return f"Employee with ID {employee_id} not found in team"
    
    def get_team_info(self) -> Dict[str, Any]:
        """Get comprehensive team information."""
        team_payroll = sum(emp.calculate_pay() * 12 for emp in self.direct_reports)
        return {
            'manager': self.name,
            'team_size': len(self.direct_reports),
            'direct_reports': [emp.name for emp in self.direct_reports],
            'team_annual_payroll': team_payroll,
            'departments_managed': list(set(emp.department for emp in self.direct_reports))
        }
    
    def conduct_team_review(self) -> List[Dict[str, Any]]:
        """Conduct performance review for all team members."""
        reviews = []
        for employee in self.direct_reports:
            review = {
                'employee': employee.name,
                'employee_id': employee.employee_id,
                'years_of_service': employee.years_of_service(),
                'current_salary': employee.base_salary,
                'performance_rating': 'Satisfactory',  # Simplified
                'recommended_raise': employee.base_salary * 0.03  # 3% raise
            }
            reviews.append(review)
        return reviews

class Developer(Employee):
    """Developer class with programming skills and technical expertise."""
    
    SKILL_MULTIPLIERS = {
        SkillLevel.JUNIOR: 1.0,
        SkillLevel.MID: 1.15,
        SkillLevel.SENIOR: 1.35,
        SkillLevel.LEAD: 1.55,
        SkillLevel.PRINCIPAL: 1.80
    }
    
    LANGUAGE_BONUSES = {
        'Python': 500,
        'JavaScript': 400,
        'Java': 600,
        'C++': 700,
        'Go': 800,
        'Rust': 900,
        'TypeScript': 450,
        'Swift': 650,
        'Kotlin': 550
    }
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float, 
                 programming_languages: List[str] = None, 
                 skill_level: str = "Junior"):
        super().__init__(employee_id, name, department, hire_date, base_salary)
        self.programming_languages = programming_languages or []
        
        # Convert string to enum
        if isinstance(skill_level, str):
            try:
                self.skill_level = SkillLevel(skill_level)
            except ValueError:
                self.skill_level = SkillLevel.JUNIOR
        else:
            self.skill_level = skill_level
        
        self.projects_completed = 0
        self.code_reviews_done = 0
    
    def calculate_pay(self) -> float:
        """Calculate pay including skill bonuses."""
        base_pay = super().calculate_pay()
        
        if not self.is_active:
            return 0.0
        
        # Apply skill level multiplier
        skill_multiplier = self.SKILL_MULTIPLIERS[self.skill_level]
        skill_adjusted_pay = base_pay * skill_multiplier
        
        # Language bonuses (monthly)
        language_bonus = 0
        for lang in self.programming_languages:
            language_bonus += self.LANGUAGE_BONUSES.get(lang, 0) / 12  # Monthly bonus
        
        # Project completion bonus
        project_bonus = self.projects_completed * 100  # $100 per completed project
        
        return skill_adjusted_pay + language_bonus + project_bonus
    
    def add_programming_language(self, language: str) -> str:
        """Add a programming language skill."""
        if not language or not language.strip():
            return "Language name cannot be empty"
        
        language = language.strip()
        if language in self.programming_languages:
            return f"{language} is already in skill set"
        
        self.programming_languages.append(language)
        return f"Added {language} to {self.name}'s skills"
    
    def update_skill_level(self, new_level: str) -> str:
        """Update developer skill level."""
        try:
            new_skill_level = SkillLevel(new_level)
            old_level = self.skill_level.value
            self.skill_level = new_skill_level
            return f"Updated {self.name}'s skill level from {old_level} to {new_level}"
        except ValueError:
            valid_levels = [level.value for level in SkillLevel]
            return f"Invalid skill level. Valid levels: {valid_levels}"
    
    def complete_project(self) -> str:
        """Mark a project as completed."""
        self.projects_completed += 1
        return f"{self.name} completed project #{self.projects_completed}"
    
    def perform_code_review(self) -> str:
        """Record a code review."""
        self.code_reviews_done += 1
        return f"{self.name} completed code review #{self.code_reviews_done}"
    
    def get_technical_info(self) -> Dict[str, Any]:
        """Get technical information about the developer."""
        return {
            'programming_languages': self.programming_languages,
            'skill_level': self.skill_level.value,
            'projects_completed': self.projects_completed,
            'code_reviews_done': self.code_reviews_done,
            'language_bonuses': {lang: self.LANGUAGE_BONUSES.get(lang, 0) 
                               for lang in self.programming_languages}
        }

class SalesRep(Employee):
    """Sales representative with commission structure."""
    
    def __init__(self, employee_id: str, name: str, department: str, 
                 hire_date: date, base_salary: float, 
                 sales_target: float, commission_rate: float = 0.05):
        super().__init__(employee_id, name, department, hire_date, base_salary)
        self.sales_target = max(0, sales_target)
        self.commission_rate = max(0, min(1, commission_rate))  # 0-100%
        self.sales_achieved = 0.0
        self.sales_history: List[Dict[str, Any]] = []
    
    def calculate_pay(self) -> float:
        """Calculate pay including commission."""
        base_pay = super().calculate_pay()
        
        if not self.is_active:
            return 0.0
        
        # Monthly commission on sales achieved
        monthly_commission = (self.sales_achieved / 12) * self.commission_rate
        
        # Bonus for exceeding targets
        quota_achievement = self.get_quota_achievement()
        if quota_achievement > 100:
            # 10% bonus for exceeding quota
            excess_bonus = base_pay * 0.10 * ((quota_achievement - 100) / 100)
            monthly_commission += excess_bonus
        
        return base_pay + monthly_commission
    
    def record_sale(self, amount: float, client_name: str = "Unknown") -> str:
        """Record a sale."""
        if amount <= 0:
            return "Sale amount must be positive"
        
        self.sales_achieved += amount
        sale_record = {
            'amount': amount,
            'client': client_name,
            'date': date.today().isoformat(),
            'rep_id': self.employee_id
        }
        self.sales_history.append(sale_record)
        
        return f"Recorded ${amount:,.2f} sale by {self.name}. Total sales: ${self.sales_achieved:,.2f}"
    
    def get_quota_achievement(self) -> float:
        """Get quota achievement percentage."""
        if self.sales_target == 0:
            return 100.0
        return round((self.sales_achieved / self.sales_target) * 100, 2)
    
    def reset_sales_period(self) -> str:
        """Reset sales for new period (e.g., quarterly)."""
        old_sales = self.sales_achieved
        self.sales_achieved = 0.0
        return f"Reset sales period. Previous sales: ${old_sales:,.2f}"
    
    def get_sales_info(self) -> Dict[str, Any]:
        """Get comprehensive sales information."""
        return {
            'sales_target': self.sales_target,
            'sales_achieved': self.sales_achieved,
            'quota_achievement': f"{self.get_quota_achievement()}%",
            'commission_rate': f"{self.commission_rate * 100}%",
            'total_sales_transactions': len(self.sales_history),
            'average_sale_amount': (self.sales_achieved / len(self.sales_history) 
                                  if self.sales_history else 0)
        }

class Company:
    """Company class to manage all employees polymorphically."""
    
    def __init__(self, name: str):
        if not name or not name.strip():
            raise ValueError("Company name cannot be empty")
        
        self.name = name.strip()
        self.employees: Dict[str, Employee] = {}
        self.departments: set = set()
        self.payroll_history: List[Dict[str, Any]] = []
    
    def hire_employee(self, employee: Employee) -> str:
        """Hire a new employee."""
        if not isinstance(employee, Employee):
            return "Invalid employee object"
        
        if employee.employee_id in self.employees:
            return f"Employee with ID {employee.employee_id} already exists"
        
        self.employees[employee.employee_id] = employee
        self.departments.add(employee.department)
        
        return f"Successfully hired {employee.name} as {employee.__class__.__name__} in {employee.department}"
    
    def fire_employee(self, employee_id: str) -> str:
        """Fire an employee."""
        if employee_id not in self.employees:
            return f"Employee with ID {employee_id} not found"
        
        employee = self.employees[employee_id]
        termination_message = employee.terminate()
        
        # Remove from any manager's direct reports
        for emp in self.employees.values():
            if isinstance(emp, Manager):
                emp.remove_team_member(employee_id)
        
        return f"Fired {employee.name}. {termination_message}"
    
    def calculate_total_payroll(self) -> float:
        """Calculate total monthly payroll for all active employees."""
        total = 0.0
        for employee in self.employees.values():
            if employee.is_active:
                total += employee.calculate_pay()
        return total
    
    def get_employees_by_department(self, department: str) -> List[Employee]:
        """Get all active employees in a department."""
        return [emp for emp in self.employees.values() 
                if emp.department.lower() == department.lower() and emp.is_active]
    
    def get_employees_by_type(self, employee_type: type) -> List[Employee]:
        """Get all employees of a specific type."""
        return [emp for emp in self.employees.values() 
                if isinstance(emp, employee_type) and emp.is_active]
    
    def generate_payroll_report(self) -> Dict[str, Any]:
        """Generate comprehensive payroll report."""
        active_employees = [emp for emp in self.employees.values() if emp.is_active]
        
        if not active_employees:
            return {"message": "No active employees"}
        
        total_payroll = self.calculate_total_payroll()
        annual_payroll = total_payroll * 12
        
        # Breakdown by employee type
        type_breakdown = {}
        for emp in active_employees:
            emp_type = emp.__class__.__name__
            if emp_type not in type_breakdown:
                type_breakdown[emp_type] = {'count': 0, 'payroll': 0}
            type_breakdown[emp_type]['count'] += 1
            type_breakdown[emp_type]['payroll'] += emp.calculate_pay()
        
        # Department breakdown
        dept_breakdown = {}
        for dept in self.departments:
            dept_employees = self.get_employees_by_department(dept)
            if dept_employees:
                dept_payroll = sum(emp.calculate_pay() for emp in dept_employees)
                dept_breakdown[dept] = {
                    'employee_count': len(dept_employees),
                    'monthly_payroll': dept_payroll
                }
        
        return {
            'company': self.name,
            'total_employees': len(active_employees),
            'monthly_payroll': total_payroll,
            'annual_payroll': annual_payroll,
            'average_monthly_salary': total_payroll / len(active_employees),
            'employee_type_breakdown': type_breakdown,
            'department_breakdown': dept_breakdown,
            'departments': list(self.departments)
        }
    
    def promote_employee(self, employee_id: str, new_salary: float, 
                        new_title: str = None) -> str:
        """Promote an employee with salary increase."""
        if employee_id not in self.employees:
            return f"Employee with ID {employee_id} not found"
        
        employee = self.employees[employee_id]
        if not employee.is_active:
            return f"Cannot promote terminated employee {employee.name}"
        
        old_salary = employee.base_salary
        employee.base_salary = new_salary
        
        promotion_msg = f"Promoted {employee.name}: ${old_salary:,.2f} → ${new_salary:,.2f}"
        
        # Special handling for developers
        if isinstance(employee, Developer) and new_title:
            try:
                employee.update_skill_level(new_title)
                promotion_msg += f" (Level: {new_title})"
            except:
                pass
        
        return promotion_msg
    
    def __str__(self) -> str:
        active_count = len([emp for emp in self.employees.values() if emp.is_active])
        return f"{self.name}: {active_count} active employees across {len(self.departments)} departments"

# Comprehensive demonstration
def demonstrate_employee_system():
    """Demonstrate the complete employee hierarchy system."""
    print("=== Employee Hierarchy System Demo ===\\n")
    
    # Create company
    company = Company("TechCorp Innovations")
    print(f"Created company: {company}")
    
    # Create employees of different types
    print("\\n--- Hiring Employees ---")
    
    # Managers
    cto = Manager("M001", "Sarah Chen", "Engineering", 
                  date(2019, 1, 15), 120000, team_size=15)
    sales_manager = Manager("M002", "Mike Rodriguez", "Sales", 
                           date(2020, 3, 10), 95000, team_size=8)
    
    # Developers
    senior_dev = Developer("D001", "Alex Kim", "Engineering", 
                          date(2020, 6, 1), 85000, 
                          ["Python", "JavaScript", "Go"], "Senior")
    junior_dev = Developer("D002", "Emma Davis", "Engineering", 
                          date(2022, 9, 15), 65000, 
                          ["Python", "React"], "Junior")
    lead_dev = Developer("D003", "James Wilson", "Engineering", 
                        date(2018, 4, 20), 95000, 
                        ["Java", "C++", "Python", "Rust"], "Lead")
    
    # Sales reps
    top_sales = SalesRep("S001", "Lisa Anderson", "Sales", 
                        date(2021, 2, 1), 55000, 
                        sales_target=150000, commission_rate=0.08)
    new_sales = SalesRep("S002", "David Brown", "Sales", 
                        date(2023, 1, 10), 45000, 
                        sales_target=100000, commission_rate=0.06)
    
    # Hire all employees
    employees = [cto, sales_manager, senior_dev, junior_dev, lead_dev, top_sales, new_sales]
    for emp in employees:
        print(f"  {company.hire_employee(emp)}")
    
    # Build management hierarchy
    print("\\n--- Building Management Structure ---")
    cto.add_team_member(senior_dev)
    cto.add_team_member(junior_dev)
    cto.add_team_member(lead_dev)
    sales_manager.add_team_member(top_sales)
    sales_manager.add_team_member(new_sales)
    
    print(f"  CTO team: {[emp.name for emp in cto.direct_reports]}")
    print(f"  Sales Manager team: {[emp.name for emp in sales_manager.direct_reports]}")
    
    # Record some sales
    print("\\n--- Recording Sales Performance ---")
    top_sales.record_sale(25000, "TechStart Inc")
    top_sales.record_sale(18000, "DataCorp LLC")
    top_sales.record_sale(32000, "CloudSystems")
    
    new_sales.record_sale(12000, "SmallBiz Co")
    new_sales.record_sale(8000, "LocalTech")
    
    print(f"  {top_sales.name}: ${top_sales.sales_achieved:,.2f} ({top_sales.get_quota_achievement()}% of target)")
    print(f"  {new_sales.name}: ${new_sales.sales_achieved:,.2f} ({new_sales.get_quota_achievement()}% of target)")
    
    # Developer activities
    print("\\n--- Developer Activities ---")
    senior_dev.complete_project()
    senior_dev.complete_project()
    senior_dev.perform_code_review()
    
    lead_dev.complete_project()
    lead_dev.add_programming_language("TypeScript")
    
    junior_dev.add_programming_language("TypeScript")
    junior_dev.complete_project()
    
    # Show polymorphic payroll calculation
    print("\\n--- Payroll Calculation (Polymorphism in Action) ---")
    for emp in employees:
        monthly_pay = emp.calculate_pay()
        print(f"  {emp.name} ({emp.__class__.__name__}): ${monthly_pay:,.2f}/month")
    
    # Generate comprehensive report
    print("\\n--- Company Report ---")
    report = company.generate_payroll_report()
    print(f"Total Monthly Payroll: ${report['monthly_payroll']:,.2f}")
    print(f"Total Annual Payroll: ${report['annual_payroll']:,.2f}")
    print(f"Average Monthly Salary: ${report['average_monthly_salary']:,.2f}")
    
    print("\\nEmployee Type Breakdown:")
    for emp_type, data in report['employee_type_breakdown'].items():
        print(f"  {emp_type}: {data['count']} employees, ${data['payroll']:,.2f}/month")
    
    print("\\nDepartment Breakdown:")
    for dept, data in report['department_breakdown'].items():
        print(f"  {dept}: {data['employee_count']} employees, ${data['monthly_payroll']:,.2f}/month")
    
    # Test promotions
    print("\\n--- Promotions ---")
    promotion_result = company.promote_employee("D002", 75000, "Mid")
    print(f"  {promotion_result}")
    
    # Test employee info
    print("\\n--- Detailed Employee Info ---")
    dev_info = senior_dev.get_employee_info()
    tech_info = senior_dev.get_technical_info()
    print(f"Senior Developer Info:")
    print(f"  Years of Service: {dev_info['years_of_service']}")
    print(f"  Annual Pay: ${dev_info['annual_pay']:,.2f}")
    print(f"  Programming Languages: {tech_info['programming_languages']}")
    print(f"  Projects Completed: {tech_info['projects_completed']}")
    
    sales_info = top_sales.get_sales_info()
    print(f"\\nTop Sales Rep Info:")
    print(f"  Quota Achievement: {sales_info['quota_achievement']}")
    print(f"  Average Sale: ${sales_info['average_sale_amount']:,.2f}")
    print(f"  Total Transactions: {sales_info['total_sales_transactions']}")
    
    print("\\n=== Demo Complete ===")

if __name__ == "__main__":
    demonstrate_employee_system()
'''
    }