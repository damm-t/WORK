"""
Instagram Content Extractor CLI
===============================
Command-line interface for downloading Instagram Reels, extracting audio,
generating speech-to-text transcripts, and abstracting quantitative trading insights.
"""

import sys
import json
import argparse
from pathlib import Path
from instagram_extractor.core import (
    extract_instagram_media,
    download_file,
    extract_audio_tracks,
    transcribe_audio_file,
    abstract_quant_content,
    process_instagram_url
)

DEMO_URLS = [
    ("Reel 1 (Quant Overfitting & Sharpe Needle)", "https://www.instagram.com/reel/DeUW_vslUI8/"),
    ("Reel 2 (Wada Property & Chaos Dynamics)", "https://www.instagram.com/reel/DedM-fnN7vS/"),
    ("Reel 3 (AstraQuant Multi-Agent Architecture)", "https://www.instagram.com/reel/Dd-ZeUxvFWS/")
]

def format_box(title: str, lines: list, color: str = "\033[36m") -> str:
    reset = "\033[0m"
    bold = "\033[1m"
    width = 76
    out = [f"{color}┌─ {bold}{title}{reset}{color} " + "─" * max(0, width - len(title) - 4) + f"┐{reset}"]
    for line in lines:
        out.append(f"{color}│{reset} {line:<{width - 2}} {color}│{reset}")
    out.append(f"{color}└" + "─" * width + f"┘{reset}")
    return "\n".join(out)

def cmd_extract(args):
    print(f"\033[34m[•] Extracting media for:\033[0m {args.url}")
    res = extract_instagram_media(args.url)
    print(f"\033[32m[✓] Success!\033[0m Found {res['media_count']} stream(s) (Type: {res.get('media_type', 'unknown')})")
    if res.get('primary_video'):
        print(f"    Video URL:     {res['primary_video'][:80]}...")
    if res.get('primary_image'):
        print(f"    Image URL:     {res['primary_image'][:80]}...")
    if res.get('primary_thumbnail') and res['primary_thumbnail'] != res.get('primary_image'):
        print(f"    Thumbnail URL: {res['primary_thumbnail'][:80]}...")
    if args.json:
        print(json.dumps(res, indent=2))

def cmd_process(args):
    print(f"\033[35m[•] Running full extraction, transcription & abstraction for:\033[0m {args.url}")
    res = process_instagram_url(args.url, output_dir=args.out, transcribe=not args.no_transcribe)
    
    print(f"\n\033[32m[✓] Pipeline Completed Successfully!\033[0m")
    print(f"    MP4 Video:     {res['files']['video_mp4']}")
    print(f"    MP3 Audio:     {res['files']['audio_mp3']}")
    print(f"    Transcript:    {res['files']['transcript_txt']}")
    print(f"    Metadata JSON: {args.out}/{res['slug']}_metadata.json\n")
    
    abs_data = res["abstraction"]
    print("\033[1;33m" + "=" * 70 + "\033[0m")
    print(f"\033[1;33m  ABSTRACTION: {abs_data.get('title')}\033[0m")
    print("\033[1;33m" + "=" * 70 + "\033[0m")
    print(f"\033[1mCategory:\033[0m   {abs_data.get('category')}")
    print(f"\033[1mCore Thesis:\033[0m\n{abs_data.get('core_thesis')}\n")
    
    if "four_rigorous_tests" in abs_data:
        print("\033[1mFour Rigorous Backtest Checks:\033[0m")
        for t in abs_data["four_rigorous_tests"]:
            print(f"  • {t['test']}: \033[36m{t['status']}\033[0m\n    {t['result']}")
    elif "mathematical_foundations" in abs_data:
        print("\033[1mMathematical Foundations:\033[0m")
        for k, v in abs_data["mathematical_foundations"].items():
            print(f"  • {k}: {v}")
    elif "architectural_layers" in abs_data:
        print("\033[1mArchitectural Layers:\033[0m")
        for layer in abs_data["architectural_layers"]:
            print(f"  • {layer['layer']}: {layer['details']}")
            
    print(f"\n\033[1;32mEngine Integration Recommendation:\033[0m\n{abs_data.get('engine_integration')}\n")

def cmd_demo(args):
    print("\033[1;36m" + "#" * 70)
    print("  INSTAGRAM QUANT EXTRACTOR & ABSTRACTOR - 3 REELS DEMO")
    print("#" * 70 + "\033[0m\n")
    
    for title, url in DEMO_URLS:
        print(f"\n\033[1;34m>>> Processing: {title}\033[0m")
        res = process_instagram_url(url, output_dir=args.out, transcribe=True)
        abs_data = res["abstraction"]
        print(f"\033[32m[✓] Saved: {res['slug']}.mp4 & {res['slug']}.mp3\033[0m")
        print(f"    Title:       {abs_data.get('title')}")
        thesis = str(abs_data.get('core_thesis') or abs_data.get('transcript_summary') or 'N/A')
        print(f"    Thesis:      {thesis[:120]}...")
        print(f"    Integration: {abs_data.get('engine_integration')}")

def main():
    parser = argparse.ArgumentParser(description="Instagram Media Extractor & Quant Content Abstractor")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")
    
    # Extract only
    p_extract = subparsers.add_parser("extract", help="Extract raw stream URLs")
    p_extract.add_argument("url", help="Instagram Reel or Video URL")
    p_extract.add_argument("--json", action="store_true", help="Print raw JSON response")
    p_extract.set_defaults(func=cmd_extract)
    
    # Process full
    p_proc = subparsers.add_parser("process", help="Download, transcribe, and abstract content")
    p_proc.add_argument("url", help="Instagram Reel or Video URL")
    p_proc.add_argument("--out", default="/Users/voonfamily/Desktop/WORK/stock-signal-engine/instagram_extractor/output", help="Output directory")
    p_proc.add_argument("--no-transcribe", action="store_true", help="Skip speech transcription")
    p_proc.set_defaults(func=cmd_process)
    
    # Demo
    p_demo = subparsers.add_parser("demo", help="Process the 3 user-provided Instagram Reels")
    p_demo.add_argument("--out", default="/Users/voonfamily/Desktop/WORK/stock-signal-engine/instagram_extractor/output", help="Output directory")
    p_demo.set_defaults(func=cmd_demo)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    args.func(args)

if __name__ == "__main__":
    main()
