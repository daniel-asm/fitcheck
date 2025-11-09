# FitCheck (Digital Closet)

FitCheck is a virtual try-on application built for HackUMass 2025. It allows a user to upload a photo of themselves and separate images of clothing, then generates a new, photorealistic image of the user wearing the complete outfit.

Video Demo: https://youtu.be/j7n_oePJHEg

## What it Does

1.  **Upload:** The user provides four images: a full-body photo, a shirt, a pair of pants, and a pair of shoes.
2.  **Generate:** The frontend sends these images to a Python backend.
3.  **Display:** The backend uses the Google Gemini API to analyze the clothing and generate a new composite image of the user wearing the selected items.

## Tech Stack

  * **Frontend:** HTML, CSS, JavaScript
  * **Backend:** Python 3.9+ with FastAPI and Uvicorn
  * **AI:** Google Gemini API (`gemini-2.5-flash`)
      * **Step 1 (Text):** The API analyzes the clothing images to create a detailed text description.
      * **Step 2 (Image):** The API uses the user's photo, the text description, and a `generation_config` (to force an `image/png` response) to create the final composite image.

## How to Run

### Prerequisites

  * Python 3.9+
  * A Google Gemini API Key
  * Visual Studio Code
  * The **Live Server** VSCode extension

### 1\. Backend (Python Server)

1.  Open a terminal in the project's root directory.
2.  Create and activate a virtual environment:
    ```bash
    # Create the venv
    python3 -m venv .venv

    # Activate it (Mac/Linux)
    source .venv/bin/activate

    # (Windows)
    # .\.venv\Scripts\activate
    ```
3.  Install the required Python packages:
    ```bash
    pip install fastapi "uvicorn[standard]" google-genai Pillow
    pip install python-multipart
    ```
4.  Open `src/main.py` and paste your Google Gemini API Key into the `GOOGLE_API_KEY` variable.
5.  Run the backend server:
    ```bash
    python src/main.py or python3 src/main.py
    ```
    The server will run on `http://127.0.0.1:8000`. Leave this terminal running.

### 2\. Frontend (VSCode Live Server)

1.  In VSCode, right-click the `frontend/index.html` file.
2.  Select **"Open with Live Server"**.
3.  Your browser will open to the app. It will automatically communicate with your backend.

## Challenges We Ran Into

  * **AI Safety Filters:** The Gemini API's safety filters frequently blocked requests, even when using a mannequin. We had to iterate on our prompts to be "safer" and build robust error-handling to catch empty API responses without crashing.
  * **API Edge Cases:** We discovered the API would sometimes return a multi-part response (`[text, image, text]`) instead of a single image. We updated our code to loop through the response parts to find the first valid image.
