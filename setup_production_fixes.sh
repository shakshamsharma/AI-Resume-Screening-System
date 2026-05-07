#!/bin/bash

# Production Fixes Setup Script
# This script installs dependencies and runs migrations

echo "🚀 Setting up Production-Grade ATS Platform..."
echo ""

# Check if we're in the right directory
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Step 1: Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Step 2: Check for database connection
echo "🗄️  Checking database connection..."
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  Warning: DATABASE_URL not set"
    echo "   Please set it in your .env file or environment"
    echo "   Example: DATABASE_URL=postgresql://user:pass@localhost/dbname"
else
    echo "✅ Database URL configured"
fi
echo ""

# Step 3: Run migrations
echo "🔄 Running database migrations..."
if [ -n "$DATABASE_URL" ]; then
    # Extract database connection details
    psql "$DATABASE_URL" -f migrations/add_parsing_confidence_and_recommendation.sql
    if [ $? -eq 0 ]; then
        echo "✅ Migrations completed successfully"
    else
        echo "⚠️  Migration failed - you may need to run it manually"
        echo "   Run: psql \$DATABASE_URL -f backend/migrations/add_parsing_confidence_and_recommendation.sql"
    fi
else
    echo "⚠️  Skipping migrations - DATABASE_URL not set"
    echo "   Run manually: psql your_db -f backend/migrations/add_parsing_confidence_and_recommendation.sql"
fi
echo ""

# Step 4: Check for AI API keys (optional)
echo "🤖 Checking AI configuration (optional)..."
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OpenAI API key configured"
elif [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ Anthropic API key configured"
else
    echo "ℹ️  No AI API keys found (optional)"
    echo "   System will use rule-based evaluation"
    echo "   To enable AI evaluation, set:"
    echo "   - OPENAI_API_KEY=sk-..."
    echo "   - OR ANTHROPIC_API_KEY=sk-ant-..."
fi
echo ""

# Step 5: Create upload directory
echo "📁 Creating upload directory..."
mkdir -p uploads
chmod 755 uploads
echo "✅ Upload directory ready"
echo ""

# Step 6: Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo "   1. Set environment variables (if not done):"
echo "      export DATABASE_URL=postgresql://user:pass@localhost/dbname"
echo "      export OPENAI_API_KEY=sk-... (optional)"
echo ""
echo "   2. Start the backend server:"
echo "      cd backend"
echo "      uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "   3. Start the frontend (in another terminal):"
echo "      cd frontend"
echo "      npm install"
echo "      npm run dev"
echo ""
echo "   4. Test the fixes:"
echo "      - Upload a resume"
echo "      - Check /api/resumes/debug/{resume_id}"
echo "      - Verify experience calculation"
echo ""
echo "📖 Documentation: See PRODUCTION_FIXES.md for details"
echo ""
