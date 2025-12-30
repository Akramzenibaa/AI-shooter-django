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

import cloudinary
import cloudinary.uploader

# Configure Cloudinary
if hasattr(settings, 'CLOUDINARY_STORAGE') and settings.CLOUDINARY_STORAGE:
    c_config = settings.CLOUDINARY_STORAGE
    if c_config.get('CLOUD_NAME'):
        cloudinary.config(
            cloud_name=c_config.get('CLOUD_NAME'),
            api_key=c_config.get('API_KEY'),
            api_secret=c_config.get('API_SECRET'),
            secure=True
        )

logger = logging.getLogger(__name__)

def generate_campaign_images(image_input, count=1, mode='creative', user_prompt='', plan='free'):
    """
    Production-grade service using the latest google-genai SDK.
    Optimized for Free Tier with model splitting and throttling.
    Modes: 'creative', 'model', 'background'
    """
    client = genai.Client(api_key=settings.GOOGLE_API_KEY)
    
    # Load image bytes - Try to avoid Pillow for performance
    try:
        if hasattr(image_input, 'read'):
            image_input.seek(0)
            img_bytes = image_input.read()
            image_input.seek(0)
        elif isinstance(image_input, bytes):
            img_bytes = image_input
        else:
            # Fallback to Pillow ONLY if necessary
            with Image.open(image_input) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()
    except Exception as e:
        logger.error(f"Error loading image bytes: {e}")
        return []

    output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_campaigns')
    os.makedirs(output_dir, exist_ok=True)

    try:
        # --- PHASE 1: GENERATE REFERENCE MODEL IMAGE (Creative Director) ---
        logger.info(f"Phase 1: Generating Reference Model Image (Gemini 3 Pro Image) [Mode: {mode}]...")
        
        # Select the high-end rules based on mode
        mode_rules = getattr(prompts, f'MODE_RULES_{mode.upper()}', prompts.MODE_RULES_CREATIVE)
        
        # Inject context (Rules + User Prompt)
        director_prompt = prompts.BETA_V2_DIRECTOR_PROMPT.format(mode_rules=mode_rules)
        if user_prompt and user_prompt.strip():
            director_prompt += f"\n\nADDITIONAL USER REQUIREMENT: {user_prompt.strip()}"

        director_res = client.models.generate_content(
            model='gemini-3-pro-image-preview',
            contents=[
                director_prompt,
                types.Part.from_bytes(data=img_bytes, mime_type='image/png')
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
        logger.info(f"Phase 2: Engineering {count} Prompts (Gemini 3 Pro Preview) [Mode: {mode}]...")
        
        mode_context = f"The user has selected the '{mode.upper()}' generation mode. Follow the specific e-commerce rules for this genre."
        engineer_prompt = prompts.BETA_V2_ENGINEER_PROMPT.format(count=count, mode_context=mode_context)
        if user_prompt and user_prompt.strip():
            engineer_prompt += f"\n\nSTRICT REQUIREMENT: The user has requested: {user_prompt.strip()}"

        prompt_res = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=[
                engineer_prompt,
                types.Part.from_bytes(data=img_bytes, mime_type='image/png'),   # [Image 1: Product]
                types.Part.from_bytes(data=model_img_bytes, mime_type='image/png') # [Image 2: Context/Vibe]
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
            logger.info(f"Phase 3: Generating Final Image {i+1}/{len(generated_prompts)} (Gemini 3 Pro Image)...")
            
            if i > 0: time.sleep(3) # Slightly longer delay for heavy Pro models

            # Instruction similar to n8n: "Generate a photo-realistic image using the provided model image and the provided product..."
            artist_instruction = (
                "Generate a photo-realistic image using the provided model image and the provided product. "
                f"Follow these details: {p_text}"
            )
            
            try:
                final_res = client.models.generate_content(
                    model='gemini-3-pro-image-preview',
                    contents=[
                        artist_instruction,
                        types.Part.from_bytes(data=img_bytes, mime_type='image/png'),       # Input Image 1
                        types.Part.from_bytes(data=model_img_bytes, mime_type='image/png') # Input Image 2 (Context)
                    ]
                )
                
                final_img_bytes = None
                if final_res.candidates and final_res.candidates[0].content.parts:
                    for part in final_res.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            final_img_bytes = part.inline_data.data
                            break
                
                if final_img_bytes:
                    filename = f"beta_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}.png"
                    cloudinary_url = None
                    
                    # --- SAFEGUARD: Local Check and Resize before Cloudinary ---
                    try:
                        with Image.open(BytesIO(final_img_bytes)) as img:
                            width, height = img.size
                            mp = (width * height) / 1000000
                            mb = len(final_img_bytes) / (1024 * 1024)
                            
                            if mp > 24.8 or mb > 9.8:
                                logger.info(f"Safeguard: Local resize needed before upload ({mp:.1f}MP, {mb:.1f}MB)")
                                scale = min(1.0, (24.0 / mp)**0.5 if mp > 24.0 else 0.9)
                                new_size = (int(width * scale), int(height * scale))
                                optimized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                                
                                temp_buffer = BytesIO()
                                optimized_img.save(temp_buffer, format="PNG", optimize=True)
                                final_img_bytes = temp_buffer.getvalue()
                                logger.info(f"Safeguard complete: {len(final_img_bytes)} bytes")

                        c_name = os.getenv('CLOUDINARY_CLOUD_NAME') or settings.CLOUDINARY_STORAGE.get('CLOUD_NAME')
                        logger.info(f"Offloading upload to Cloudinary Cloud: {c_name} ({len(final_img_bytes)} bytes)")
                        
                        import cloudinary.uploader
                        
                        try:
                            # ATTEMPT 1: Try direct upload without any local processing
                            upload_res = cloudinary.uploader.upload(
                                BytesIO(final_img_bytes),
                                folder="generated_campaigns",
                                resource_type="image"
                            )
                            cloudinary_url = upload_res.get('secure_url')
                        except Exception as upload_err:
                            err_msg = str(upload_err).lower()
                            if "too large" in err_msg or "megapixel" in err_msg or "limit" in err_msg:
                                logger.warning(f"Cloudinary rejected original file. Falling back to local optimization: {upload_err}")
                                
                                # FALLBACK: Pillow Optimization Only When Necessary
                                with Image.open(BytesIO(final_img_bytes)) as img:
                                    width, height = img.size
                                    mp = (width * height) / 1000000
                                    mb = len(final_img_bytes) / (1024 * 1024)
                                    
                                    # Optimize loop
                                    current_img = img
                                    attempts = 0
                                    while (mp > 24.5 or mb > 9.3) and attempts < 3:
                                        attempts += 1
                                        scale = 0.85
                                        if mp > 25.0: scale = (24.0 / mp) ** 0.5
                                        
                                        new_size = (int(current_img.size[0] * scale), int(current_img.size[1] * scale))
                                        current_img = current_img.resize(new_size, Image.Resampling.LANCZOS)
                                        
                                        temp_buffer = BytesIO()
                                        current_img.save(temp_buffer, format="PNG", optimize=True)
                                        final_img_bytes = temp_buffer.getvalue()
                                        
                                        mp = (new_size[0] * new_size[1]) / 1000000
                                        mb = len(final_img_bytes) / (1024 * 1024)
                                    
                                    # ATTEMPT 2: Try upload again after local optimization
                                    upload_res = cloudinary.uploader.upload(
                                        BytesIO(final_img_bytes),
                                        folder="generated_campaigns",
                                        resource_type="image"
                                    )
                                    cloudinary_url = upload_res.get('secure_url')
                            else:
                                raise upload_err # Rethrow if it's not a size issue

                        if cloudinary_url:
                            logger.info(f"Cloudinary Success [Plan: {plan}]: {cloudinary_url}")
                    except Exception as e:
                        logger.error(f"CLOUDINARY ERROR: {str(e)}")

                    
                    # 2. URL resolution and Fallback Storage
                    if cloudinary_url:
                        final_url = cloudinary_url
                        filepath = f"cloud:{filename}" # Logical path for reference
                    else:
                        # Fallback: Save locally ONLY if Cloudinary failed
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(final_img_bytes)
                        
                        final_url = f"{settings.MEDIA_URL}generated_campaigns/{filename}"
                        logger.warning(f"Cloudinary upload failed for {filename}, falling back to local storage.")
                    
                    results.append({
                        'path': filepath,
                        'prompt': p_text,
                        'url': final_url
                    })
                    logger.info(f"Final Image {i+1} ready at: {final_url}")
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
