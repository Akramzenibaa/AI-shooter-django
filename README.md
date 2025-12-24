# AI Shooter

AI Shooter is a professional AI-powered product photography application. It allows users to turn simple product photos into high-end advertising campaigns using Google Gemini's multimodal capabilities.

## Features

-   **Multi-Mode Generation**:
    -   **✨ Campaign**: Creates conceptual, high-emotion advertising scenes.
    -   **👤 On Model**: Realistically places products on human models.
    -   **⬜ Clean BG**: Generates commercial quality, distraction-free product shots.
-   **Custom Prompting**: Users can provide specific creative direction (e.g., "add neon lights") which the AI integrates into the generation process.
-   **Credit System**: Built-in user credit management.
-   **History**: Automatically saves generated images locally.

## Tech Stack

-   **Backend**: Django 5.x, Python 3.12
-   **AI**: Google Gemini 2.0 Flash Lite (Analysis) + Gemini 2.5 Flash Image (Generation)
-   **Frontend**: HTML, CSS (Vanilla), JavaScript

## Setup

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Set up environment variables (see `.env`):
    -   `GOOGLE_API_KEY`: Your Gemini API key.
    -   `DJANGO_SECRET_KEY`: Your Django secret.
4.  Run migrations:
    ```bash
    python manage.py migrate
    ```
5.  Start the server:
    ```bash
    python manage.py runserver 5500
    ```
