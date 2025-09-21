#!/usr/bin/env python3

import os
import json
import asyncio
from typing import Dict, List, Optional
from fasthtml.common import *
from fasthtml.components import *
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Set up the FastHTML app
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
        Link(rel="stylesheet", href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"),
        Style("""
            :root {
                --primary-color: #3b82f6;
                --secondary-color: #8b5cf6;
                --accent-color: #ec4899;
                --background-gradient: linear-gradient(135deg, #f8fafc 0%, #e0e7ff 50%, #e0f2fe 100%);
            }
            
            body {
                background: var(--background-gradient);
                min-height: 100vh;
            }
            
            .sidebar {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(20px);
                border-right: 1px solid rgba(229, 231, 235, 0.5);
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
                width: 320px;
                min-height: 100vh;
                position: fixed;
                left: 0;
                top: 0;
                overflow-y: auto;
            }
            
            .main-content {
                margin-left: 320px;
                min-height: 100vh;
                padding: 0;
            }
            
            .header {
                background: rgba(255, 255, 255, 0.8);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(229, 231, 235, 0.5);
                padding: 1.5rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            
            .canvas-area {
                padding: 1.5rem;
                min-height: calc(100vh - 120px);
            }
            
            .gradient-text {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .gradient-bg {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
            }
            
            .post-card {
                background: rgba(255, 255, 255, 0.9);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(229, 231, 235, 0.5);
                border-radius: 12px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
            }
            
            .quick-action-btn {
                background: rgba(255, 255, 255, 0.5);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(229, 231, 235, 0.5);
                border-radius: 12px;
                padding: 1.5rem;
                text-align: center;
                transition: all 0.3s ease;
                cursor: pointer;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 0.75rem;
            }
            
            .quick-action-btn:hover {
                background: rgba(255, 255, 255, 0.7);
                transform: translateY(-2px);
                box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.15);
            }
            
            .agent-selector {
                background: rgba(255, 255, 255, 0.5);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(229, 231, 235, 0.5);
                border-radius: 12px;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            .chat-input {
                background: rgba(255, 255, 255, 0.9);
                border: 1px solid rgba(229, 231, 235, 0.5);
                border-radius: 12px;
                padding: 1rem;
                resize: vertical;
                min-height: 80px;
            }
            
            .send-btn {
                background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
                border: none;
                border-radius: 12px;
                color: white;
                padding: 0.75rem 1.5rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .send-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.5);
            }
            
            .status-badge {
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 600;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .pulse {
                width: 8px;
                height: 8px;
                background: white;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .columns-layout {
                display: flex;
                gap: 1.5rem;
                min-height: 100%;
            }
            
            .linkedin-column {
                flex: 3;
            }
            
            .twitter-column {
                flex: 1;
            }
        """)
    )
)

# Global state
app_state = {
    "current_agent": "post_generation_agent",
    "is_generating": False,
    "posts": {
        "linkedin": {"title": "", "content": ""},
        "twitter": {"title": "", "content": ""}
    },
    "show_posts": False,
    "chat_messages": []
}

# Agent configurations
agents = [
    {
        "id": "post_generation_agent",
        "name": "Post Generator",
        "description": "Generate posts for LinkedIn and X with Gemini and Google web search",
        "icon": "fas fa-search",
        "gradient": "linear-gradient(135deg, #3b82f6, #8b5cf6)"
    },
    {
        "id": "stack_analysis_agent", 
        "name": "Stack Analyst",
        "description": "Analyze the stack of a Project and generate insights from it",
        "icon": "fas fa-file-text",
        "gradient": "linear-gradient(135deg, #10b981, #059669)"
    }
]

# Quick actions
quick_actions = [
    {"label": "Recent Research", "icon": "fas fa-search", "color": "#3b82f6", "prompt": "Generate a post about recent research on String Theory"},
    {"label": "Recent News", "icon": "fas fa-newspaper", "color": "#10b981", "prompt": "Generate a post about recent news in United States"},
    {"label": "Post about Social Media", "icon": "fab fa-twitter", "color": "#8b5cf6", "prompt": "Generate a post about Instagram"},
    {"label": "Post about Stocks", "icon": "fas fa-chart-line", "color": "#f59e0b", "prompt": "Generate a post about Nvidia"}
]

def create_sidebar():
    """Create the sidebar component"""
    return Div(
        # Header section
        Div(
            Div(
                Div(
                    I(cls="fas fa-brain", style="color: white; font-size: 1.5rem;"),
                    style="width: 40px; height: 40px; background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899); border-radius: 12px; display: flex; align-items: center; justify-content: center; position: relative;"
                ),
                Div(
                    H1("Open Gemini Canvas", cls="gradient-text", style="font-size: 1.25rem; font-weight: bold; margin: 0;"),
                    P("Advanced AI Canvas", style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                    style="margin-left: 0.75rem;"
                ),
                style="display: flex; align-items: center; margin-bottom: 1rem;"
            ),
            
            # Agent selector
            Div(
                Label("Active Agent", style="font-size: 0.875rem; font-weight: 600; color: #374151; margin-bottom: 0.75rem; display: block;"),
                Div(
                    Div(
                        I(cls=agents[0]["icon"], style="color: white; font-size: 1rem;"),
                        style=f"width: 24px; height: 24px; background: {agents[0]['gradient']}; border-radius: 6px; display: flex; align-items: center; justify-content: center;"
                    ),
                    Span(agents[0]["name"], style="font-weight: 500; color: #111827; margin-left: 0.75rem;"),
                    style="display: flex; align-items: center;"
                ),
                cls="agent-selector"
            ),
            style="padding: 1rem; border-bottom: 1px solid rgba(229, 231, 235, 0.5); height: 160px;"
        ),
        
        # Chat area
        Div(
            Div(id="chat-messages", style="flex: 1; overflow-y: auto; padding: 1rem;"),
            
            # Chat input
            Form(
                Div(
                    Textarea(
                        placeholder="Type your message...",
                        name="message",
                        id="chat-input",
                        cls="chat-input",
                        style="width: 100%; margin-bottom: 0.75rem;"
                    ),
                    Button(
                        I(cls="fas fa-paper-plane", style="margin-right: 0.5rem;"),
                        "Send",
                        type="submit",
                        cls="send-btn",
                        style="width: 100%;"
                    ),
                    style="padding: 0 1rem 1rem 1rem;"
                ),
                hx_post="/send_message",
                hx_target="#main-content",
                hx_swap="innerHTML"
            ),
            style="display: flex; flex-direction: column; height: calc(100vh - 160px);"
        ),
        cls="sidebar"
    )

def create_header(is_generating=False):
    """Create the header component"""
    return Div(
        Div(
            Div(
                I(cls="fas fa-sparkles", style="color: white; font-size: 1.25rem;"),
                style="width: 32px; height: 32px; background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899); border-radius: 8px; display: flex; align-items: center; justify-content: center;"
            ),
            Div(
                H2("Posts Generation Canvas", cls="gradient-text", style="font-size: 1.5rem; font-weight: bold; margin: 0;"),
                P("Powered by Gemini AI & Google Web Search", style="font-size: 0.875rem; color: #6b7280; margin: 0;"),
                style="margin-left: 1rem;"
            ),
            style="display: flex; align-items: center;"
        ),
        Div(
            Span(
                Div(cls="pulse"),
                "Live Research",
                cls="status-badge"
            ) if is_generating else "",
            style="display: flex; align-items: center; gap: 0.75rem;"
        ),
        style="display: flex; align-items: center; justify-content: space-between;",
        cls="header"
    )

def create_welcome_screen():
    """Create the welcome screen with quick actions"""
    return Div(
        Div(
            Div(
                I(cls="fas fa-brain", style="color: white; font-size: 2.5rem;"),
                style="width: 80px; height: 80px; background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899); border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 2rem auto; box-shadow: 0 20px 40px -10px rgba(59, 130, 246, 0.3);"
            ),
            H3("Ready to Explore", cls="gradient-text", style="font-size: 1.5rem; font-weight: bold; margin-bottom: 0.75rem; text-align: center;"),
            P("Harness the power of Google's most advanced AI models for generating interactive LinkedIn and X Posts.", 
              style="color: #6b7280; margin-bottom: 2rem; max-width: 400px; margin-left: auto; margin-right: auto; text-align: center; line-height: 1.6;"),
            
            # Quick actions grid
            Div(
                *[
                    Div(
                        I(cls=action["icon"], style=f"color: {action['color']}; font-size: 1.5rem;"),
                        Span(action["label"], style="font-size: 0.875rem; font-weight: 500;"),
                        cls="quick-action-btn",
                        hx_post="/send_message",
                        hx_vals=f'{{"message": "{action["prompt"]}"}}',
                        hx_target="#main-content",
                        hx_swap="innerHTML"
                    )
                    for action in quick_actions
                ],
                style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; max-width: 500px; margin: 0 auto;"
            ),
            style="text-align: center; padding: 4rem 0;"
        ),
        cls="canvas-area"
    )

def create_posts_view(linkedin_post, twitter_post):
    """Create the posts view with LinkedIn and Twitter columns"""
    return Div(
        Div(
            # LinkedIn column
            Div(
                create_linkedin_post(linkedin_post["title"], linkedin_post["content"]),
                cls="linkedin-column"
            ) if linkedin_post["content"] else "",
            
            # Twitter column  
            Div(
                create_twitter_post(twitter_post["title"], twitter_post["content"]),
                cls="twitter-column"
            ) if twitter_post["content"] else "",
            cls="columns-layout"
        ),
        cls="canvas-area"
    )

def create_linkedin_post(title, content):
    """Create LinkedIn post preview"""
    return Div(
        H3("LinkedIn Post", style="margin-bottom: 1rem; color: #0a66c2; font-weight: 600;"),
        Div(
            Div(
                Div(
                    Img(src="/api/placeholder/40/40", alt="Profile", style="width: 40px; height: 40px; border-radius: 50%;"),
                    Div(
                        Strong("DeepMind Research"),
                        Br(),
                        Small("AI Research Organization • 2h", style="color: #666;"),
                        style="margin-left: 0.75rem;"
                    ),
                    style="display: flex; align-items: center; margin-bottom: 1rem;"
                ),
                H4(title, style="margin-bottom: 0.75rem; color: #000;") if title else "",
                P(content, style="line-height: 1.6; color: #000; white-space: pre-wrap;"),
                Div(
                    Button(I(cls="fas fa-thumbs-up"), " Like", style="background: none; border: 1px solid #ccc; color: #666; padding: 0.5rem 1rem; border-radius: 20px; margin-right: 0.5rem;"),
                    Button(I(cls="fas fa-comment"), " Comment", style="background: none; border: 1px solid #ccc; color: #666; padding: 0.5rem 1rem; border-radius: 20px; margin-right: 0.5rem;"),
                    Button(I(cls="fas fa-share"), " Share", style="background: none; border: 1px solid #ccc; color: #666; padding: 0.5rem 1rem; border-radius: 20px;"),
                    style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee;"
                )
            ),
            cls="post-card"
        )
    )

def create_twitter_post(title, content):
    """Create Twitter post preview"""
    return Div(
        H3("X Post", style="margin-bottom: 1rem; color: #000; font-weight: 600;"),
        Div(
            Div(
                Div(
                    Img(src="/api/placeholder/40/40", alt="Profile", style="width: 40px; height: 40px; border-radius: 50%;"),
                    Div(
                        Strong("DeepMind Research"),
                        Span(" @deepmind_research", style="color: #666; margin-left: 0.25rem;"),
                        Br(),
                        Small("2h", style="color: #666;"),
                        style="margin-left: 0.75rem;"
                    ),
                    style="display: flex; align-items: flex-start; margin-bottom: 1rem;"
                ),
                H4(title, style="margin-bottom: 0.75rem; color: #000; font-size: 1rem;") if title else "",
                P(content, style="line-height: 1.5; color: #000; white-space: pre-wrap;"),
                Div(
                    Button(I(cls="fas fa-comment"), " 12", style="background: none; border: none; color: #666; padding: 0.25rem 0.5rem;"),
                    Button(I(cls="fas fa-retweet"), " 45", style="background: none; border: none; color: #666; padding: 0.25rem 0.5rem;"),
                    Button(I(cls="fas fa-heart"), " 234", style="background: none; border: none; color: #666; padding: 0.25rem 0.5rem;"),
                    Button(I(cls="fas fa-share"), "", style="background: none; border: none; color: #666; padding: 0.25rem 0.5rem;"),
                    style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee; display: flex; justify-content: space-around;"
                )
            ),
            cls="post-card"
        )
    )

@rt("/")
def get():
    """Main page route"""
    return Html(
        Head(
            Title("Open Gemini Canvas"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1")
        ),
        Body(
            create_sidebar(),
            Div(
                create_header(app_state["is_generating"]),
                Div(
                    create_welcome_screen() if not app_state["show_posts"] else create_posts_view(
                        app_state["posts"]["linkedin"], 
                        app_state["posts"]["twitter"]
                    ),
                    id="main-content"
                ),
                cls="main-content"
            ),
            Script(src="https://unpkg.com/htmx.org@1.9.10")
        )
    )

async def generate_posts_with_ai(prompt: str):
    """Generate posts using Google Gemini AI"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        system_prompt = f"""You are an advanced AI research agent powered by Google DeepMind and Gemini technologies. Generate both a LinkedIn post and a Twitter/X post based on the user's request: "{prompt}"

Please respond with a JSON object containing:
{{
    "linkedin": {{
        "title": "Professional title for LinkedIn post",
        "content": "Professional LinkedIn post content with relevant hashtags and insights"
    }},
    "twitter": {{
        "title": "",
        "content": "Engaging Twitter/X post content with relevant hashtags (under 280 characters)"
    }}
}}

Make the content engaging, professional, and relevant to the topic. Include appropriate hashtags and emojis where suitable."""

        response = model.generate_content(system_prompt)
        
        # Try to parse JSON response
        try:
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                posts_data = json.loads(json_match.group())
                return posts_data
        except:
            pass
        
        # Fallback if JSON parsing fails
        return {
            "linkedin": {
                "title": "AI-Generated Insights",
                "content": response.text[:500] + "\n\n#AI #Technology #Innovation"
            },
            "twitter": {
                "title": "",
                "content": response.text[:250] + " #AI #Tech"
            }
        }
        
    except Exception as e:
        print(f"AI generation error: {e}")
        # Fallback to mock data
        return {
            "linkedin": {
                "title": "AI-Powered Content Generation",
                "content": f"Exploring: {prompt}\n\nThe integration of advanced AI systems is transforming how we approach content creation and research.\n\n#AI #Innovation #Technology"
            },
            "twitter": {
                "title": "",
                "content": f"🤖 AI insights on {prompt}! The future of intelligent content creation is here. #AI #Tech #Innovation"
            }
        }

@rt("/send_message", methods=["POST"])
async def send_message(message: str):
    """Handle chat message submission"""
    app_state["is_generating"] = True
    app_state["chat_messages"].append({"role": "user", "content": message})
    
    # Generate posts using AI
    posts_data = await generate_posts_with_ai(message)
    
    app_state["posts"]["linkedin"] = posts_data["linkedin"]
    app_state["posts"]["twitter"] = posts_data["twitter"]
    
    app_state["show_posts"] = True
    app_state["is_generating"] = False
    
    # Return updated main content
    return Div(
        create_header(app_state["is_generating"]),
        Div(
            create_posts_view(
                app_state["posts"]["linkedin"], 
                app_state["posts"]["twitter"]
            ),
            id="main-content"
        ),
        cls="main-content"
    )

@rt("/api/placeholder/{width}/{height}")
def placeholder_image(width: int, height: int):
    """Serve placeholder images"""
    # Return a simple SVG placeholder
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#e5e7eb"/>
        <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#9ca3af">{width}x{height}</text>
    </svg>'''
    return Response(svg, media_type="image/svg+xml")

if __name__ == "__main__":
    serve(port=5002)
