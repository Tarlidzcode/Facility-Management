"""Utility helpers for presence tracking (occupancy counts).

Provides lightweight functions to compute current employees in office and
total employees, reusing existing PresenceLog and PresenceStatus models.
Separated to avoid duplicating logic across multiple endpoints (login portal
and safety routes).
"""
from typing import Dict
from sqlalchemy import desc

from models import db, Employee, PresenceLog, PresenceStatus, SafetyVisitor


def get_current_presence_summary(include_visitors: bool = True) -> Dict[str, int]:
    """Return a summary of current presence counts.

    Counts employees whose latest PresenceLog status is IN. Optionally includes
    active visitors (status == 'checked_in').

    Returns dict with keys:
      employees_in_office: number of employees currently IN
      total_employees: total active employees (with user accounts) in DB
      visitors_in_office: number of active checked-in visitors (only if include_visitors)
      total_in_office: employees_in_office + visitors_in_office (only if include_visitors)
    """
    # Query all active employees that have a linked user account
    employees = (db.session.query(Employee)
                 .filter(Employee.status == 'active')
                 .all())

    employees_in = 0
    for employee in employees:
        if not employee.user_id:
            continue
        latest_log = (PresenceLog.query
                       .filter_by(user_id=employee.user_id)
                       .order_by(PresenceLog.created_at.desc())
                       .first())
        if latest_log and latest_log.status == PresenceStatus.IN:
            employees_in += 1

    total_employees = len([e for e in employees if e.user_id])

    summary = {
        'employees_in_office': employees_in,
        'total_employees': total_employees,
    }

    if include_visitors:
        visitors_in = SafetyVisitor.query.filter_by(status='checked_in').count()
        summary['visitors_in_office'] = visitors_in
        summary['total_in_office'] = employees_in + visitors_in

    return summary
