# main.py
import argparse
import os
from loguru import logger
from parser import parse_transcript
from agent import app_graph
from models import DegreePlan

# 1. Configure Logger for structured JSON output
# This fulfills the requirement to log in JSON format to output/agent.log
logger.remove() # Remove the default console logger
logger.add(
    "output/agent.log", 
    serialize=True, 
    level=os.getenv("LOG_LEVEL", "INFO")
)

def main():
    # 2. Parse command-line arguments
    parser = argparse.ArgumentParser(description="University Degree Planner Agent")
    parser.add_argument("--transcript", required=True, help="Path to the student's PDF transcript")
    parser.add_argument("--goal", required=True, help="The goal for the agent to achieve")
    args = parser.parse_args()

    logger.info("Application started", event="App startup", goal=args.goal, transcript_path=args.transcript)

    # 3. Parse the PDF Transcript
    try:
        completed_courses = parse_transcript(args.transcript)
        logger.info("Parsed transcript successfully", event="Transcript parsed", courses_found=len(completed_courses))
    except Exception as e:
        logger.error(f"Failed to parse transcript: {e}", event="Parser error")
        return

    # 4. Initialize the Agent State
    # Note: We initialize an empty plan with the completed courses. 
    # In a fully fleshed-out agent, you would create a tool like `add_course_to_plan` 
    # for the LLM to call, which would update this specific object in the state.
    initial_degree_plan = DegreePlan(
        student_id="STUD_999", 
        completed_courses=completed_courses, 
        planned_semesters=[]
    )
    
    initial_state = {
        "messages": [
            ("system", "You are a helpful university degree planning assistant. Use the search_courses tool to find available classes to fulfill the user's goal."),
            ("human", f"My transcript shows I have completed these courses: {[c.course_code for c in completed_courses]}. {args.goal}")
        ],
        "degree_plan": initial_degree_plan,
        "step_count": 0
    }

    # 5. Run the LangGraph Agent
    logger.info("Starting agent execution loop", event="Agent loop started")
    
    # We use invoke() to run the graph from start to finish
    final_state = app_graph.invoke(initial_state)

    # 6. Check for Step Limit and Log Warning
    max_steps = int(os.getenv("AGENT_MAX_STEPS", 10))
    if final_state["step_count"] >= max_steps:
        # This matches the strict contract requirement for step limits
        logger.warning("Agent step limit reached", event="Agent step limit reached", step_count=final_state["step_count"])
    else:
        logger.info("Agent execution completed", event="Agent completed", total_steps=final_state["step_count"])

    # 7. Serialize the Final Plan to JSON
    final_plan: DegreePlan = final_state["degree_plan"]
    
    with open("output/degree_plan.json", "w") as f:
        # Pydantic's .json() handles the schema formatting automatically
        f.write(final_plan.json(indent=2))
        
    logger.info("Degree plan saved", event="Plan saved", file_path="output/degree_plan.json")
    print("\n✅ Execution Complete! Check the 'output' folder for agent.log and degree_plan.json.")

if __name__ == "__main__":
    main()