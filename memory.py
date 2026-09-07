import datetime
import json
from vector_db import patient_vector_store

class ShortTermMemory:
    """Retains the active user session context and message history."""
    def __init__(self):
        self.messages = [] # list of {"role": "user"|"assistant"|"system", "content": str, "timestamp": str}
        self.active_patient_id = None
        self.active_patient_context = {}

    def add_message(self, role, content):
        msg = {
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.messages.append(msg)
        return msg

    def set_patient_context(self, patient_id, patient_info):
        self.active_patient_id = patient_id
        self.active_patient_context = patient_info

    def clear(self):
        self.messages.clear()
        self.active_patient_id = None
        self.active_patient_context = {}

    def get_history(self):
        return self.messages

class LongTermMemory:
    """Manages persistent memory lookups across patient sessions via vector & DB lookups."""
    def __init__(self):
        pass

    def search_patient_history(self, patient_id, query, top_k=3):
        """Query vector database for specific patient records relevant to search query."""
        results = patient_vector_store.similarity_search(query, top_k=top_k*2)
        # Filter for this specific patient
        patient_results = [r for r in results if r.get("metadata", {}).get("patient_id") == patient_id]
        return patient_results[:top_k]

    def get_patient_profile_summary(self, patient_info, records):
        """Format a rich patient context summary string."""
        summary = f"Patient: {patient_info['name']} (ID: {patient_info['patient_id']}), {patient_info['age']} y/o {patient_info['gender']}.\n"
        summary += f"Relation: {patient_info.get('relation', 'Self')}\n"
        summary += f"Primary Condition: {patient_info.get('primary_condition', 'N/A')}\n"
        summary += f"Allergies: {patient_info.get('allergies', 'None reported')}\n"
        summary += f"Blood Group: {patient_info.get('blood_group', 'Unknown')}\n"
        
        if records:
            summary += "\nRecent Clinical Records & Diagnostics:\n"
            for r in records[:5]:
                summary += f"- [{r.get('timestamp', 'Recent')}] {r.get('record_type', 'Note')}: {r.get('title', '')} - {r.get('details', '')} (Severity: {r.get('severity', 'Normal')})\n"
        else:
            summary += "\nNo prior clinical records found.\n"

        return summary

class AgentMemoryTrace:
    """Tracks sub-goal decomposition, tool inputs/outputs, and reasoning steps for debugging and audit."""
    def __init__(self):
        self.trace_steps = []

    def log_step(self, step_num, goal, tool_name, tool_input, tool_output, success=True, details=None):
        step = {
            "step_number": step_num,
            "goal": goal,
            "tool_name": tool_name,
            "tool_input": tool_input,
            "tool_output": tool_output,
            "success": success,
            "details": details or {},
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
        self.trace_steps.append(step)

    def get_trace(self):
        return self.trace_steps

    def clear(self):
        self.trace_steps.clear()
