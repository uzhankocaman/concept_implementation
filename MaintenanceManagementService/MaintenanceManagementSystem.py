import json
from collections import defaultdict
from queue import Queue
import os
import pickle
import numpy as np
import sqlite3
import random
import numpy as np
from datetime import datetime, timedelta, date
from collections import defaultdict
import requests
import pickle
import os
import logging
import sqlite3
import json
from queue import Queue
import pprint
from collections import defaultdict

from datetime import datetime
from typing import List
import logging
import pandas as pd
import queue
import random
import threading
import time

import random
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import requests
import pickle
import os
import logging

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from .monitoring import MonitoringUI

class PersonnelManager:
    """A class to manage personnel schedules and skills."""

    def __init__(self, initial_personnel):
        self.schedule = defaultdict(lambda: defaultdict(list))
        self.skills = defaultdict(set)

        for person in initial_personnel:
            self.schedule[person] = defaultdict(list)
            self.skills[person] = set()

    def add_task_to_personnel_calendar(self, person, scheduled_date, task):
        """Add a task to the personnel's calendar on a specific date."""
        if person in self.schedule:
            if isinstance(scheduled_date, date):
                self.schedule[person][scheduled_date].append(task)
            else:
                print(f"Invalid date format for task assignment.")
        else:
            print(f"Personnel '{person}' not found in the system.")

    def get_personnel_schedule(self, person, date=None):
        """Get the schedule for the personnel. If date is provided, get tasks for that specific date."""
        if person in self.schedule:
            if date:
                return self.schedule[person].get(date, [])
            return self.schedule[person]
        return defaultdict(list)

    def add_personnel_skills(self, person, skills):
        """Add or update skills for a person."""
        if person in self.skills:
            self.skills[person].update(skills)
        else:
            print(f"Personnel '{person}' not found in the system.")

    def person_has_required_skill(self, person, required_skill):
        """Check if the person has the required skills for a task."""
        return required_skill in self.skills.get(person, [])

    def is_personnel_available_on_date(self, person, date):
        """Check if the personnel is available on the specified date."""
        return len(self.schedule[person][date]) == 0


class InventoryManager:
    """A class to manage inventory, including checking levels and ordering new stock."""

    def __init__(self, parts_inventory, delivery_times):
        self.delivery_times = delivery_times
        self.parts_inventory = parts_inventory

    def get_inventory_level(self, part_name):
        """Return the current inventory level of the specified part."""
        return self.parts_inventory.get(part_name, 0)

    def order_new_inventory(self, part_name, quantity):
        """Order new inventory for a specific part."""
        if part_name in self.parts_inventory:
            self.parts_inventory[part_name] += quantity
        else:
            self.parts_inventory[part_name] = quantity
        print(f"Ordered {quantity} units of {part_name}.")

    def check_and_reorder_inventory(self):
        """Check inventory levels and reorder parts if necessary."""
        for part, quantity in self.parts_inventory.items():
            if quantity <= 0:
                reorder_quantity = self.determine_reorder_quantity(part)
                self.order_new_inventory(part, reorder_quantity)

    def determine_reorder_quantity(self, part_name):
        """Determine the quantity to reorder for a specific part."""
        quantity = {"fuel filter": 2, "battery": 1}
        return quantity[part_name]  # Example fixed reorder quantity

    def get_estimated_arrival_time(self, part_name):
        """Get the estimated arrival time for an ordered part."""
        days_to_arrival = self.delivery_times.get(part_name, 0)
        arrival_date = datetime.datetime.now() + datetime.timedelta(
            days=days_to_arrival
        )
        return arrival_date


class MaintenanceManagementService():
    def __init__(self):
        self.initialize_database()
        self.load_state()
        self.delivery_times = {"fuel filter": 2, "battery": 5}
        self.inventory_manager = InventoryManager(
            self.parts_inventory, self.delivery_times
        )
        #  self.delivery_times adjust code

        personnel = ["Technician1", "Technician2", "Engineer1", "Engineer2", "Engineer3"]
        self.personnel_system = PersonnelManager(personnel)
        self.personnel_system.add_personnel_skills("Technician1", {"replace"})
        self.personnel_system.add_personnel_skills("Technician2", {"replace"})
        self.personnel_system.add_personnel_skills("Engineer1", {"inspect", "repair"})
        self.personnel_system.add_personnel_skills("Engineer2", {"inspect", "repair"})
        self.personnel_system.add_personnel_skills("Engineer3", {"inspect", "repair"})

        self.reports = {}

    def load_state(self):
        """Load the state from an SQLite database."""
        conn = sqlite3.connect("maintenance_management.db")
        cursor = conn.cursor()

        try:
            # Load maintenance_required
            cursor.execute(
                "SELECT value FROM system_state WHERE key = 'maintenance_required'"
            )
            result = cursor.fetchone()
            self.maintenance_required = result[0] if result else True

            # Load constraints
            cursor.execute("SELECT value FROM system_state WHERE key = 'constraints'")
            result = cursor.fetchone()
            self.constraints = (
                json.loads(result[0]) if result else None
            )  # Default to 0 if not found

            # Load parts_inventory
            cursor.execute("SELECT part, quantity FROM parts_inventory")
            self.parts_inventory = {row[0]: row[1] for row in cursor.fetchall()}

            # Load personnel
            cursor.execute("SELECT name FROM personnel")
            self.personnel = [row[0] for row in cursor.fetchall()]

            # Load maintenance_tasks
            cursor.execute(
                "SELECT value FROM system_state WHERE key = 'maintenance_tasks'"
            )
            result = cursor.fetchone()
            self.maintenance_tasks = json.loads(result[0]) if result else []

            # Load advisories and task_queue
            cursor.execute("SELECT value FROM system_state WHERE key = 'advisories'")
            result = cursor.fetchone()
            advisories_list = json.loads(result[0]) if result else []
            self.advisories = Queue()
            for item in advisories_list:
                self.advisories.put(item)

            cursor.execute("SELECT value FROM system_state WHERE key = 'task_queue'")
            result = cursor.fetchone()
            task_queue_list = json.loads(result[0]) if result else []
            self.task_queue = Queue()
            for item in task_queue_list:
                self.task_queue.put(item)
        except sqlite3.Error as e:
            # Initialize with empty values in case of an error
            print(f"Database error: {e}")
            self.advisories = Queue()
            self.maintenance_required = True
            self.constraints = None
            self.parts_inventory = {}  # Example inventory
            self.personnel = []  # Example personnel
            self.maintenance_tasks = []
            self.task_queue = Queue()  # Queue for tasks awaiting personnel assignment
        finally:
            conn.close()

    def save_state(self):
        """Save the state to an SQLite database."""
        conn = sqlite3.connect("maintenance_management.db")
        cursor = conn.cursor()

        # Save maintenance_required
        cursor.execute(
            "REPLACE INTO system_state (key, value) VALUES ('maintenance_required', ?)",
            (self.maintenance_required,),
        )

        cursor.execute(
            "REPLACE INTO system_state (key, value) VALUES ('constraints', ?)",
            (json.dumps(self.constraints),),
        )

        # Save parts_inventory
        for part, quantity in self.parts_inventory.items():
            cursor.execute(
                "INSERT INTO parts_inventory (part, quantity) VALUES (?, ?)",
                (part, quantity),
            )

        # Save personnel
        for person in self.personnel:
            cursor.execute("INSERT INTO personnel (name) VALUES (?)", (person,))

        # Save maintenance_tasks as a JSON string
        cursor.execute(
            "REPLACE INTO system_state (key, value) VALUES ('maintenance_tasks', ?)",
            (json.dumps(self.maintenance_tasks),),
        )

        # For queues, save only their contents if necessary
        advisories_list = list(self.advisories.queue)
        task_queue_list = list(self.task_queue.queue)
        cursor.execute(
            "REPLACE INTO system_state (key, value) VALUES ('advisories', ?)",
            (json.dumps(advisories_list),),
        )
        cursor.execute(
            "REPLACE INTO system_state (key, value) VALUES ('task_queue', ?)",
            (json.dumps(task_queue_list),),
        )

        conn.commit()
        conn.close()

    def initialize_database(self):
        """Initialize the database with the required tables."""
        conn = sqlite3.connect("maintenance_management.db")
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS system_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS parts_inventory (
                part TEXT PRIMARY KEY,
                quantity INTEGER
            )
        """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS personnel (
                name TEXT PRIMARY KEY
            )
        """
        )

        # Add other table creation statements as needed
        cursor.execute(
            "INSERT OR REPLACE INTO system_state (key, value) VALUES ('maintenance_required', ?)",
            (True,),
        )
        cursor.execute(
            "INSERT OR REPLACE INTO system_state (key, value) VALUES ('constraints', ?)",
            (json.dumps(0),),
        )  # Assuming 'constraints' is an integer, adjust as needed

        conn.commit()
        conn.close()

    def run(self):
        self.receive_maintenance_advisories(
            [
                {
                    "id": 1,
                    "fault": "high pressure detected",
                    "fault_location": "fuel filter",
                    "fault_time": datetime.now(),
                    "fault_severity": 4,
                    "degradation_severity": 0,
                },
                {
                    "id": 22,
                    "fault": "high pressure detected",
                    "fault_location": "fuel filter",
                    "fault_time": datetime.now(),
                    "fault_severity": 4,
                    "degradation_severity": 0,
                },
            ]
        )
        self.process_maintenance_needs()
        # self.real_time_monitoring()
        self.update_system_status()
        self.store_reports()
        self.save_state()

    def receive_maintenance_advisories(self, advisories):
        """Receive advisories and add them to the advisories list."""
        for advisory in advisories:
            self.advisories.put(advisory)

    def process_maintenance_needs(self):
        """Analyze the advisories to understand maintenance needs."""
        while not self.advisories.empty():
            self.advisory = self.advisories.get()
            self.evaluate_advisory()
            self.generate_report()

    def evaluate_advisory(self):
        """Evaluate if maintenance is required based on the advisory."""
        # check for high severity (4 and 5)
        self.advisory["maintenance_required"] = any(
            [
                True
                for key, value in self.advisory.items()
                if key.endswith("_severity") and int(value) > 2
            ]
        )
        if self.advisory["maintenance_required"]:
            self.determine_required_maintenance_action()
        else:
            self.generate_report()

    def determine_required_maintenance_action(self):
        """Determine the required maintenance action from the advisory."""
        # Rule-based maintenance action determination
        # Parse the advisory for specific actions to be taken
        if (
            self.advisory["fault"] == "high pressure detected"
            and self.advisory["fault_location"] == "fuel filter"
        ):
            if self.advisory["fault_severity"] == 5:
                self.advisory["required"] = {
                    "action": "replace",
                    "component": "fuel filter",
                    "urgency": "immediate",
                }
            elif self.advisory["fault_severity"] == 4:
                self.advisory["required"] = {
                    "action": "replace",
                    "component": "fuel filter",
                    "urgency": "scheduled",
                }
            else:  # 3
                self.advisory["required"] = {
                    "action": "inspect",
                    "component": "fuel filter",
                    "urgency": "scheduled",
                }
        elif self.advisory["fault_location"] == "fuel filter":
            self.advisory["required"] = {
                "action": "inspect",
                "component": "fuel filter",
                "urgency": "scheduled",
            }

        self.apply_constraints_to_maintenance_action()

        self.check_availability_of_necessary_parts_and_tools()


    def apply_constraints_to_maintenance_action(self):
        """Apply cost constraints to the maintenance action."""
        costs = {"replace": 110, "inspect": 20, "nothing": 0}

        if costs[self.advisory["required"]["action"]] > self.maintenance_budget():
            if (
                self.advisory["fault_severity"] != 5
                and self.advisory["required"]["action"] == "replace"
            ):
                self.advisory["required"]["action"] = "inspect"
            elif self.advisory["required"]["action"] == "inspect":
                self.advisory["required"]["action"] = "nothing"

    def maintenance_budget(self):
        """Estimate the cost of a maintenance action."""
        return 100  # Example fixed cost for demonstration

    def check_availability_of_necessary_parts_and_tools(self):
        """Check if the necessary parts and tools are available."""
        if self.advisory["required"]["action"] == "replace":
            required_component = self.advisory["required"]["component"]
            quantity_available = self.inventory_manager.get_inventory_level(
                required_component
            )

            if quantity_available <= 0:
                reorder_quantity = self.inventory_manager.determine_reorder_quantity(
                    required_component
                )
                self.inventory_manager.order_new_inventory(
                    required_component, reorder_quantity
                )
                self.advisory["required"]["delay_due_missing_part"] = (
                    self.inventory_manager.get_estimated_arrival_time(
                        required_component
                    )
                    - datetime.datetime.now()
                )
        else:
            self.advisory["required"]["delay_due_missing_part"] = 0

        self.develop_maintenance_plan()

    def develop_maintenance_plan(self):
        """Develop a detailed maintenance plan based on the available parts and tools."""
        self.schedule_maintenance_task()  # assign time
        self.allocate_personnel_to_task()  # assign personnel

    def schedule_maintenance_task(self):
        """Schedule the maintenance tasks to be performed."""
        urgency_task = {
            "scheduled": 7,
            "immediate": 0,
        }  # assuming a scheduled task can be done after 7 days, and a immediate task needs be handled asap
        delay_due_personnel = 3  # assuming the maintenance provider has a fixed notice period of 3 days for any personnel
        delay = max(
            self.advisory["required"]["delay_due_missing_part"],
            delay_due_personnel,
            urgency_task[self.advisory["required"]["urgency"]],
        )
        schedule = datetime.now() + timedelta(days=delay)
        self.advisory["schedule"] = schedule.date()

    def allocate_personnel_to_task(self):
        """Assign personnel to carry out the scheduled maintenance tasks considering their availability and skills."""
        for person in self.personnel_system.skills: 
            if self.personnel_system.is_personnel_available_on_date(
                person, self.advisory["schedule"]
            ) and self.personnel_system.person_has_required_skill(
                person, self.advisory["required"]["action"]
            ):
                self.advisory["assigned_personnel"] = person
                self.personnel_system.add_task_to_personnel_calendar(
                    person,
                    self.advisory["schedule"],
                    self.advisory["required"]["action"],
                )
                # print(
                #     f"Task '{self.advisory['id']}' '{self.advisory['required']['action']}' assigned to {person} on {self.advisory['schedule']}"
                # )
                break
        else:
            print(
                "No available personnel with required skills for the task on the specified date."
            )

    def update_system_status(self):
        """Update the system with the new status once the maintenance tasks are planned."""
        # update system-wide status to reflect the planned maintenance

    def generate_report(self):
        advisory = self.advisory
        report = []

        # Report Header
        report.append(f"MAINTENANCE REPORT ID: {advisory['id']}")
        report.append("=" * 50)

        # Analysis Section
        report.append("ANALYSIS:")
        report.append(f"  Fault Detected: {advisory['fault']}")
        report.append(f"  Location: {advisory['fault_location']}")
        report.append(f"  Time Detected: {advisory['fault_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"  Fault Severity (1-5 scale): {advisory['fault_severity']}")
        report.append(f"  Equipment Degradation Severity (1-5 scale): {advisory['degradation_severity']}")
        report.append(f"  Maintenance Required: {'Yes' if advisory['maintenance_required'] else 'No'}")
        report.append("-" * 50)

        # Maintenance Action Plan Section
        required_action = advisory.get('required', {})
        report.append("MAINTENANCE ACTION PLAN:")
        report.append(f"  Proposed Action: {required_action.get('action', 'N/A')}")
        report.append(f"  Affected Component: {required_action.get('component', 'N/A')}")
        report.append(f"  Urgency Level: {required_action.get('urgency', 'N/A')}")
        delay = required_action.get('delay_due_missing_part', 0)
        report.append(f"  Delay Due to Missing Parts: {delay} day(s)" if delay else "  No Delay Expected")
        report.append("-" * 50)

        # Scheduling and Personnel Assignment Section
        schedule_date = advisory.get('schedule', 'N/A')
        assigned_personnel = advisory.get('assigned_personnel', 'Unassigned')
        report.append("SCHEDULING AND PERSONNEL ASSIGNMENT:")
        report.append(f"  Maintenance Scheduled On: {schedule_date}")
        report.append(f"  Assigned Maintenance Personnel: {assigned_personnel}")
        report.append("=" * 50)

        # Combine all parts into a single report string
        self.reports[f"{self.advisory['id']}"] = " \n".join(report)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.reports[f"{self.advisory['id']}"])

    def store_reports(self):
        """Storing the report in a persistent storage."""
        # store in database


# mms = MaintenanceManagementService()
# mms.run()
