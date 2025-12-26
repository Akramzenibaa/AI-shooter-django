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
        # --- PHASE 1: GENERATE REFERENCE MODEL IMAGE (Creative Director) ---
        logger.info("Phase 1: Generating Reference Model Image (Gemini 2.0 Flash)...")
        
        director_res = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                prompts.BETA_V2_DIRECTOR_PROMPT,
                types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg')
            ]
        )
        
        model_img_bytes = None
        if director_res.candidates and director_res.candidates[0].content.parts:
            for part in director_res.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    model_img_bytes = part.inline_data.data
                    break
        
        if not model_img_bytes:
            logger.error("Failed to generate Phase 1 Model Image. Falling back...")
            # Fallback: Just use the original image if model generation failed
            model_img_bytes = img_bytes

        # --- PHASE 2: GENERATE PROMPT LIST (Prompt Engineer) ---
        logger.info(f"Phase 2: Engineering {count} Prompts (Gemini 2.0 Flash)...")
        
        engineer_prompt = prompts.BETA_V2_ENGINEER_PROMPT.format(count=count)
        
        prompt_res = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                engineer_prompt,
                types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),   # [Image 1: Product]
                types.Part.from_bytes(data=model_img_bytes, mime_type='image/jpeg') # [Image 2: Context/Vibe]
            ]
        )
        
        response_text = prompt_res.text or ""
        generated_prompts = []
        for line in response_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() and ('. ' in line[:4] or ') ' in line[:4])):
                if ':' in line:
                    generated_prompts.append(line.split(':', 1)[1].strip())
                else:
                    # Capture everything after the first dot/parenthesis
                    import re
                    match = re.search(r'^\d+[\.\)]\s*(.*)', line)
                    if match:
                        generated_prompts.append(match.group(1).strip())
        
        # Fallback if parsing fails
        if not generated_prompts:
            generated_prompts = [line.strip() for line in response_text.split('\n') if len(line.strip()) > 30][:count]

        generated_prompts = generated_prompts[:count]
        logger.info(f"Phase 2 complete. Generated {len(generated_prompts)} prompts.")

        # --- PHASE 3: EXECUTE FINAL IMAGES (Artist) ---
        results = []
        for i, p_text in enumerate(generated_prompts):
            logger.info(f"Phase 3: Generating Final Image {i+1}/{len(generated_prompts)}...")
            
            if i > 0: time.sleep(2) # Modest throttle for rate limits

            # Instruction similar to n8n: "Generate a photo-realistic image using the provided model image and the provided product..."
            artist_instruction = (
                "Generate a photo-realistic image using the provided model image and the provided product. "
                f"Follow these details: {p_text}"
            )
            
            try:
                final_res = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=[
                        artist_instruction,
                        types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),       # Input Image 1
                        types.Part.from_bytes(data=model_img_bytes, mime_type='image/jpeg') # Input Image 2 (Context)
                    ]
                )
                
                final_img_bytes = None
                if final_res.candidates and final_res.candidates[0].content.parts:
                    for part in final_res.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            final_img_bytes = part.inline_data.data
                            break
                
                if final_img_bytes:
                    filename = f"beta_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(final_img_bytes)
                    
                    results.append({
                        'path': filepath,
                        'prompt': p_text,
                        'url': f"{settings.MEDIA_URL}generated_campaigns/{filename}"
                    })
                    logger.info(f"Success! Final Image {i+1} saved.")
                else:
                    logger.warning(f"No image data in final response for prompt {i+1}")
            
            except Exception as e_inner:
                logger.error(f"Error in Phase 3.{i+1}: {e_inner}")
                if "429" in str(e_inner): break 

        return results



    except Exception as e:
        import traceback
        logger.error(f"Global AI Error: {e}")
        # traceback.print_exc()
        return []
