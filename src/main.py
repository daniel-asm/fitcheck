import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import PIL.Image
import io
import os

# Configuration 
GOOGLE_API_KEY = "Insert_Key_Here"

client = genai.Client(api_key=GOOGLE_API_KEY)

# FastAPI Setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AI Logic
def generate_try_on_image(person_img: PIL.Image.Image, shirt_img: PIL.Image.Image, pants_img: PIL.Image.Image, shoes_img: PIL.Image.Image):
    """
    Takes 4 PIL Images, returns the generated image as bytes.
    """
    print("AI Generation Started...")

    # 1. Get the description
    prompt_1 = (
    f"Describe these clothing items in a numbered list: 1. top pieces 2. bottom piece 3. footwear. For each piece of clothing, take note of: "
    f"the fit (slim, regular, relaxed),"
    f"the color (specific hex codes and on which part of the clothing that hex code refers to),"
    f"the exact type of clothing (e.g. button down or a polo if it's the top piece, jeans vs slacks if it's the bottom piece, boots vs sneakers if it's the shoes)"
    f"the material of the clothing (e.g. denim vs synthetic)"
    f"ensure that only top pieces from **IMAGE 1** are described, only bottom pieces from **IMAGE 2** are described, and only footwear from **IMAGE 3** is described\n")


    response_1 = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt_1, shirt_img, pants_img, shoes_img]
    )
    clothing_description = response_1.text.strip()
    print(f"Detected clothing: {clothing_description}")

    # 2. Generate the composite image
    prompt_2 = (
    f"Create a high-fidelity, photorealistic virtual try-on image.\n"
    f"**CORE INSTRUCTION:** Use the person/model in **IMAGE 1** as the *exclusive* identity source.\n"
    f"The person from IMAGE 1 must be wearing the clothing items shown in the other images, "
    f"which are: '{clothing_description}'.\n" 
    f"**CRUCIAL CONSTRAINTS:**\n"
    f"* **IDENTITY PRESERVATION:** Preserve the facial identity, body shape, hair, and pose *ONLY* from IMAGE 1. **DO NOT** use the identity, pose, or body of any person or mannequin from the clothing images (IMAGE 2, 3, or 4).\n"
    f"* **CLOTHING SOURCE:** Only use the visual appearance, texture, and style of the clothing items from the product images (IMAGE 2, 3, 4).\n"
    f"* **REALISM:** The clothing must be realistically composited onto their body, matching the lighting, shadows, and perspective of IMAGE 1.\n"
    f"* **BACKGROUND:** Do not change the background of IMAGE 1."
    )

    print("Sending image generation request (forcing image/png)...")
    
    try:
        response_2 = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[prompt_2, shirt_img, pants_img, shoes_img, person_img],
        )
    except Exception as e:
        print(f"API call failed directly: {e}")
        raise HTTPException(status_code=500, detail=f"API call failed: {e}")

    try:
        if not response_2.candidates[0].content.parts or len(response_2.candidates[0].content.parts) == 0:
            raise ValueError("API returned empty content (likely safety block).")
        
        image_data = None
        
        for part in response_2.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                print("Found an image in a multi-part response.")
                break
        
        if image_data:
            print("AI Generation Complete.")
            return image_data
        else:
            error_text = response_2.candidates[0].content.parts[0].text
            raise ValueError(f"API returned text-only response: {error_text}")

    except Exception as e:
        print(f"An error occurred during image extraction: {e}")
        print(f"Full API Response: {response_2}")
        
        if response_2.prompt_feedback and response_2.prompt_feedback.block_reason:
            print(f"Block Reason: {response_2.prompt_feedback.block_reason}")
            raise HTTPException(status_code=400, detail=f"Generation Blocked: {response_2.prompt_feedback.block_reason}")
        
        raise HTTPException(status_code=500, detail=f"Failed to parse API response: {e}")

# The API Endpoint
@app.post("/generate")
async def handle_generate(
    face_image: UploadFile = File(...),
    shirt_image: UploadFile = File(...),
    pants_image: UploadFile = File(...),
    shoes_image: UploadFile = File(...)
):
    try:
        person_img = PIL.Image.open(io.BytesIO(await face_image.read()))
        shirt_img = PIL.Image.open(io.BytesIO(await shirt_image.read()))
        pants_img = PIL.Image.open(io.BytesIO(await pants_image.read()))
        shoes_img = PIL.Image.open(io.BytesIO(await shoes_image.read()))

        generated_image_bytes = generate_try_on_image(person_img, shirt_img, pants_img, shoes_img)

        from fastapi.responses import StreamingResponse
        return StreamingResponse(io.BytesIO(generated_image_bytes), media_type="image/png")

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Running the server
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
