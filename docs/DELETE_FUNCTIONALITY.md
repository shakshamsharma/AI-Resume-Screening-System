# 🗑️ Delete Functionality Added

## Feature: Delete Jobs, Resumes, and Candidates

**Status:** ✅ **IMPLEMENTED**

---

## 🎯 What's New

You can now delete:
1. **Jobs** - Delete entire hiring campaigns
2. **Resumes** - Delete uploaded resume files
3. **Candidates** - Delete candidate records

---

## 🔧 Implementation Details

### Backend Endpoints Added

#### 1. Delete Job
```
DELETE /api/jobs/{job_id}
```
- Deletes job and all associated data
- Cascades to: resumes, candidates, work_experience, interviews
- Returns: `{"message": "Deleted"}`

#### 2. Delete Resume
```
DELETE /api/resumes/{resume_id}
```
- Deletes resume record from database
- Deletes physical file from disk
- Cascades to: candidate, work_experience
- Returns: `{"message": "Resume deleted successfully", "id": "..."}`

#### 3. Delete Candidate
```
DELETE /api/candidates/{candidate_id}
```
- Deletes candidate record
- Cascades to: work_experience, interviews
- Keeps resume file (can be deleted separately)
- Returns: `{"message": "Candidate deleted successfully", "id": "..."}`

---

## 🎨 UI Changes

### Jobs Page
- **Delete Button:** Trash icon appears on hover
- **Location:** Top-right corner of each job card
- **Confirmation:** "Are you sure?" dialog
- **Warning:** Shows that resumes and candidates will also be deleted

### Candidates Page
- **Delete Button:** Trash icon in Actions column
- **Location:** Last column of candidate table
- **Confirmation:** "Are you sure?" dialog with candidate name
- **Warning:** Shows permanent deletion warning

---

## 🚀 How to Use

### Delete a Job

1. Go to **Jobs** page
2. Hover over a job card
3. Click the **trash icon** (🗑️) in top-right
4. Confirm deletion in dialog
5. Job and all associated data deleted ✅

**Warning:** This will delete:
- The job posting
- All uploaded resumes for this job
- All candidates for this job
- All work experience records
- All interview records

### Delete a Candidate

1. Go to **Candidates** page
2. Find the candidate you want to delete
3. Click the **trash icon** (🗑️) in Actions column
4. Confirm deletion in dialog
5. Candidate deleted ✅

**Note:** The resume file remains in the system (can be deleted separately if needed)

### Delete a Resume

Currently available via API only:
```bash
DELETE /api/resumes/{resume_id}
```

---

## ⚠️ Important Notes

### Cascade Deletion

When you delete a **Job**, it automatically deletes:
```
Job
 ├── Resumes (all)
 │    └── Physical files
 ├── Candidates (all)
 │    ├── Work Experience
 │    └── Interviews
 └── Bias Metrics
```

When you delete a **Resume**, it automatically deletes:
```
Resume
 ├── Physical file
 └── Candidate
      ├── Work Experience
      └── Interviews
```

When you delete a **Candidate**, it automatically deletes:
```
Candidate
 ├── Work Experience
 └── Interviews
```

### Data Safety

1. **Confirmation Required:** All deletions require confirmation
2. **No Undo:** Deletions are permanent
3. **Cascade Warning:** Users are warned about cascade effects
4. **Physical Files:** Resume files are deleted from disk

---

## 🧪 Testing

### Test Delete Job

```bash
# 1. Create a test job
POST /api/jobs/
{
  "title": "Test Job",
  "required_skills": ["python"]
}

# 2. Upload a resume
POST /api/resumes/upload
(with job_id)

# 3. Delete the job
DELETE /api/jobs/{job_id}

# 4. Verify:
# - Job deleted ✅
# - Resume deleted ✅
# - Candidate deleted ✅
# - Physical file deleted ✅
```

### Test Delete Candidate

```bash
# 1. Find a candidate
GET /api/candidates/job/{job_id}

# 2. Delete candidate
DELETE /api/candidates/{candidate_id}

# 3. Verify:
# - Candidate deleted ✅
# - Work experience deleted ✅
# - Interviews deleted ✅
# - Resume still exists ✅
```

---

## 📊 Database Schema

### Cascade Rules

```sql
-- Jobs table
ON DELETE CASCADE to:
  - resumes
  - candidates
  - interviews
  - bias_metrics

-- Resumes table
ON DELETE CASCADE to:
  - candidates

-- Candidates table
ON DELETE CASCADE to:
  - work_experience
  - interviews
```

---

## 🔐 Security

### Authorization
- ✅ Requires authentication (JWT token)
- ✅ Only authenticated users can delete
- ✅ User must be logged in

### Validation
- ✅ Checks if resource exists before deletion
- ✅ Returns 404 if not found
- ✅ Returns proper error messages

---

## 💻 Code Changes

### Files Modified

#### Backend (3 files)
1. **`backend/routers/resumes.py`**
   - Added `delete_resume()` endpoint
   - Deletes physical file and database record

2. **`backend/routers/candidates.py`**
   - Added `delete_candidate()` endpoint
   - Cascades to work_experience and interviews

3. **`backend/routers/jobs.py`**
   - Already had delete endpoint ✅

#### Frontend (3 files)
1. **`frontend/src/utils/api.ts`**
   - Added `resumesApi.delete()`
   - Added `candidatesApi.delete()`

2. **`frontend/src/pages/JobsPage.tsx`**
   - Added delete button with trash icon
   - Added confirmation dialog
   - Added delete mutation

3. **`frontend/src/pages/CandidatesPage.tsx`**
   - Added delete button in Actions column
   - Added confirmation dialog
   - Added delete mutation

---

## 🎯 User Experience

### Before Deletion
```
User clicks delete button
    ↓
Confirmation dialog appears
    ↓
"Are you sure you want to delete [name]?"
"This will permanently remove..."
    ↓
User confirms or cancels
```

### After Deletion
```
If confirmed:
    ↓
Delete request sent to API
    ↓
Success: "Deleted successfully!" toast
    ↓
List refreshes automatically
    ↓
Item removed from UI
```

### If Error
```
Delete fails
    ↓
Error: "Failed to delete" toast
    ↓
Item remains in list
    ↓
User can try again
```

---

## 📝 API Examples

### Delete Job
```bash
curl -X DELETE http://localhost:8000/api/jobs/{job_id} \
  -H "Authorization: Bearer {token}"

# Response:
{
  "message": "Deleted"
}
```

### Delete Resume
```bash
curl -X DELETE http://localhost:8000/api/resumes/{resume_id} \
  -H "Authorization: Bearer {token}"

# Response:
{
  "message": "Resume deleted successfully",
  "id": "resume-id-here"
}
```

### Delete Candidate
```bash
curl -X DELETE http://localhost:8000/api/candidates/{candidate_id} \
  -H "Authorization: Bearer {token}"

# Response:
{
  "message": "Candidate deleted successfully",
  "id": "candidate-id-here",
  "resume_id": "resume-id-here"
}
```

---

## ✅ Verification Checklist

After implementing delete functionality:

- [ ] Can delete jobs from Jobs page
- [ ] Confirmation dialog appears
- [ ] Job and all data deleted
- [ ] Success toast shown
- [ ] List refreshes automatically
- [ ] Can delete candidates from Candidates page
- [ ] Candidate and related data deleted
- [ ] Physical resume files deleted
- [ ] No errors in console
- [ ] API endpoints work correctly

---

## 🐛 Troubleshooting

### Issue: Delete button not visible
**Solution:** Hover over the job card or candidate row

### Issue: "Failed to delete" error
**Solution:** 
- Check if you're logged in
- Verify the item exists
- Check backend logs

### Issue: Item still appears after deletion
**Solution:** Refresh the page manually

### Issue: Physical file not deleted
**Solution:** 
- Check file permissions
- Verify UPLOAD_DIR path
- Check backend logs

---

## 🔮 Future Enhancements

### Planned Features
1. **Bulk Delete:** Select multiple items to delete
2. **Soft Delete:** Move to trash instead of permanent deletion
3. **Restore:** Undo deletion within 30 days
4. **Archive:** Archive old jobs instead of deleting
5. **Export Before Delete:** Download data before deletion

---

## 📚 Related Documentation

- **API Docs:** http://localhost:8000/docs
- **Database Schema:** `backend/models.py`
- **Frontend Components:** `frontend/src/pages/`

---

## 🎉 Summary

### What You Can Do Now

1. ✅ **Delete Jobs**
   - Remove entire hiring campaigns
   - Clean up old job postings
   - Remove test data

2. ✅ **Delete Candidates**
   - Remove incorrect candidates
   - Clean up duplicate entries
   - Remove test uploads

3. ✅ **Clean Data**
   - Keep your system organized
   - Remove old/test data
   - Maintain data hygiene

### Benefits

- ✅ **Better Organization:** Remove clutter
- ✅ **Data Privacy:** Delete sensitive data
- ✅ **Testing:** Easy cleanup after tests
- ✅ **Flexibility:** Full control over your data

---

**Status:** ✅ Fully Implemented and Ready to Use!

**Last Updated:** May 7, 2026
