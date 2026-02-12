#!/bin/bash
# Run this script from inside the scotus-website folder
# Usage: bash setup.sh

echo "Creating SCOTUS Predictor website..."

# Initialize the project
npm create vite@latest . -- --template react
npm install

echo ""
echo "Setup complete! Next steps:"
echo "  1. Replace src/App.jsx with your scotus-predictor.jsx content"
echo "  2. Run: npm run dev"
echo "  3. Open http://localhost:5173 in your browser"
echo ""
echo "To deploy:"
echo "  1. Create a GitHub repo and push this folder"
echo "  2. Go to vercel.com, sign in with GitHub"
echo "  3. Import your repo — Vercel auto-detects Vite and deploys"
echo "  4. You get a free URL like scotus-predictor.vercel.app"
echo "  5. Later, connect a custom domain in Vercel settings"
