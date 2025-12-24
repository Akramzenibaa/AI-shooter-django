import os
import time
import logging
from google import genai
from google.genai import types
from django.conf import settings
from PIL import Image
from io import BytesIO
import base64
from datetime import datetime
from . import prompts

logger = logging.getLogger(__name__)

def generate_campaign_images(image_input, count=1, mode='creative', user_prompt=''):
    """
    Production-grade service using the latest google-genai SDK.
    Optimized for Free Tier with model splitting and throttling.
    Modes: 'creative', 'model', 'background'
    """
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    
    # Load image
    try:
        if isinstance(image_input, Image.Image):
            product_img = image_input
        else:
            # Handle string path or file-like object (InMemoryUploadedFile)
            product_img = Image.open(image_input)
            # Re-verify and convert to RGB if necessary (e.g. RGBA -> RGB for JPEG save)
            if product_img.mode != 'RGB':
                product_img = product_img.convert('RGB')
        
        # Convert PIL to bytes for the new SDK
        buffered = BytesIO()
        product_img.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

    except Exception as e:
        logger.error(f"Error loading image: {e}")
        return []

    output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_campaigns')
    os.makedirs(output_dir, exist_ok=True)

    try:
        # --- PHASE 1 & 2: CONSOLIDATED ANALYSIS & IDEATION (Gemini 2.0 Flash Lite) ---
        # 2.0-flash-lite: The absolute highest quota model for text/vision.
        logger.info(f"Phase 1 & 2: Analyzing & Brainstorming (Gemini 2.0 Flash Lite) [Mode: {mode}]...")
        
        # Select prompt based on mode
        if mode == 'model':
            analysis_text = prompts.ANALYSIS_PROMPT_MODEL
        elif mode == 'background':
            analysis_text = prompts.ANALYSIS_PROMPT_BACKGROUND
        else:
            analysis_text = prompts.ANALYSIS_PROMPT_CREATIVE

        # Inject user custom instructions if provided
        custom_instruction = ""
        if user_prompt and user_prompt.strip():
            # We add this nicely to the creative brief
            custom_instruction = f"\n\nADDITIONAL USER REQUIREMENTS:\nThe user has explicitly requested: {user_prompt.strip()}.\nIntegrate this requirement naturally into the visual concepts."

        # We need a stronger connection to ensure it generates the LIST, not just the analysis.
        combined_prompt = (
            f"{analysis_text}\n"
            f"{custom_instruction}\n"
            f"--------------------------------------------------\n"
            f"CRITICAL INSTRUCTION: Perform the analysis above silently, "
            f"and then output ONLY the list of prompts as requested below.\n"
            f"{prompts.PROMPT_GENERATION_PROMPT.format(count=count)}"
        )
        
        try:
            consolidated_res = client.models.generate_content(
                model='gemini-2.0-flash-lite',
                contents=[combined_prompt, types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')]
            )
            response_text = consolidated_res.text
        except Exception as api_err:
            # If the newest lite model fails, we try the "Old Reliable" 1.5 equivalent
            if "429" in str(api_err):
                logger.warning("2.0-Lite Busy. Falling back to Gemini-Flash-Latest...")
                consolidated_res = client.models.generate_content(
                    model='gemini-flash-latest',
                    contents=[combined_prompt, types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')]
                )
                response_text = consolidated_res.text
            else:
                raise api_err
        
        if not response_text:
            logger.warning(f"AI Brain returned no text. Candidates: {consolidated_res.candidates}")
            response_text = ""
        
        # Parse prompts from the consolidated response
        generated_prompts = []
        for line in response_text.split('\n'):
            if line.strip() and (line[0].isdigit() and '. ' in line[:4]):
                if ':' in line:
                    generated_prompts.append(line.split(':', 1)[1].strip())
                else:
                    generated_prompts.append(line.split('.', 1)[1].strip())
        
        # Fallback if parsing fails
        if not generated_prompts:
             generated_prompts = [line.strip() for line in response_text.split('\n') if len(line.strip()) > 30][:count]

        generated_prompts = generated_prompts[:count]
        logger.info(f"Ideation complete. Found {len(generated_prompts)} concepts.")

        time.sleep(1) # Minimal pause for testing

        # --- PHASE 3: EXECUTION (Gemini 2.5 Flash Image) ---
        # Native Image Generation: This model (Nano Banana) draws natively.
        results = []
        for i, p_text in enumerate(generated_prompts):
            logger.info(f"Phase 3: Image {i+1}/{len(generated_prompts)} (Gemini 2.5 Flash Image)...")
            
            if i > 0: time.sleep(2) # Faster for Flash

            # Imagen models prefer a direct, descriptive prompt
            execution_req = f"{p_text}. Professional high-quality advertising photography, 8k resolution, cinematic lighting."
            
            try:
                # Use generate_content for Native Image Models with original image context
                response = client.models.generate_content(
                    model='gemini-2.5-flash-image',
                    contents=[
                        p_text, 
                        types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')
                    ]
                )

                
                # Extract image bytes from the first candidate/part
                img_data = None
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            img_data = part.inline_data.data
                            break
                
                if img_data:
                    filename = f"gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    
                    results.append({
                        'path': filepath,
                        'prompt': p_text,
                        'url': f"{settings.MEDIA_URL}generated_campaigns/{filename}"
                    })
                    logger.info(f"Success! Image {i+1} saved using Gemini 2.5 Flash Image.")
                else:
                    logger.warning(f"No native image found in response for prompt {i+1}")
            
            except Exception as e_inner:
                logger.error(f"Error in Phase 3.{i+1} (Flash Image): {e_inner}")
                if "429" in str(e_inner): break 

        return results



    except Exception as e:
        import traceback
        logger.error(f"Global AI Error: {e}")
        # traceback.print_exc()
        return []
