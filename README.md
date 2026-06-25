
# University Degree Planner - Autonomous AI Agent

This project implements an autonomous AI agent using the ReAct (Reasoning and Acting) framework to function as a university degree planner. It integrates a local Large Language Model (LLM) with external tools, parses unstructured PDF data, and manages application state using LangGraph and Pydantic.

## Project Structure

* `main.py`: The main orchestrator that parses command-line arguments, reads the transcript, and executes the LangGraph agent.
* `agent.py`: Contains the LangGraph state definition, nodes, edges, and compilation logic for the ReAct loop.
* `models.py`: Defines strict Pydantic schemas (`Course`, `Semester`, `DegreePlan`) with custom validators (e.g., schedule conflict detection).
* `tools.py`: Contains the mock MCP (Model Context Protocol) tool `search_courses` that the LLM uses to fetch university catalog data.
* `parser.py`: Utility to parse unstructured text from PDF transcripts into structured `Course` objects using `pdfplumber` and Regex.
* `docker-compose.yml` & `Dockerfile`: Containerization setup ensuring reproducible execution and isolated environments.
* `.env.example`: Template for required environment variables.

## Design Choices & Architecture

1. **State Management (LangGraph):** LangGraph manages the cyclical, stateful nature of the ReAct loop. The state tracks the conversation history, step count, and the evolving `DegreePlan`.
2. **Data Validation (Pydantic):** Pydantic ensures the LLM's outputs conform to strict JSON schemas. A custom class validator on the `Semester` model programmatically catches overlapping course schedules, forcing the agent to reason about constraints.
3. **Structured Logging (Loguru):** All agent steps, tool calls, and limits are logged as JSON objects to `output/agent.log` for programmatic auditing.
4. **Local LLM (Ollama):** The project uses Llama 3.2 1B (via Ollama) to balance performance and local resource constraints, running entirely privately without relying on paid external APIs.

## Setup and Execution Instructions

### Prerequisites
* Docker and Docker Compose installed on your machine.

### 1. Configure the Environment
Copy the example environment file to create your active configuration:
```bash
cp .env.example .env

```

Ensure your `OLLAMA_MODEL` is set to `llama3.2:1b` (or whichever model your system has the RAM to support).

### 2. Prepare the Input Data

Ensure you have a student transcript in PDF format located at `data/sample_transcript.pdf`. The parser expects a standard format containing the course code, title, and credits (e.g., `CS 101 Intro to Programming 3`).

### 3. Run the Application

The entire environment, including the Python application and the Ollama LLM service, is orchestrated via Docker Compose.

Run the following command from the root of the project:

```bash
docker-compose up --build

```

**Note on First Execution:** If this is your first time running the application, you must pull the LLM into the Ollama container before the Python app executes:

```bash
docker-compose up -d ollama
docker exec -it <name_of_ollama_container> ollama pull llama3.2:1b
docker-compose up --build

```

### 4. View the Output

Upon successful completion, the application will generate two files in the `output/` directory:

1. **`agent.log`**: A structured JSON log detailing every step of the agent's decision-making process, tool calls, and responses.
2. **`degree_plan.json`**: The final, Pydantic-validated degree plan formatted strictly to the required schema.

```

```
