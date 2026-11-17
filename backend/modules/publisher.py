import os
import zipfile
import json

def create_export_pack(video_id: str, video_path: str, script_data: dict, output_dir: str = None) -> str:
    """
    Creates an export pack (.zip) with video, captions, hashtags,
    and platform-specific posting guidelines.
    """
    if not output_dir:
        output_dir = r"F:\Projects\beauty-marketing-agent\storage\export_packs"
    os.makedirs(output_dir, exist_ok=True)
    
    zip_path = os.path.join(output_dir, f"pack_{video_id}.zip")
    
    caption_content = f"""=== INSTAGRAM / TIKTOK / YOUTUBE SHORTS CAPTION ===
{script_data.get('caption', '')}

HASHTAGS:
{' '.join(script_data.get('hashtags', []))}

CALL TO ACTION:
{script_data.get('call_to_action', 'Check link in bio')}

TRACKED STORE LINK:
https://mystore.pk/products/{script_data.get('product_name', 'item').lower().replace(' ', '-')}?utm_source=instagram_reels&utm_medium=ai_agent&utm_campaign={video_id}
"""
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        if os.path.exists(video_path):
            zf.write(video_path, arcname=os.path.basename(video_path))
        zf.writestr("caption_and_links.txt", caption_content)
        zf.writestr("script_metadata.json", json.dumps(script_data, indent=2))
        
    return zip_path
