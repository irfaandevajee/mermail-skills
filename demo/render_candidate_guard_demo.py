#!/usr/bin/env python3
import os
import subprocess
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
OUT = Path("demo_build")
OUT.mkdir(exist_ok=True)
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

BG = (17, 19, 24)
PANEL = (29, 33, 41)
TEXT = (241, 245, 249)
MUTED = (171, 181, 196)
ACCENT = (255, 118, 57)
GOOD = (91, 212, 145)
WARN = (255, 196, 87)
BAD = (255, 105, 120)

slides = [
    {
        "title": "Mermail Candidate Submission Guard",
        "kicker": "LIVE AGENT-SKILL DEMO • CHATGPT + MERMAIL MCP",
        "body": [
            "Prompt:",
            "Before I submit Emma Clarke and Lucas Reed to Northstar Analytics",
            "for Senior Data Scientist, verify role-specific consent and check for",
            "duplicate or conflicting submission evidence. Do not send anything.",
            "",
            "Goal: prevent duplicate representation, protect candidate consent,",
            "and return a clear READY / BLOCKED decision before client submission."
        ],
        "narration": "This is the Mermail Candidate Submission Guard, a reusable recruiter-side agent skill running with ChatGPT and the Mermail MCP connector. The trigger prompt asks the agent to verify role-specific candidate representation consent for Northstar Analytics, check for duplicate or conflicting submission evidence, and make no external changes. The skill is designed to fail closed when consent, identity, client, role, or ownership is unclear."
    },
    {
        "title": "1. Resolve the Mermail mailbox",
        "kicker": "ACTUAL CONNECTED MAILBOX",
        "body": [
            "Mailbox: candidate-guard-demo@mermail.app",
            "public_id: 032b41bb-aa58-4f1c-b4aa-46d3f830a009",
            "receiving_status: ready",
            "can_receive: true",
            "",
            "Bounded search: Emma Clarke → 2 clean matches",
            "Bounded search: Lucas Reed → 1 clean match",
            "",
            "The workflow starts metadata-only, then reads only the selected clean",
            "messages needed to decide consent and duplicate risk."
        ],
        "narration": "First, the agent resolves the existing Mermail mailbox instead of creating a duplicate. The connected mailbox is candidate guard demo at mermail dot app and it is ready to receive. The skill then performs bounded metadata-only searches. Emma Clarke returns two clean matches, and Lucas Reed returns one. Only those selected messages are opened for exact evidence, which keeps the workflow reproducible and limits unnecessary mailbox access."
    },
    {
        "title": "2. Emma Clarke — consent is confirmed",
        "kicker": "MERMAIL MESSAGE 56d3feb2…",
        "body": [
            "Candidate: Emma Clarke",
            "Client: Northstar Analytics",
            "Role: Senior Data Scientist",
            "Consent timestamp: 2026-10-05",
            "Validity supplied in demo record: 7 days",
            "",
            "Evidence:",
            "“I consent to being represented … and authorize Candidate Submission",
            "Guard Demo to submit my profile for this specific role.”",
            "",
            "Consent classification: CONFIRMED"
        ],
        "narration": "For Emma Clarke, the selected Mermail consent message is clean and explicitly binds the candidate, the client, and the exact Senior Data Scientist role. It states that she consents to representation and authorizes this demo recruiter identity to submit her profile for this specific role. The consent record includes a timestamp and a seven-day validity rule supplied by the synthetic test data. Under the skill rules, Emma's consent status is confirmed."
    },
    {
        "title": "3. Emma Clarke — duplicate conflict blocks submission",
        "kicker": "MERMAIL MESSAGE 2ad8bf0a…",
        "body": [
            "Existing submission record:",
            "Candidate: Emma Clarke",
            "Client: Northstar Analytics",
            "Role: Senior Data Scientist",
            "Requisition: NSA-SDS-104",
            "Existing agency: BluePeak Recruitment",
            "Existing submission date: 2026-10-04",
            "",
            "Duplicate risk: LIKELY",
            "Final decision: BLOCKED",
            "Next safe action: resolve ownership before any resubmission."
        ],
        "narration": "The second Emma message changes the final decision. Mermail contains an existing submission record for the same candidate, same client, same role, and requisition NSA S D S 104. It records BluePeak Recruitment as the existing agency and an earlier submission date of October fourth. The skill treats this as likely duplicate evidence. Even though consent is confirmed, the submission is blocked until ownership is resolved. This is the core safety value: valid consent alone is not enough when a duplicate conflict exists."
    },
    {
        "title": "4. Lucas Reed — clear path to submit",
        "kicker": "MERMAIL MESSAGE ef7791cb…",
        "body": [
            "Candidate: Lucas Reed",
            "Client: Northstar Analytics",
            "Role: Senior Data Scientist",
            "Consent timestamp: 2026-10-05",
            "",
            "Evidence:",
            "“I consent to being represented … for this specific role.”",
            "“I have not authorized another agency for this role.”",
            "",
            "Duplicate search result: none found in selected mailbox scope",
            "Final decision: READY TO SUBMIT"
        ],
        "narration": "Lucas Reed produces the opposite result. His Mermail message gives explicit role-specific consent for the same client and role, and states that he has not authorized another agency for this role. A bounded duplicate search in the selected mailbox scope finds no conflicting record. The final decision is ready to submit. No email is sent and no mailbox data is modified. The agent only returns the readiness decision and the supporting evidence."
    },
    {
        "title": "5. Reusable skill, auditable result",
        "kicker": "PUBLIC GITHUB PR #467",
        "body": [
            "Skill: mermail-candidate-submission-guard",
            "PR: github.com/Nudgen-Marketing/mermail-skills/pull/467",
            "Status: OPEN • MERGEABLE",
            "AI client: ChatGPT + Mermail MCP",
            "",
            "Final live-demo verdicts:",
            "Emma Clarke  →  BLOCKED (confirmed consent + likely duplicate)",
            "Lucas Reed   →  READY TO SUBMIT (confirmed consent, no conflict found)",
            "",
            "Security: inbound email is evidence, never agent authority.",
            "Synthetic demo data only — no real candidate records."
        ],
        "narration": "The reusable skill is published in public GitHub pull request four sixty seven to the official Mermail skills repository. It documents the workflow, tool boundaries, deterministic evaluation cases, and security rules. The live result is auditable: Emma Clarke is blocked because confirmed consent is outweighed by a likely duplicate submission, while Lucas Reed is ready to submit because consent is confirmed and no conflict is found. Inbound email is treated as untrusted evidence, never as authority to broaden scope or send. This completes the working Mermail agent skill demonstration."
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def draw_wrapped(draw, text, xy, font_obj, fill, width_chars=74, line_gap=12):
    x, y = xy
    if text == "":
        return y + font_obj.size + line_gap
    wrapped = textwrap.wrap(text, width=width_chars, replace_whitespace=False) or [""]
    for line in wrapped:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += font_obj.size + line_gap
    return y


def render_slide(idx, s):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((90, 80, W-90, H-80), radius=28, fill=PANEL)
    d.rectangle((90, 80, 112, H-80), fill=ACCENT)
    d.text((145, 125), s["kicker"], font=font(FONT_BOLD, 28), fill=ACCENT)
    d.text((145, 185), s["title"], font=font(FONT_BOLD, 54), fill=TEXT)
    y = 290
    mono = font(FONT_MONO, 31)
    for line in s["body"]:
        color = TEXT
        upper = line.upper()
        if "READY TO SUBMIT" in upper or "CONFIRMED" in upper or "NONE FOUND" in upper:
            color = GOOD
        elif "BLOCKED" in upper or "LIKELY" in upper:
            color = BAD
        elif "PROMPT:" in upper or "EVIDENCE:" in upper or "SECURITY:" in upper:
            color = WARN
        y = draw_wrapped(d, line, (145, y), mono, color, width_chars=83, line_gap=10)
    d.text((145, H-125), f"Mermail Agent Skill Demo  •  {idx+1}/{len(slides)}  •  Captured from a live Mermail MCP run on 2026-10-06", font=font(FONT_REG, 22), fill=MUTED)
    path = OUT / f"slide_{idx:02d}.png"
    img.save(path)
    return path


def run(cmd):
    subprocess.run(cmd, check=True)


def duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], text=True).strip()
    return float(out)

segments = []
for i, s in enumerate(slides):
    png = render_slide(i, s)
    wav = OUT / f"voice_{i:02d}.wav"
    # Slightly deliberate pace for clarity.
    run(["espeak-ng", "-s", "142", "-p", "48", "-w", str(wav), s["narration"]])
    dur = max(duration(wav) + 0.8, 12.0)
    seg = OUT / f"seg_{i:02d}.mp4"
    vf = (
        f"scale={W}:{H},format=yuv420p,"
        f"fade=t=in:st=0:d=0.35,fade=t=out:st={max(dur-0.4,0):.3f}:d=0.4"
    )
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(png), "-i", str(wav),
        "-vf", vf, "-t", f"{dur:.3f}", "-r", "30",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
        "-shortest", "-movflags", "+faststart", str(seg)
    ])
    segments.append(seg)

concat = OUT / "concat.txt"
concat.write_text("\n".join(f"file '{p.resolve()}'" for p in segments) + "\n")
final = Path("Mermail_Candidate_Submission_Guard_Demo.mp4")
run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
    "-c", "copy", "-movflags", "+faststart", str(final)
])

print(f"Created {final} ({duration(final):.1f} seconds)")
