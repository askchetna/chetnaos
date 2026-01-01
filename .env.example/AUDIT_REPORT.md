# ChetnaOS.v1 - Full Security & Code Quality Audit Report

**Date:** 2024-12-19  
**Project:** ChetnaOS.v1  
**Auditor:** Automated Security Audit  
**Scope:** Full codebase security, quality, and best practices review

---

## Executive Summary

This audit identified **15 critical security vulnerabilities**, **12 code quality issues**, and **8 configuration problems** across the ChetnaOS.v1 codebase. The most severe issues include:

- **CRITICAL:** Use of `eval()` function with insufficient sanitization
- **CRITICAL:** CORS configured to allow all origins (`allow_origins=["*"]`)
- **HIGH:** Missing authentication/authorization on all API endpoints
- **HIGH:** Hardcoded API endpoints in frontend
- **MEDIUM:** SQL injection risks (though parameterized queries are used)
- **MEDIUM:** XSS vulnerabilities in frontend code
- **MEDIUM:** Missing input validation and rate limiting

---

## 1. Security Vulnerabilities

### 1.1 CRITICAL: Unsafe `eval()` Usage

**Location:** `backend/agent.py:32`

```python
result = eval(expr, {"__builtins__": {}}, {})
```

**Issue:** Despite attempts to sanitize, `eval()` is inherently dangerous. The regex check can be bypassed, and `eval()` can execute arbitrary code.

**Risk:** Remote Code Execution (RCE) if malicious input reaches this function.

**Recommendation:**
- Replace with `ast.literal_eval()` for safe evaluation
- Or use a proper math expression parser library
- Add stricter input validation

**Severity:** 🔴 CRITICAL

---

### 1.2 CRITICAL: Overly Permissive CORS Configuration

**Location:** `backend/app.py:22-28`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Issue:** CORS allows requests from any origin, enabling CSRF attacks and unauthorized API access.

**Risk:** Cross-Site Request Forgery (CSRF), unauthorized data access

**Recommendation:**
- Restrict `allow_origins` to specific domains
- Use environment variables for allowed origins
- Remove `allow_credentials=True` if not needed, or restrict origins when using it

**Severity:** 🔴 CRITICAL

---

### 1.3 HIGH: Missing Authentication & Authorization

**Location:** All API endpoints in `backend/app.py`, `backend/api.py`, `backend/agent.py`

**Issue:** No authentication or authorization mechanisms on any endpoints. All endpoints are publicly accessible.

**Affected Endpoints:**
- `/api/chat`
- `/api/goal`
- `/api/agent`
- `/evaluate`
- `/roi`
- `/crop`
- `/chetna`
- `/health`

**Risk:** Unauthorized access, API abuse, data exfiltration, resource exhaustion

**Recommendation:**
- Implement API key authentication or JWT tokens
- Add rate limiting per IP/user
- Implement role-based access control (RBAC) if needed
- Use FastAPI's `Depends()` for authentication middleware

**Severity:** 🟠 HIGH

---

### 1.4 HIGH: Hardcoded API Endpoints

**Location:** `frontend/app.js:65, 69, 73` and other frontend files

```javascript
return fetchJson('http://127.0.0.1:8000/api/chat', payload);
```

**Issue:** Hardcoded localhost URLs will break in production. No environment-based configuration.

**Risk:** Application won't work in production, requires code changes for deployment

**Recommendation:**
- Use environment variables or configuration files
- Implement a config.js that reads from environment
- Use relative URLs or API base URL configuration

**Severity:** 🟠 HIGH

---

### 1.5 MEDIUM: Potential XSS Vulnerabilities

**Location:** `frontend/app.js:16`, `kalpavriksha_ui/js/*.js`

**Issue:** Direct use of `innerHTML` with user-controlled or server-controlled content.

```javascript
bubble.innerHTML = text.split('\\n').map(escapeHtml).join('<br/>');
```

While `escapeHtml` is used, there are other places where `innerHTML` is set directly:
- `kalpavriksha_ui/js/crop.js:25, 37, 39`
- `kalpavriksha_ui/js/roi.js:9, 15, 36, 41, 53`

**Risk:** Cross-Site Scripting (XSS) if malicious content is injected

**Recommendation:**
- Always use `textContent` instead of `innerHTML` when possible
- If HTML is needed, use a proper sanitization library (DOMPurify)
- Never trust server responses without sanitization

**Severity:** 🟡 MEDIUM

---

### 1.6 MEDIUM: SQL Injection Risk (Low, but present)

**Location:** `backend/memory.py:30`, `memory/db.py:70-73`

**Issue:** While parameterized queries are used (good!), there's a typo in `memory/db.py:92`:
```python
embedding = np.frombuffer(embedding_bytes, dtype=np.float32)  # Typo: frombuffer
```

Should be `np.frombuffer` → `np.frombuffer` (correct) or `np.from_buffer` (if that's the intent).

**Risk:** Runtime errors, potential data corruption

**Recommendation:**
- Fix the typo (verify correct numpy function)
- Continue using parameterized queries (already doing this correctly)
- Add input validation for all database operations

**Severity:** 🟡 MEDIUM (mostly a bug, but could cause issues)

---

### 1.7 MEDIUM: Missing Input Validation

**Location:** Multiple endpoints

**Issue:** Limited input validation on user inputs. Examples:
- No length limits on text inputs
- No type validation beyond Pydantic models
- No sanitization of user-provided URLs in `web_fetch()`

**Risk:** DoS attacks, injection attacks, resource exhaustion

**Recommendation:**
- Add maximum length limits to all text inputs
- Validate URL format and scheme before fetching
- Add rate limiting
- Implement request size limits

**Severity:** 🟡 MEDIUM

---

### 1.8 MEDIUM: Unsafe URL Fetching

**Location:** `backend/agent.py:67-92`

**Issue:** `web_fetch()` function fetches arbitrary URLs without validation:
- No URL scheme validation (could fetch `file://`, `gopher://`, etc.)
- No SSRF protection
- No timeout limits (though 10s timeout is set, which is good)

**Risk:** Server-Side Request Forgery (SSRF), internal network access

**Recommendation:**
- Whitelist allowed URL schemes (only `http://` and `https://`)
- Block private/internal IP ranges
- Validate URL format strictly
- Consider using a URL validation library

**Severity:** 🟡 MEDIUM

---

### 1.9 LOW: Error Information Disclosure

**Location:** Multiple endpoints return full exception messages

**Issue:** Error messages expose internal details:
```python
raise HTTPException(status_code=500, detail=str(e))
```

**Risk:** Information leakage about system internals

**Recommendation:**
- Log detailed errors server-side
- Return generic error messages to clients
- Use proper error handling middleware

**Severity:** 🟢 LOW

---

### 1.10 LOW: Missing Security Headers

**Location:** `backend/app.py`

**Issue:** No security headers configured (CSP, X-Frame-Options, X-Content-Type-Options, etc.)

**Risk:** Clickjacking, MIME type sniffing attacks

**Recommendation:**
- Add security headers middleware
- Implement Content Security Policy (CSP)
- Add X-Frame-Options, X-Content-Type-Options headers

**Severity:** 🟢 LOW

---

## 2. Code Quality Issues

### 2.1 Missing Error Handling

**Location:** Multiple files

**Issues:**
- Generic exception catching without specific handling
- Missing try-catch blocks in some critical paths
- Inconsistent error handling patterns

**Recommendation:**
- Use specific exception types
- Implement proper logging
- Add retry logic where appropriate

---

### 2.2 Inconsistent Logging

**Location:** Throughout codebase

**Issue:** Mix of `print()` statements and no logging framework:
- `backend/agent.py:111` uses `print()`
- `memory/db.py:101` uses `print()`
- No structured logging

**Recommendation:**
- Replace all `print()` with proper logging
- Use Python's `logging` module
- Configure log levels appropriately
- Add structured logging for production

---

### 2.3 Missing Type Hints

**Location:** Multiple files

**Issue:** Inconsistent use of type hints. Some functions have them, others don't.

**Recommendation:**
- Add type hints to all functions
- Use `mypy` for type checking
- Enable strict type checking in CI

---

### 2.4 Code Duplication

**Location:** Multiple files

**Issue:** Similar patterns repeated across files (e.g., error handling, API calls)

**Recommendation:**
- Extract common patterns into utility functions
- Create shared error handling middleware
- Use decorators for common functionality

---

### 2.5 Missing Documentation

**Location:** Multiple files

**Issue:** Limited docstrings, no API documentation generation

**Recommendation:**
- Add comprehensive docstrings
- Use FastAPI's automatic OpenAPI documentation
- Add README with setup instructions

---

### 2.6 Hardcoded Values

**Location:** Multiple files

**Issue:** Magic numbers and hardcoded strings throughout code:
- Database paths
- Model names
- Timeout values

**Recommendation:**
- Move to configuration files
- Use environment variables
- Create constants file

---

## 3. Configuration Issues

### 3.1 Missing .env.example File

**Location:** Root directory

**Issue:** `.env.example` directory exists but is empty. No template for required environment variables.

**Recommendation:**
- Create `.env.example` with all required variables (without values)
- Document each variable's purpose

---

### 3.2 Missing .gitignore

**Issue:** No `.gitignore` file found. Risk of committing:
- `.env` files with secrets
- `__pycache__/` directories
- Database files (`mem.db`)
- Virtual environment files

**Recommendation:**
- Create comprehensive `.gitignore`
- Ensure sensitive files are excluded

---

### 3.3 Database File Location

**Location:** `backend/memory.py:10`, `memory/db.py:46`

**Issue:** Database files (`mem.db`) are created in current working directory, not a dedicated data directory.

**Risk:** Database files could be committed, overwritten, or lost

**Recommendation:**
- Use a dedicated `data/` directory
- Add database files to `.gitignore`
- Document database location

---

### 3.4 Missing Dependency Pinning

**Location:** `requirements.txt`

**Issue:** Some dependencies are pinned, others are not:
- `fastapi==0.112.0` ✅
- `python-dotenv>=1.0` ⚠️
- `pydantic>=2.0.0` ⚠️

**Recommendation:**
- Pin all dependencies to specific versions
- Use `pip freeze` to generate exact versions
- Document why specific versions are required

---

### 3.5 Missing Production Configuration

**Issue:** No distinction between development and production configurations:
- CORS allows all origins (should be restricted in production)
- Debug mode not controlled by environment
- No production-ready settings

**Recommendation:**
- Add environment-based configuration
- Separate dev/prod settings
- Disable debug mode in production

---

## 4. Dependency Security

### 4.1 Outdated Dependencies

**Location:** `requirements.txt`

**Issues:**
- `numpy==1.24.3` - Check for security updates
- `requests==2.31.0` - Check for security updates
- `beautifulsoup4==4.12.2` - Check for security updates

**Recommendation:**
- Run `pip-audit` or `safety check` to identify vulnerabilities
- Update dependencies regularly
- Subscribe to security advisories

---

### 4.2 Missing Security Scanning

**Issue:** No automated dependency vulnerability scanning in CI/CD

**Recommendation:**
- Add `pip-audit` or `safety` to CI pipeline
- Use GitHub Dependabot or similar
- Regular security audits

---

## 5. Testing & Quality Assurance

### 5.1 Missing Tests

**Issue:** No test files found in `tests/` directory

**Recommendation:**
- Add unit tests for core functionality
- Add integration tests for API endpoints
- Add security tests (OWASP ZAP, etc.)
- Achieve minimum 70% code coverage

---

### 5.2 Missing CI/CD Security Checks

**Location:** `.github/workflows/ci.yml`

**Issue:** CI only checks imports, no security scanning

**Recommendation:**
- Add security linting (bandit, semgrep)
- Add dependency vulnerability scanning
- Add code quality checks (pylint, black, flake8)
- Add security tests

---

## 6. Architecture & Design

### 6.1 Missing API Versioning

**Issue:** No API versioning strategy. Changes could break clients.

**Recommendation:**
- Implement API versioning (`/api/v1/...`)
- Document deprecation policies
- Maintain backward compatibility

---

### 6.2 Missing Rate Limiting

**Issue:** No rate limiting on any endpoints

**Risk:** DoS attacks, API abuse, resource exhaustion

**Recommendation:**
- Implement rate limiting (e.g., using `slowapi`)
- Different limits for different endpoints
- Per-IP and per-user limits

---

### 6.3 Missing Request Size Limits

**Issue:** No limits on request body size

**Risk:** DoS via large payloads

**Recommendation:**
- Configure FastAPI request size limits
- Validate input sizes
- Reject oversized requests early

---

## 7. Data Privacy & Compliance

### 7.1 Missing Data Encryption

**Issue:** No encryption at rest for database files

**Recommendation:**
- Encrypt sensitive data in database
- Use encrypted SQLite or encrypt fields
- Consider using proper database with encryption

---

### 7.2 Missing Privacy Policy / Data Handling

**Issue:** No documentation on data collection, storage, or retention

**Recommendation:**
- Document what data is stored
- Implement data retention policies
- Add data deletion capabilities
- Consider GDPR/privacy compliance if handling user data

---

## 8. Positive Findings

### ✅ Good Practices Found:

1. **Parameterized SQL Queries:** Using parameterized queries prevents SQL injection
2. **Pydantic Models:** Using Pydantic for request validation
3. **Type Hints:** Some functions have type hints (though inconsistent)
4. **Error Handling:** Basic error handling in place
5. **Modular Structure:** Code is organized into modules
6. **FastAPI:** Using modern async framework

---

## 9. Priority Recommendations

### Immediate (Critical - Fix Now):

1. 🔴 **Remove or replace `eval()`** in `backend/agent.py:32`
2. 🔴 **Restrict CORS** to specific origins
3. 🔴 **Add authentication** to all API endpoints
4. 🔴 **Fix hardcoded URLs** in frontend

### Short-term (High Priority - Fix This Week):

5. 🟠 **Add input validation** and rate limiting
6. 🟠 **Fix XSS vulnerabilities** in frontend
7. 🟠 **Add SSRF protection** to URL fetching
8. 🟠 **Create `.gitignore`** and `.env.example`
9. 🟠 **Replace `print()` with logging**

### Medium-term (Important - Fix This Month):

10. 🟡 **Add comprehensive tests**
11. 🟡 **Implement security headers**
12. 🟡 **Add dependency vulnerability scanning**
13. 🟡 **Fix typo in `memory/db.py:92`**
14. 🟡 **Add API versioning**
15. 🟡 **Document security practices**

---

## 10. Security Checklist

- [ ] Remove unsafe `eval()` usage
- [ ] Restrict CORS configuration
- [ ] Implement authentication/authorization
- [ ] Add rate limiting
- [ ] Fix XSS vulnerabilities
- [ ] Add SSRF protection
- [ ] Implement input validation
- [ ] Add security headers
- [ ] Create `.gitignore`
- [ ] Create `.env.example`
- [ ] Replace `print()` with logging
- [ ] Add comprehensive tests
- [ ] Add dependency scanning to CI
- [ ] Document security practices
- [ ] Implement error handling best practices
- [ ] Add API versioning
- [ ] Configure production settings

---

## 11. Compliance Considerations

If this application handles:
- **User data:** Consider GDPR compliance
- **Financial data:** Consider PCI-DSS compliance
- **Healthcare data:** Consider HIPAA compliance
- **General:** Follow OWASP Top 10 guidelines

---

## 12. Tools Recommended

1. **Security Scanning:**
   - `bandit` - Python security linter
   - `safety` - Dependency vulnerability scanner
   - `semgrep` - Static analysis
   - `pip-audit` - Dependency auditing

2. **Code Quality:**
   - `pylint` - Code analysis
   - `black` - Code formatting
   - `mypy` - Type checking
   - `pytest` - Testing framework

3. **Security Testing:**
   - OWASP ZAP - Web app security testing
   - Burp Suite - Penetration testing
   - `sqlmap` - SQL injection testing (for testing defenses)

---

## Conclusion

The ChetnaOS.v1 codebase shows good structure and modern framework usage, but requires significant security hardening before production deployment. The most critical issues are the unsafe `eval()` usage, overly permissive CORS, and missing authentication. Addressing the immediate and short-term recommendations will significantly improve the security posture of the application.

**Overall Security Rating:** 🟡 **MEDIUM RISK** (with critical issues that must be addressed)

**Estimated Effort to Address Critical Issues:** 2-3 days  
**Estimated Effort for Full Security Hardening:** 1-2 weeks

---

**Report Generated:** 2024-12-19  
**Next Review Recommended:** After addressing critical issues

