# FastHTML Implementation of Open Gemini Canvas

This directory contains a FastHTML implementation of the Open Gemini Canvas application, migrated from the original Next.js/TypeScript version.

## Features

- **Server-rendered UI** using FastHTML components
- **Google Gemini AI integration** for intelligent post generation
- **Responsive design** with modern CSS styling
- **Real-time post generation** for LinkedIn and Twitter/X platforms
- **HTMX-powered interactivity** for seamless user experience

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your Google API keys
```

3. Run the application:
```bash
python main.py
```

The application will be available at `http://localhost:5001`

## Architecture

- **FastHTML**: Server-side rendering framework
- **Google Gemini AI**: Content generation
- **HTMX**: Dynamic UI updates
- **Pico CSS**: Styling framework

## Migration Notes

This FastHTML version maintains the same functionality as the original Next.js application while leveraging server-side rendering and Python-based components. Key changes include:

- React components → FastHTML FT components
- Client-side state → Server-side state management
- JavaScript interactivity → HTMX attributes
- TypeScript → Python

## API Keys

The application requires Google API keys for Gemini AI integration. Set these in the `.env` file:

- `GOOGLE_API_KEY`: Primary API key
- `GOOGLE_API_KEY_2`: Backup API key

## Usage

1. Enter a prompt in the chat input
2. Click "Send" to generate posts
3. View generated LinkedIn and Twitter/X posts in the main canvas area
4. Use quick action buttons for common prompts
