# AI Healthcare Assistant (Powered by Gemini)

This project is a domain-specific conversational assistant designed for a healthcare organization. It provides safe, general information about health topics, symptoms, and wellness guidelines. The assistant is built using Google's Gemini API and relies on advanced prompt engineering techniques to ensure its responses are accurate, harmless, and responsible.

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/YourUsername/YourSpaceName) <!--- **IMPORTANT**: Replace this link with your actual Hugging Face Space URL --->


<!--- **OPTIONAL**: Replace this with a screenshot of your running Gradio app --->

## Table of Contents

- [**Project Overview**](#project-overview)
- [**Core Features**](#core-features)
- [**The Three-Layer Safety Framework**](#the-three-layer-safety-framework)
- [**Prompting Techniques Implemented**](#prompting-techniques-implemented)
- [**Technology Stack**](#technology-stack)
- [**Getting Started**](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup](#local-setup)
  - [Running with Docker](#running-with-docker)
- [**Deployment**](#deployment)
  - [Deploying on Hugging Face Spaces](#deploying-on-hugging-face-spaces)
- [**How to Use the App**](#how-to-use-the-app)
- [**Project Structure**](#project-structure)
- [**Future Work**](#future-work)

## Project Overview

The goal of this project is to create a reliable AI assistant that can serve as a first point of contact for non-emergency patient queries. Instead of fine-tuning a model, which requires significant computational resources, this project leverages the power of a large foundation model (Google's Gemini) and controls its behavior through carefully crafted prompts. This approach allows for rapid development, state-of-the-art performance, and a strong focus on safety.

## Core Features

-   **Interactive Chat Interface:** A user-friendly web UI built with Gradio.
-   **Multiple Prompting Techniques:** An interactive "laboratory" to compare Zero-Shot, Few-Shot, and Chain-of-Thought prompting in real-time.
-   **Robust Safety System:** A multi-layered approach to prevent the model from giving harmful advice or handling emergencies.
-   **API and Docker Support:** The application is built with FastAPI and containerized with Docker for easy deployment and scalability.

## The Three-Layer Safety Framework

Safety is the highest priority. This application implements a three-layer system to ensure responsible operation:

1.  **Input Guardrail:** Scans all user queries for a predefined list of sensitive or emergency-related keywords (e.g., "chest pain", "suicide"). If a keyword is found, the query is immediately blocked, and a standard emergency message is returned without ever calling the AI.
2.  **Prompting Guardrail:** The prompt sent to the Gemini API is engineered with a detailed "system persona" that strictly defines the AI's role as a helpful assistant, not a doctor. It explicitly forbids giving diagnoses or medical advice.
3.  **Output Guardrail:** A final check is performed on the AI's response. If the mandatory disclaimer ("*Disclaimer: This is for informational purposes only...*") is missing for any reason, it is automatically appended before being displayed to the user.

## Prompting Techniques Implemented

The application allows users to dynamically switch between three key prompting techniques:

-   **Zero-Shot:** Giving the model a direct command without examples. Quick but can be inconsistent.
-   **Few-Shot:** Providing 2-3 high-quality examples of questions and desired answers. This significantly improves the reliability and structure of the model's output.
-   **Chain-of-Thought (CoT):** The most advanced technique used. The prompt includes an example where the AI "thinks step-by-step" to deconstruct a query before formulating an answer. This produces the most reasoned, safe, and reliable responses, making it the recommended default.

## Technology Stack

-   **AI Service:** Google Gemini 1.5 Flash API
-   **Web Framework:** Gradio
-   **Backend API:** FastAPI (integrated via Gradio)
-   **Containerization:** Docker
-   **Primary Libraries:** `google-generativeai`, `gradio`, `fastapi`

## Getting Started

You can run this application either locally on your machine or using Docker.

### Prerequisites

-   Python 3.9+
-   A Google Gemini API Key. You can get one from [**Google AI Studio**](https://aistudio.google.com/app/apikey).
-   Docker (if using the Docker-based setup).

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/YourRepositoryName.git
    cd YourRepositoryName
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set the API Key as an Environment Variable:**
    This is the secure way to handle your key. **Do not hard-code it in the script.**

    -   **On macOS/Linux:**
        ```bash
        export GOOGLE_API_KEY="your_api_key_here"
        ```
    -   **On Windows (Command Prompt):**
        ```bash
        set GOOGLE_API_KEY="your_api_key_here"
        ```
    -   **On Windows (PowerShell):**
        ```powershell
        $env:GOOGLE_API_KEY="your_api_key_here"
        ```

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The app will be available at `http://127.0.0.1:7860`.

### Running with Docker

Using Docker is the easiest way to ensure a consistent environment.

1.  **Build the Docker image:**
    From the root of the project directory, run:
    ```bash
    docker build -t gemini-healthcare-app .
    ```

2.  **Run the Docker container:**
    Pass your API key as an environment variable using the `-e` flag.
    ```bash
    docker run -p 8000:8000 -e GOOGLE_API_KEY="your_api_key_here" gemini-healthcare-app
    ```
    The app will be available at `http://localhost:8000`.

## Deployment

The easiest way to deploy this application online for free and share it with others is by using **Hugging Face Spaces**.

1.  **Create a Hugging Face Account:** Sign up at [HuggingFace.co](https://huggingface.co).
2.  **Create a New Space:**
    -   Click your profile -> "New Space".
    -   Give it a name and select **"Gradio"** as the SDK.
    -   Choose a free "CPU basic" hardware tier.
3.  **Upload Files:**
    -   Go to the **"Files"** tab and upload your `app.py` and `requirements.txt` files.
4.  **Add API Key as a Secret:**
    -   Go to the **"Settings"** tab.
    -   Scroll to **"Repository secrets"** and click "New secret".
    -   **Name:** `GOOGLE_API_KEY`
    -   **Secret value:** Paste your actual Gemini API key.

The Space will automatically build and launch your application, giving you a public URL to share.

## How to Use the App

1.  Navigate to the running application's URL.
2.  Select a **Prompting Technique** from the radio buttons (Chain-of-Thought is recommended).
3.  Type your general health question into the textbox.
4.  Press Enter or click the submit button to get a response.
5.  Observe how different prompting techniques change the AI's answer structure and detail.

## Project Structure
