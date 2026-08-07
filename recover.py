import json

path = "/home/rhlou/.gemini/antigravity-cli/brain/913cdaf4-9123-4763-9774-5f5777e7724a/.system_generated/logs/transcript_full.jsonl"
last_full_code = None

with open(path, 'r') as f:
    for line in f:
        if "graphical.py" in line:
            try:
                data = json.loads(line)
                if "tool_calls" in data:
                    for tc in data["tool_calls"]:
                        args = tc.get("arguments", {})
                        if "graphical.py" in str(args):
                            if "CodeContent" in args:
                                last_full_code = args["CodeContent"]
            except Exception as e:
                pass

if last_full_code:
    with open("src/visualization/graphical_blueprint.py", "w") as f:
        f.write(last_full_code)
    print("Recovered blueprint!")
else:
    print("Could not find CodeContent")
