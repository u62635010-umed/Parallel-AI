# 🧠 Parallel AI: Premium Explainer Agent

Parallel AI is a sophisticated, agentic system built with **LangGraph**, **Groq**, and **Streamlit**. It provides structured, context-aware responses and allows for deep-dive exploration of specific points in a dedicated "Parallel Explainer" panel.

![Parallel-AI-Banner](https://img.shields.io/badge/LangGraph-Agentic-blue?style=for-the-badge&logo=python&logoColor=white)
![Groq-Powered](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange?style=for-the-badge&logo=speedtest&logoColor=white)
![Streamlit-UI](https://img.shields.io/badge/Streamlit-Premium_UI-red?style=for-the-badge&logo=streamlit&logoColor=white)

## ✨ Key Features

-   **🎯 5-Point Insights**: Every query is broken down into exactly 5 concise, actionable points.
-   **🔍 Context-Isolated Deep Dives**: Select any point to trigger a "Parallel Agent" that provides a deep-dive explanation without losing your conversation flow.
-   **🚀 Lightning Fast**: Powered by Groq's high-performance `llama-3.3-70b-versatile` model.
-   **💎 Premium UI**: A sleek, dark-themed interface with glassmorphism effects and responsive side-panels.

## 🛠️ Tech Stack

-   **Backend**: Python, LangGraph (for agent orchestration)
-   **LLM Provider**: [Groq](https://groq.com/)
-   **Frontend**: Streamlit
-   **State Management**: LangGraph StateGraph

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.9+ installed and a valid [Groq API Key](https://console.groq.com/keys).

### 2. Installation
Clone the repository and install the dependencies:

```bash
git clone https://github.com/your-username/Parallel-AI.git
cd Parallel-AI
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory and add your API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Running the App
Launch the Streamlit interface:

```bash
streamlit run streamlit_app.py
```

## 🧠 How it Works

1.  **Main Agent**: Processes your initial request and generates 5 core pillars of the answer.
2.  **Explainer Agent**: Waits for your selection. When a point is clicked, it receives the original context and deep-dives specifically into that atomic point.
3.  **State Management**: LangGraph ensures that the explanation state and the main conversation state remain perfectly synchronized.

---

> [!TIP]
> Use the sidebar configuration if you need to quickly swap API keys during development.

---
*Built with ❤️ by Antigravity*
