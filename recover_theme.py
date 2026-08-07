import json

transcript_path = "/home/rhlou/.gemini/antigravity-cli/brain/913cdaf4-9123-4763-9774-5f5777e7724a/.system_generated/logs/transcript_full.jsonl"
matches = []

with open(transcript_path, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            if "tool_calls" in data:
                for tool in data["tool_calls"]:
                    if tool.get("name") in ["default_api:write_to_file", "default_api:replace_file_content"]:
                        args = tool.get("arguments", {})
                        if args.get("TargetFile", "").endswith("graphical.py"):
                            matches.append(args)
        except:
            pass

print(f"Found {len(matches)} modifications to graphical.py")
# Let's save the second to last complete write or the original file to a backup
