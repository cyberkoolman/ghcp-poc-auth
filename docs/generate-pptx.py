"""
Generate: GitHub Copilot for Developers — Getting Started
Outputs: docs/ghcp-getting-started.pptx
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
import copy

# ── Brand colours ──────────────────────────────────────────────────────────
GH_BLACK   = RGBColor(0x0D, 0x11, 0x17)   # GitHub dark bg
GH_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
GH_BLUE    = RGBColor(0x23, 0x8B, 0xE6)   # Copilot accent blue
GH_GREY    = RGBColor(0x30, 0x36, 0x3D)   # Slide body bg
ACCENT_GRN = RGBColor(0x2D, 0xBA, 0x4E)   # GitHub green
ACCENT_YLW = RGBColor(0xF7, 0x8C, 0x00)   # Warning / highlight
LIGHT_GREY = RGBColor(0xE8, 0xEC, 0xF0)   # Table alt row

W = Inches(13.333)   # widescreen 16:9
H = Inches(7.5)


def hex2rgb(h):
    h = h.lstrip('#')
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))


# ── Helpers ────────────────────────────────────────────────────────────────

def set_bg(slide, color: RGBColor):
    from pptx.oxml.ns import qn
    from lxml import etree
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, l, t, w, h, color: RGBColor, alpha=None):
    shape = slide.shapes.add_shape(1, l, t, w, h)   # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.line.fill.background()
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color
    return shape


def add_label(slide, text, l, t, w, h, size=20, bold=False, color=GH_WHITE,
              align=PP_ALIGN.LEFT, wrap=True):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf = txb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    return txb


def accent_bar(slide, color=GH_BLUE, height=Inches(0.06)):
    add_rect(slide, 0, 0, W, height, color)


def slide_number_tag(slide, num, total, color=GH_BLUE):
    add_label(slide, f"{num} / {total}",
              W - Inches(1.4), H - Inches(0.45), Inches(1.3), Inches(0.35),
              size=11, color=RGBColor(0x88,0x92,0x9A), align=PP_ALIGN.RIGHT)


# ── Slide builders ─────────────────────────────────────────────────────────

def slide_title(prs, title, subtitle):
    layout = prs.slide_layouts[6]   # blank
    sl = prs.slides.add_slide(layout)
    set_bg(sl, GH_BLACK)
    # left accent strip
    add_rect(sl, 0, 0, Inches(0.18), H, GH_BLUE)
    # copilot gradient panel
    add_rect(sl, Inches(0.18), 0, W - Inches(0.18), H, GH_BLACK)
    # decorative circle
    circ = sl.shapes.add_shape(9, W - Inches(4.2), Inches(-1.5), Inches(6), Inches(6))
    circ.fill.solid(); circ.fill.fore_color.rgb = RGBColor(0x1A,0x22,0x2E)
    circ.line.fill.background()
    # title
    add_label(sl, title,
              Inches(0.6), Inches(1.8), Inches(9), Inches(1.8),
              size=44, bold=True, color=GH_WHITE)
    # blue underline
    add_rect(sl, Inches(0.6), Inches(3.55), Inches(2.2), Inches(0.07), GH_BLUE)
    # subtitle
    add_label(sl, subtitle,
              Inches(0.6), Inches(3.75), Inches(9.5), Inches(1.0),
              size=22, color=RGBColor(0xA0,0xAA,0xB4))
    # footer tag
    add_label(sl, "github.com/features/copilot",
              Inches(0.6), H - Inches(0.65), Inches(5), Inches(0.4),
              size=13, color=RGBColor(0x55,0x60,0x6A))
    return sl


def slide_section(prs, number, title, color=GH_BLUE):
    layout = prs.slide_layouts[6]
    sl = prs.slides.add_slide(layout)
    set_bg(sl, GH_BLACK)
    add_rect(sl, 0, 0, Inches(0.18), H, color)
    add_label(sl, f"SECTION  {number:02d}", Inches(0.5), Inches(2.4), Inches(10), Inches(0.5),
              size=14, color=color)
    add_label(sl, title, Inches(0.5), Inches(2.9), Inches(11), Inches(1.4),
              size=40, bold=True, color=GH_WHITE)
    add_rect(sl, Inches(0.5), Inches(4.35), Inches(1.6), Inches(0.06), color)
    return sl


def slide_content(prs, title, bullets, total, num,
                  bg=GH_GREY, note=None, code_block=None):
    layout = prs.slide_layouts[6]
    sl = prs.slides.add_slide(layout)
    set_bg(sl, bg)
    accent_bar(sl)
    add_label(sl, title,
              Inches(0.55), Inches(0.22), Inches(11.5), Inches(0.7),
              size=26, bold=True, color=GH_WHITE)
    add_rect(sl, Inches(0.55), Inches(0.95), Inches(11.2), Inches(0.03), GH_BLUE)

    if code_block:
        # split area: bullets left, code right
        bw = Inches(5.4)
        add_bullets(sl, bullets, Inches(0.55), Inches(1.1), bw, Inches(5.6))
        add_rect(sl, Inches(6.2), Inches(1.05), Inches(6.8), Inches(5.7), GH_BLACK)
        add_label(sl, code_block,
                  Inches(6.35), Inches(1.2), Inches(6.55), Inches(5.4),
                  size=12, color=RGBColor(0xA8,0xCC,0x88), wrap=True)
    else:
        add_bullets(sl, bullets, Inches(0.55), Inches(1.1), Inches(12.2), Inches(5.6))

    if note:
        add_rect(sl, Inches(0.55), H - Inches(1.0), Inches(12.2), Inches(0.7),
                 RGBColor(0x1A,0x2A,0x3A))
        add_label(sl, f"💡  {note}",
                  Inches(0.7), H - Inches(0.98), Inches(12.0), Inches(0.62),
                  size=13, color=RGBColor(0xA0,0xC8,0xF0))
    slide_number_tag(sl, num, total)
    return sl


def add_bullets(slide, bullets, l, t, w, h):
    txb = slide.shapes.add_textbox(l, t, w, h)
    tf = txb.text_frame
    tf.word_wrap = True
    first = True
    for item in bullets:
        # item can be str  →  normal bullet
        #              (str, int) → (text, indent_level)
        if isinstance(item, tuple):
            text, level = item
        else:
            text, level = item, 0

        if first:
            p = tf.paragraphs[0]
            first = False
        else:
            p = tf.add_paragraph()

        p.level = level
        p.space_before = Pt(4 if level == 0 else 2)
        run = p.add_run()
        run.text = ("    " * level + ("• " if level == 0 else "◦ ")) + text
        run.font.size = Pt(17 if level == 0 else 15)
        run.font.bold = (level == 0)
        run.font.color.rgb = GH_WHITE if level == 0 else RGBColor(0xC0,0xCA,0xD4)


def slide_two_col(prs, title, left_head, left_items, right_head, right_items, total, num):
    layout = prs.slide_layouts[6]
    sl = prs.slides.add_slide(layout)
    set_bg(sl, GH_GREY)
    accent_bar(sl)
    add_label(sl, title,
              Inches(0.55), Inches(0.22), Inches(11.5), Inches(0.7),
              size=26, bold=True, color=GH_WHITE)
    add_rect(sl, Inches(0.55), Inches(0.95), Inches(11.2), Inches(0.03), GH_BLUE)

    col_w = Inches(5.8)
    # left column
    add_rect(sl, Inches(0.55), Inches(1.1), col_w, Inches(0.42), GH_BLUE)
    add_label(sl, left_head, Inches(0.65), Inches(1.12), col_w-Inches(0.2), Inches(0.38),
              size=15, bold=True)
    add_bullets(sl, left_items, Inches(0.55), Inches(1.6), col_w, Inches(5.0))

    # right column
    rx = Inches(6.95)
    add_rect(sl, rx, Inches(1.1), col_w, Inches(0.42), ACCENT_GRN)
    add_label(sl, right_head, rx+Inches(0.1), Inches(1.12), col_w-Inches(0.2), Inches(0.38),
              size=15, bold=True)
    add_bullets(sl, right_items, rx, Inches(1.6), col_w, Inches(5.0))

    slide_number_tag(sl, num, total)
    return sl


def slide_table(prs, title, headers, rows, total, num):
    from pptx.util import Inches, Pt
    layout = prs.slide_layouts[6]
    sl = prs.slides.add_slide(layout)
    set_bg(sl, GH_GREY)
    accent_bar(sl)
    add_label(sl, title,
              Inches(0.55), Inches(0.22), Inches(11.5), Inches(0.7),
              size=26, bold=True, color=GH_WHITE)
    add_rect(sl, Inches(0.55), Inches(0.95), Inches(11.2), Inches(0.03), GH_BLUE)

    cols = len(headers)
    col_w = [Inches(v) for v in ([2.8] + [(13.333-0.55-0.55-2.8)/(cols-1)]*(cols-1))]
    row_h = Inches(0.52)
    top = Inches(1.1)

    table = sl.shapes.add_table(len(rows)+1, cols,
                                Inches(0.55), top,
                                Inches(12.23), row_h*(len(rows)+1)).table
    table.columns[0].width = col_w[0]
    for ci in range(1, cols):
        table.columns[ci].width = col_w[ci]

    def set_cell(cell, text, bg, fg=GH_WHITE, bold=False, size=14):
        cell.fill.solid()
        cell.fill.fore_color.rgb = bg
        tf = cell.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.LEFT
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = fg

    for ci, h in enumerate(headers):
        set_cell(table.cell(0, ci), h, GH_BLUE, bold=True, size=14)
    for ri, row in enumerate(rows):
        bg = RGBColor(0x23,0x2B,0x33) if ri % 2 == 0 else RGBColor(0x1C,0x23,0x2A)
        for ci, val in enumerate(row):
            set_cell(table.cell(ri+1, ci), val, bg, size=13)

    slide_number_tag(sl, num, total)
    return sl


def slide_code(prs, title, description, code, total, num):
    layout = prs.slide_layouts[6]
    sl = prs.slides.add_slide(layout)
    set_bg(sl, GH_GREY)
    accent_bar(sl)
    add_label(sl, title,
              Inches(0.55), Inches(0.22), Inches(11.5), Inches(0.7),
              size=26, bold=True, color=GH_WHITE)
    add_rect(sl, Inches(0.55), Inches(0.95), Inches(11.2), Inches(0.03), GH_BLUE)
    add_label(sl, description,
              Inches(0.55), Inches(1.05), Inches(12.2), Inches(0.7),
              size=16, color=RGBColor(0xA0,0xAA,0xB4))
    # code box
    add_rect(sl, Inches(0.55), Inches(1.75), Inches(12.2), Inches(5.3), GH_BLACK)
    add_label(sl, code,
              Inches(0.75), Inches(1.85), Inches(11.8), Inches(5.1),
              size=13, color=RGBColor(0xA8,0xCC,0x88), wrap=True)
    slide_number_tag(sl, num, total)
    return sl


def slide_closing(prs, total):
    layout = prs.slide_layouts[6]
    sl = prs.slides.add_slide(layout)
    set_bg(sl, GH_BLACK)
    add_rect(sl, 0, 0, Inches(0.18), H, GH_BLUE)
    add_label(sl, "Start Today",
              Inches(0.6), Inches(1.6), Inches(10), Inches(1.2),
              size=46, bold=True, color=GH_WHITE)
    add_rect(sl, Inches(0.6), Inches(2.85), Inches(2.0), Inches(0.07), GH_BLUE)
    steps = [
        "1.  Install GitHub Copilot extension in VS Code",
        "2.  Sign in with your GitHub account",
        "3.  Open Chat  →  try  /plan  with your next task",
        "4.  Use  /init  to generate workspace instructions",
        "5.  Create a  /create-instructions  for team conventions",
    ]
    add_bullets(sl, steps, Inches(0.6), Inches(3.05), Inches(11.5), Inches(3.5))
    add_label(sl, "github.com/features/copilot  •  docs.github.com/copilot",
              Inches(0.6), H - Inches(0.6), Inches(11), Inches(0.4),
              size=13, color=RGBColor(0x55,0x60,0x6A))
    slide_number_tag(sl, total, total)
    return sl


# ── Main ───────────────────────────────────────────────────────────────────

def build():
    prs = Presentation()
    prs.slide_width  = W
    prs.slide_height = H

    TOTAL = 18   # update if adding/removing slides

    # 1 — Title
    slide_title(prs,
        "GitHub Copilot\nfor Developers",
        "From zero to /plan — a practical introduction")

    # 2 — Agenda
    slide_content(prs, "Agenda", [
        "What is GitHub Copilot?",
        "The Copilot Chat interface",
        "Built-in slash commands ( /plan, /init, /create-* )",
        "How /plan works — under the hood",
        "Customisation primitives ( instructions, prompts, skills, agents, hooks )",
        "Live walkthrough — OAuth2 + JWT auth system PoC",
        "Best practices & security considerations",
        "Getting started checklist",
    ], TOTAL, 2)

    # 3 — Section: What is GitHub Copilot?
    slide_section(prs, 1, "What is GitHub Copilot?")

    # 4 — What it is
    slide_content(prs, "GitHub Copilot — Overview", [
        "AI pair programmer built into VS Code, JetBrains, Visual Studio, and the CLI",
        "Powered by large language models (Claude Sonnet 4.6 in Copilot Chat)",
        "Two main surfaces:",
        ("Inline completions — code suggested as you type", 1),
        ("Copilot Chat — conversational agent with tool use", 1),
        "Agent mode: can read files, run commands, edit code, run tests — autonomously",
        "Customisable via instructions, prompts, skills, agents and hooks",
    ], TOTAL, 4,
    note="This session focuses on Copilot Chat in agent mode — the most powerful surface.")

    # 5 — Section: Slash Commands
    slide_section(prs, 2, "Built-in Slash Commands", color=ACCENT_GRN)

    # 6 — Slash commands table
    slide_table(prs, "Built-in Slash Commands ( /  in Chat )",
        ["Command", "Purpose", "What it does"],
        [
            ["/plan",                "Research & planning",     "Interviews you, then produces a phased implementation plan"],
            ["/init",                "Workspace bootstrap",     "Scans your codebase and generates copilot-instructions.md"],
            ["/create-agent",        "Custom agent",            "Guides creation of a .agent.md specialized persona"],
            ["/create-instructions", "Coding conventions",      "Creates a .instructions.md rule file from conversation context"],
            ["/create-prompt",       "Reusable prompt",         "Packages a repeated task pattern as a .prompt.md slash command"],
            ["/create-skill",        "Workflow skill",          "Bundles a multi-step workflow into a SKILL.md with assets"],
            ["/create-hook",         "Lifecycle hook",          "Creates a .json hook to enforce policy at agent lifecycle events"],
        ],
        TOTAL, 6)

    # 7 — Section: How /plan Works
    slide_section(prs, 3, "How  /plan  Works — Under the Hood", color=ACCENT_YLW)

    # 8 — The template is minimal
    slide_code(prs,
        "The /plan Template File",
        "assets/prompts/plan.prompt.md  inside the Copilot Chat extension:",
        "---\nname: plan\ndescription: Research and plan with the Plan agent\nagent: Plan\nargument-hint: Describe what you want to plan or research\n---\n\nPlan my task.",
        TOTAL, 8)

    # 9 — What the Plan agent actually does
    slide_content(prs, "What the Plan Agent Actually Does", [
        "The template is just a routing declaration — 7 lines",
        "All intelligence comes from the built-in Plan agent mode",
        "Step-by-step process:",
        ("Parses your request to identify domain and implied requirements", 1),
        ("Identifies missing decisions → generates targeted questionnaire", 1),
        ("Maps answers to concrete technologies and patterns", 1),
        ("Produces a sequenced, dependency-ordered implementation plan", 1),
        ("Saves plan to session memory so it persists through the whole session", 1),
        "The questionnaire answers shape every downstream decision",
    ], TOTAL, 9,
    note="The agent knows what it doesn't know — it asks before it acts.")

    # 10 — PoC walkthrough
    slide_two_col(prs,
        "PoC Walkthrough — OAuth2 + JWT Auth System",
        "The Questionnaire",
        [
            "Framework?  →  .NET / ASP.NET Core",
            "OAuth provider?  →  Google",
            "OAuth flow?  →  Authorization Code Flow",
            "Token storage?  →  Redis",
            "Frontend?  →  React SPA",
            "Token strategy?  →  Access + Refresh tokens",
        ],
        "The 6-Phase Plan Generated",
        [
            "Phase 1 — Scaffold solution & projects",
            "Phase 2 — Config, packages, JwtSettings",
            "Phase 3 — TokenService + RedisRefreshTokenStore",
            "Phase 4 — AuthController (5 endpoints)",
            "Phase 5 — React frontend + axios interceptor",
            "Phase 6 — Security hardening",
        ],
        TOTAL, 10)

    # 11 — Section: Customisation Primitives
    slide_section(prs, 4, "Customisation Primitives", color=GH_BLUE)

    # 12 — Decision table
    slide_table(prs, "Which Primitive Should I Use?",
        ["Primitive", "File", "Location", "When to Use"],
        [
            ["Workspace Instructions", "copilot-instructions.md", ".github/",           "Always-on rules for every task in the project"],
            ["File Instructions",      "*.instructions.md",       ".github/instructions/","Rules scoped to file types or task contexts"],
            ["Prompts",                "*.prompt.md",             ".github/prompts/",   "Single focused reusable task with inputs"],
            ["Hooks",                  "*.json",                  ".github/hooks/",     "Deterministic enforcement via shell at lifecycle events"],
            ["Custom Agents",          "*.agent.md",              ".github/agents/",    "Specialized persona with restricted tools"],
            ["Skills",                 "SKILL.md",                ".github/skills/",    "Multi-step workflow with bundled assets"],
        ],
        TOTAL, 12)

    # 13 — Decision shortcuts
    slide_content(prs, "Customisation Decision Shortcuts", [
        "Instructions vs Skill?",
        ("Applies to most work → Instructions", 1),
        ("On-demand specialist task → Skill", 1),
        "Skill vs Prompt?",
        ("Multi-step workflow with scripts/templates → Skill", 1),
        ("Single focused task → Prompt", 1),
        "Skill vs Custom Agent?",
        ("Same tools throughout → Skill", 1),
        ("Need context isolation or different tools per stage → Custom Agent", 1),
        "Hooks vs Instructions?",
        ("Instructions guide (non-deterministic) → Instructions", 1),
        ("Must block/enforce via shell commands (deterministic) → Hook", 1),
    ], TOTAL, 13)

    # 14 — Section: Best Practices
    slide_section(prs, 5, "Best Practices & Security", color=ACCENT_GRN)

    # 15 — Best practices
    slide_two_col(prs,
        "Best Practices",
        "Effective Prompting",
        [
            "Be specific about stack, constraints, and goals",
            "Answer questionnaires completely — vague answers → vague plans",
            "Use /init first on any new repo",
            "Create .instructions.md for team conventions so every developer gets the same results",
            "Review every generated file before committing",
        ],
        "Common Pitfalls",
        [
            "Description field is the discovery surface — if keywords aren't in the description, the agent won't load the skill/instruction",
            "YAML frontmatter silently fails on unescaped colons or tabs",
            "Don't commit appsettings with real secrets",
            "Don't use applyTo: '**' — too broad",
            "Hooks enforce; instructions guide — don't confuse the two",
        ],
        TOTAL, 15)

    # 16 — Security note
    slide_content(prs, "Security Considerations with Copilot", [
        "Generated code is a starting point — always review for OWASP Top 10",
        "Copilot will not generate or store your actual secrets",
        "Use dotnet user-secrets / environment variables — never hardcode",
        "The agent follows your instructions — write secure instructions",
        "Sensitive patterns to always check in generated code:",
        ("SQL queries — parameterised? No string concatenation?", 1),
        ("JWT validation — algorithm pinned? Signature verified?", 1),
        ("Cookie flags — HttpOnly, Secure, SameSite set?", 1),
        ("CORS — locked to known origins, not wildcard *?", 1),
        ("Input validation — at system boundaries only, not deep in business logic?", 1),
    ], TOTAL, 16,
    note="Copilot in this PoC generated RS256 JWT, HttpOnly cookies, Lua atomics, rate limiting, and security headers — but you should still review.")

    # 17 — Obstacles & Lessons Learned
    slide_table(prs, "Real Obstacles — Lessons from the PoC",
        ["Problem", "Root Cause", "Fix"],
        [
            [".sln file not found",               ".NET 10 creates .slnx not .sln",               "Use AuthSystem.slnx"],
            ["NuGet version conflicts",            "Projects targeted net8.0, SDK was 10",          "Upgrade .csproj to net10.0"],
            ["Authentication.Google not found",   "No longer implicit in .NET 10",                 "Add NuGet package explicitly"],
            ["npm --template flag intercepted",   "npm consumed flag before passing to create-vite","Use npx -y create-vite@latest -- --template"],
            ["300+ missing IDatabase members",    "StackExchange.Redis v2.11 large interface",      "Replace hand-rolled fake with Moq"],
            ["Moq StringSetAsync mismatch",        "Implicit overload vs explicit 5-param overload","Change prod code to explicit overload"],
        ],
        TOTAL, 17)

    # 18 — Closing
    slide_closing(prs, TOTAL)

    out = r"c:\Projects\GHCP\docs\ghcp-getting-started.pptx"
    prs.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    build()
