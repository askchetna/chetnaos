# Chetna-GPT Smoke Test Script
# Tests basic functionality without requiring GROQ_API_KEY

Write-Host "🧪 Running Chetna-GPT Smoke Tests..." -ForegroundColor Green

# Test 1: Health endpoint
Write-Host "`n1. Testing /health endpoint..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
    if ($healthResponse.ok -eq $true) {
        Write-Host "✅ Health check passed: $($healthResponse | ConvertTo-Json)" -ForegroundColor Green
    } else {
        Write-Host "❌ Health check failed: unexpected response" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Chat endpoint (empty text should return 400)
Write-Host "`n2. Testing /api/chat endpoint..." -ForegroundColor Yellow
try {
    $chatBody = @{ text = "" } | ConvertTo-Json
    $chatResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/chat" -Method Post -ContentType "application/json" -Body $chatBody
    Write-Host "✅ Chat endpoint accessible: $($chatResponse | ConvertTo-Json)" -ForegroundColor Green
} catch {
  if ($_.Exception.Response.StatusCode.value__ -eq 400) {
    Write-Host "✅ Chat endpoint validation OK (400 on empty text)" -ForegroundColor Green
  } else {
    Write-Host "❌ Chat endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
  }
}

# Test 3: Agent endpoint (should work without API key for search messages)
Write-Host "`n3. Testing /api/agent endpoint..." -ForegroundColor Yellow
try {
    $agentBody = @{ message = "search test" } | ConvertTo-Json
    $agentResponse = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/agent" -Method Post -ContentType "application/json" -Body $agentBody
    Write-Host "✅ Agent endpoint accessible: $($agentResponse | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Agent endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Memory persistence (organism MemoryStore via Python gate — no HTTP mem routes)
Write-Host "`n4. Testing memory persistence (phase1 gate)..." -ForegroundColor Yellow
try {
    python scripts/phase1_gate.py 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Memory persistence gate passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Memory persistence gate failed (exit $LASTEXITCODE)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Memory gate failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Smoke tests completed!" -ForegroundColor Green
Write-Host "Note: Full functionality requires GROQ_API_KEY in .env file" -ForegroundColor Cyan
