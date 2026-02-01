#!/bin/bash

# AURA API Test Script
# Run this to verify all endpoints are working

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🧪 Testing AURA Preprocessor 2.0 API"
echo "======================================"

# Test 1: Root endpoint
echo -e "\n📍 Test 1: Root Endpoint"
curl -s "$BASE_URL/" | jq '.' || echo -e "${RED}❌ Failed${NC}"

# Test 2: Health check
echo -e "\n📍 Test 2: Health Check"
curl -s "$BASE_URL/api/health" | jq '.' || echo -e "${RED}❌ Failed${NC}"

# Test 3: System status
echo -e "\n📍 Test 3: System Status"
curl -s "$BASE_URL/api/status" | jq '.system.cpu' || echo -e "${RED}❌ Failed${NC}"

# Test 4: Service metrics
echo -e "\n📍 Test 4: Service Metrics"
curl -s "$BASE_URL/api/metrics" | jq '.jobs' || echo -e "${RED}❌ Failed${NC}"

# Test 5: List jobs
echo -e "\n📍 Test 5: List Pipeline Jobs"
curl -s "$BASE_URL/api/pipeline/jobs" | jq '.' || echo -e "${RED}❌ Failed${NC}"

# Test 6: List background jobs
echo -e "\n📍 Test 6: List Background Jobs"
curl -s "$BASE_URL/api/jobs/" | jq '.' || echo -e "${RED}❌ Failed${NC}"

# Test 7: Upload and process (if titanic.csv exists)
if [ -f "data/titanic.csv" ]; then
    echo -e "\n📍 Test 7: Pipeline Execution (titanic.csv)"
    RESPONSE=$(curl -s -X POST "$BASE_URL/api/pipeline/run" \
        -F "file=@data/titanic.csv" \
        -F "mode=auto" \
        -F "target_col=Survived")
    
    echo "$RESPONSE" | jq '.'
    
    # Extract job_id for further tests
    JOB_ID=$(echo "$RESPONSE" | jq -r '.job_id')
    
    if [ "$JOB_ID" != "null" ]; then
        echo -e "\n${GREEN}✅ Pipeline executed! Job ID: $JOB_ID${NC}"
        
        # Test download endpoints
        echo -e "\n📍 Test 8: Download Report"
        curl -s "$BASE_URL/api/pipeline/download/$JOB_ID/report" | jq '.' | head -20
        
        echo -e "\n📍 Test 9: Get Job Info"
        curl -s "$BASE_URL/api/pipeline/info/$JOB_ID" | jq '.report.pipeline_info' || echo "Report not ready yet"
    else
        echo -e "${RED}❌ Pipeline execution failed${NC}"
    fi
else
    echo -e "\n⚠️  Test 7 skipped: data/titanic.csv not found"
fi

echo -e "\n======================================"
echo -e "✅ API testing complete!"
echo -e "\n🌐 Visit http://localhost:8000/docs for interactive API docs"