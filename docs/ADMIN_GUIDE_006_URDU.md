# Admin Guide: Urdu Translation Management (T077)

**Feature**: 006-urdu-translation
**Audience**: Administrators and Content Managers
**Last Updated**: February 10, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Access Control](#access-control)
3. [Translation Dashboard](#translation-dashboard)
4. [Managing Translations](#managing-translations)
5. [Glossary Management](#glossary-management)
6. [Monitoring & Analytics](#monitoring--analytics)
7. [Handling Feedback](#handling-feedback)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Admin Translation Management system allows administrators and instructors to:

- **Manage translations** of chatbot responses from English to Urdu
- **Review and approve** translations before publishing
- **Monitor translation progress** with completion metrics
- **Handle user feedback** on translations
- **Audit translation history** with detailed logs
- **Manage glossary terms** with Urdu translations
- **Track stale translations** that need updating

### Access Requirements

**Admin-Only Features**:
- ✅ View all translations
- ✅ Update translations
- ✅ Review and publish translations
- ✅ View analytics and metrics
- ✅ Manage glossary
- ✅ View audit logs
- ✅ Handle feedback

**Required Roles**:
- `admin` - Full access to all management features
- `instructor` - Limited access (read-only for some features)

---

## Access Control

### 1. Authentication

All admin endpoints require JWT authentication:

```bash
# Get your API token
curl -X POST https://api.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin_user", "password": "your_password"}'

# Response:
# {"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}

# Use token in requests
ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 2. Role-Based Access

**Admin Role** (`admin`):
```json
{
  "sub": "user_123",
  "username": "admin_user",
  "role": "admin"
}
```

Permissions:
- ✅ View all translations
- ✅ Update all translations
- ✅ Publish/unpublish translations
- ✅ Delete translations (if needed)
- ✅ View all analytics
- ✅ Manage glossary
- ✅ View audit logs

**Instructor Role** (`instructor`):
```json
{
  "sub": "user_456",
  "username": "instructor_user",
  "role": "instructor"
}
```

Permissions:
- ✅ View translations (read-only)
- ⚠️ Update translations (if author)
- ❌ Cannot publish (requires admin)
- ⚠️ Limited analytics access
- ⚠️ Cannot delete or bulk operations

---

## Translation Dashboard

### 1. Access Dashboard

Navigate to: `https://app.example.com/admin/translations`

### 2. Dashboard Overview

The dashboard displays:

```
┌─────────────────────────────────────────────────────┐
│ TRANSLATION DASHBOARD                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📊 METRICS SUMMARY                                │
│ ├─ Total Templates: 100                           │
│ ├─ Translated: 85 (85%)                           │
│ ├─ Reviewed: 70 (70%)                             │
│ ├─ Published: 65 (65%)                            │
│ └─ Stale: 5                                       │
│                                                     │
│ 🔄 QUICK ACTIONS                                   │
│ ├─ [Review Next] [Publish All] [Export]           │
│ └─ [Import] [Settings] [Help]                     │
│                                                     │
│ 📋 TRANSLATION LIST                                │
│ ├─ Filters: Status [ ] Language [ ]              │
│ ├─ Search: [____________] [Search]               │
│ └─ Rows per page: [10 ▼]                          │
│                                                     │
│ | Key | Status | Progress | Actions |             │
│ |-----|--------|----------|---------|             │
│ | greeting | Published | 100% | ... |            │
│ | farewell | Reviewed | 100% | ... |             │
│ | error_404 | Draft | 50% | ... |                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 3. Filter Translations

**By Status**:
```
Filter: Status = [All ▼]
- [ ] All
- [ ] Draft
- [ ] Reviewed
- [ ] Published
```

**By Language**:
```
Filter: Language = [Urdu ▼]
- [ ] All
- [ ] English
- [ ] Urdu
```

**Search**:
```
Search: [________] (searches in template key and content)
```

---

## Managing Translations

### 1. View Translation Details

**Click on a row** in the translation list to view:

```
TRANSLATION DETAILS
────────────────────────────────────────

Template Key: greeting
Status: Draft

English Content:
"Hello, how can I help you?"

Urdu Translation:
"السلام علیکم، میں آپ کی کیا مدد کر سکتا ہوں؟"

Metadata:
├─ Created: Feb 1, 2026 by admin_user
├─ Last Updated: Feb 5, 2026
├─ Version: 3
└─ Stale: No

Actions:
├─ [Edit] [Review] [Publish] [History] [Delete]
└─ [Compare with English] [Preview RTL]
```

### 2. Update Translation

**To update a translation**:

```bash
curl -X PUT https://api.example.com/api/v1/admin/translations/1 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urdu_translation": "نیا ترجمہ"
  }'

# Response:
# {
#   "id": 1,
#   "template_id": 1,
#   "urdu_translation": "نیا ترجمہ",
#   "status": "draft",
#   "updated_at": "2026-02-10T12:00:00"
# }
```

**Via Dashboard**:
1. Click [Edit] button on translation row
2. Update the Urdu text in the editor
3. Click [Save Draft] or [Save & Review]

### 3. Review Translation

**Mark as Reviewed**:

```bash
curl -X POST https://api.example.com/api/v1/admin/translations/1/review \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "reviewed"}'

# Response: 200 OK
```

**Checklist for Review**:

- [ ] Translation is accurate to English meaning
- [ ] Grammar and spelling are correct
- [ ] Technical terms are properly translated
- [ ] RTL formatting displays correctly
- [ ] Character encoding is correct (UTF-8)
- [ ] Length is reasonable (not too long/short)
- [ ] No hardcoded values or variables
- [ ] Consistency with glossary terms

### 4. Publish Translation

**Publish for Production**:

```bash
curl -X POST https://api.example.com/api/v1/admin/translations/1/review \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'

# Triggers:
# 1. Cache invalidation
# 2. Notification to users
# 3. Analytics tracking
# 4. Audit log entry
```

**Via Dashboard**:
1. Filter by status "Reviewed"
2. Select translations to publish (checkbox)
3. Click [Publish All] button
4. Confirm in modal
5. Translations go live immediately

### 5. Bulk Operations

**Publish Multiple Translations**:

```bash
curl -X POST https://api.example.com/api/v1/admin/translations/bulk/publish \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_ids": [1, 2, 3, 4, 5],
    "status": "published"
  }'
```

**Update Stale Translations**:

```bash
curl -X GET https://api.example.com/api/v1/admin/translations/stale \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# [
#   {
#     "id": 5,
#     "template_key": "error_500",
#     "status": "published",
#     "is_stale": true,
#     "stale_since": "2026-02-08T10:00:00"
#   }
# ]
```

---

## Glossary Management

### 1. Access Glossary

Navigate to: `https://app.example.com/admin/glossary`

### 2. View Glossary Terms

```
GLOSSARY MANAGEMENT
────────────────────────────────────────

Search: [__________] [Search]

| English Term | Urdu | Progress | Actions |
|---|---|---|---|
| ROS 2 | ROS 2 | ✓ | View |
| Node | نوڈ | ✓ | View |
| Topic | ٹاپک | ✓ | View |
| Service | سروس | ✗ | Edit |
| Kinematics | کائنیمیٹکس | ✓ | View |
```

### 3. Add New Term

**Via API**:

```bash
curl -X POST https://api.example.com/api/v1/admin/glossary \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "english_term": "Actuator",
    "urdu_translation": "ایکچولیٹر",
    "pronunciation_transliterated": "actuator",
    "definition_english": "A device that moves or controls a mechanism",
    "definition_urdu": "ایک آلہ جو کسی میکانزم کو حرکت دیتا ہے",
    "category": "robotics"
  }'
```

**Via Dashboard**:
1. Click [Add New Term] button
2. Fill in English term, Urdu translation, definition
3. Click [Save]

### 4. Update Glossary Term

```bash
curl -X PUT https://api.example.com/api/v1/admin/glossary/5 \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urdu_translation": "بہتر ترجمہ"
  }'
```

### 5. View Glossary Statistics

```bash
curl -X GET https://api.example.com/api/v1/admin/glossary/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# {
#   "total_terms": 150,
#   "translated": 145,
#   "untranslated": 5,
#   "translated_percent": 96.7,
#   "categories": {
#     "robotics": 80,
#     "programming": 40,
#     "hardware": 30
#   }
# }
```

---

## Monitoring & Analytics

### 1. View Translation Metrics

**API Endpoint**:

```bash
curl -X GET https://api.example.com/api/v1/admin/translations/metrics \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# {
#   "total_templates": 100,
#   "translated": 85,
#   "reviewed": 70,
#   "published": 65,
#   "translation_percent": 85.0,
#   "review_percent": 70.0,
#   "published_percent": 65.0,
#   "stale_count": 5
# }
```

### 2. Language Adoption Analytics

**User Language Preferences**:

```bash
curl -X GET https://api.example.com/api/v1/analytics/language-adoption \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# {
#   "total_users": 1000,
#   "english_users": 850,
#   "urdu_users": 150,
#   "english_percent": 85.0,
#   "urdu_percent": 15.0
# }
```

### 3. Demographics

**By User Role**:

```bash
curl -X GET https://api.example.com/api/v1/analytics/language-demographics \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# {
#   "student": {
#     "english": 700,
#     "urdu": 130,
#     "total": 830
#   },
#   "instructor": {
#     "english": 150,
#     "urdu": 20,
#     "total": 170
#   }
# }
```

### 4. Performance Monitoring

**Monitor API Response Times**:

| Endpoint | p95 Latency | Target | Status |
|----------|---|---|---|
| /api/v1/chatbot/response | 250ms | <500ms | ✅ |
| /api/v1/glossary/search | 150ms | <300ms | ✅ |
| /api/v1/admin/translations | 200ms | <1000ms | ✅ |

**Check Cache Hit Rate**:

```bash
curl -X GET https://api.example.com/admin/cache-stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Expected: > 80% hit rate for translations
```

---

## Handling Feedback

### 1. View User Feedback

**Get Glossary Feedback**:

```bash
curl -X GET https://api.example.com/api/v1/admin/glossary/feedback \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# [
#   {
#     "id": 1,
#     "term_id": 5,
#     "user_id": "user_123",
#     "feedback": "Translation could be improved",
#     "rating": 3,
#     "created_at": "2026-02-05T10:00:00"
#   }
# ]
```

### 2. Feedback Dashboard

Navigate to: `https://app.example.com/admin/feedback`

```
FEEDBACK MANAGEMENT
────────────────────────────────────────

Filters: Rating [1⭐] Status [All]

| Term | User | Feedback | Rating | Status | Actions |
|---|---|---|---|---|---|
| ROS 2 | student_1 | Good translation | 5⭐ | ✓ | Archive |
| Node | student_2 | Could improve | 3⭐ | Pending | [Review] |
| Topic | student_3 | Wrong term | 1⭐ | Alert | [Urgent] |
```

### 3. Respond to Feedback

**Update Translation Based on Feedback**:

1. Click [Review] on the feedback item
2. See the suggested improvement
3. Update translation if needed
4. Mark feedback as "Addressed"
5. Notify user of update

```bash
curl -X POST https://api.example.com/api/v1/admin/glossary/feedback/1/address \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response": "Thank you for the feedback. We have updated the translation.",
    "action_taken": "updated_translation"
  }'
```

---

## Audit Logging

### 1. View Audit Log

All translation changes are logged:

```bash
curl -X GET https://api.example.com/api/v1/admin/audit-log?resource=translation \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Response:
# [
#   {
#     "id": 1,
#     "admin_id": "admin_123",
#     "action": "update_translation",
#     "resource_type": "translation",
#     "resource_id": 5,
#     "changes": {
#       "urdu_translation": "new value"
#     },
#     "timestamp": "2026-02-10T12:00:00",
#     "ip_address": "192.168.1.100"
#   }
# ]
```

### 2. Export Audit Log

```bash
curl -X GET https://api.example.com/api/v1/admin/audit-log/export \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  > audit_log_2026-02-10.csv
```

### 3. Generate Audit Report

**Via Dashboard**:
1. Navigate to Admin → Reports
2. Click [Generate Audit Report]
3. Select date range
4. Choose format (PDF, CSV, JSON)
5. Download report

---

## Troubleshooting

### Issue 1: Cannot access admin dashboard

**Error**: 403 Forbidden

**Solution**:
1. Verify your account has `admin` role
2. Check JWT token is valid
3. Verify token includes role claim
4. Contact system admin if role not assigned

### Issue 2: Translation update fails

**Error**: 400 Bad Request

**Solution**:
```json
// Ensure correct format:
{
  "urdu_translation": "صحیح اردو متن"  // Must be valid Urdu
}

// Common mistakes:
- Empty string: ""
- Wrong field name: "translation" instead of "urdu_translation"
- HTML/special characters not escaped
```

### Issue 3: Stale translation not detected

**Symptoms**: Translation marked as stale not showing in list

**Solution**:
1. Verify English template was updated
2. Check `stale_since` timestamp in database
3. Run cache invalidation:
   ```bash
   curl -X POST /admin/cache/invalidate \
     -H "Authorization: Bearer $TOKEN"
   ```

### Issue 4: Performance degradation

**Symptoms**: Dashboard slow to load

**Solution**:
1. Check cache hit rate
2. Verify database indexes exist:
   ```sql
   SELECT * FROM pg_indexes
   WHERE tablename = 'chatbot_response_translation_status';
   ```
3. Run database vacuum:
   ```bash
   sudo -u postgres vacuumdb dbname
   ```

---

## Best Practices

### Translation Quality

✅ **Do**:
- Use professional Urdu terms
- Maintain consistency with glossary
- Keep translations concise
- Use formal Urdu (Urdū-ye Fuṣḥā)
- Test RTL rendering before publishing

❌ **Don't**:
- Use transliteration instead of proper Urdu script
- Leave untranslated English terms mixed in
- Create translations that are too long
- Use colloquial or regional dialects
- Publish without testing on multiple browsers

### Security

✅ **Do**:
- Use strong passwords (16+ characters)
- Enable 2FA if available
- Log out after admin sessions
- Monitor audit logs regularly
- Report suspicious activity

❌ **Don't**:
- Share your admin token
- Publish sensitive information
- Delete translations without backup
- Disable rate limiting
- Give admin access to untrusted users

### Performance

✅ **Do**:
- Cache translations aggressively
- Use batch operations for bulk updates
- Monitor performance metrics
- Optimize database queries
- Use CDN for font delivery

❌ **Don't**:
- Trigger cache invalidation unnecessarily
- Perform heavy operations during peak hours
- Store large files in database
- Ignore performance warnings
- Run migrations during business hours

---

## Support

**For Admin Support**:
- 📧 Email: admin-support@example.com
- 💬 Slack: #admin-support
- 📞 Phone: +92-300-ADMIN1
- 🌐 Wiki: https://wiki.example.com/admin

**Common Resources**:
- [API Documentation](../API_DOCUMENTATION.md)
- [Troubleshooting Guide](../TROUBLESHOOTING.md)
- [FAQ](../FAQ.md)

---

**Version**: 1.0
**Last Updated**: February 10, 2026
**Owner**: Platform Admin Team
