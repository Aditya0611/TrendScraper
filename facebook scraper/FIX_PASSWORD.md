# 🔐 Fix Facebook Password Issue

## Problem

The scraper is failing to log in with this error:
```
"The password you've entered is incorrect."
```

This means the password stored in GitHub Secrets is **incorrect**.

## Solution: Update GitHub Secrets

### Step 1: Get Your Correct Facebook Password

1. Test your login manually:
   - Go to https://www.facebook.com
   - Try logging in with your email and password
   - **Make sure it works** before updating secrets

### Step 2: Update GitHub Secrets

1. **Go to your repository**:
   - https://github.com/Aditya0611/facebook

2. **Click Settings** (top menu)

3. **Go to Secrets and variables** → **Actions** (left sidebar)

4. **Update `FACEBOOK_PASSWORD`**:
   - Find `FACEBOOK_PASSWORD` in the list
   - Click **Update** (pencil icon)
   - Enter your **correct Facebook password**
   - Click **Update secret**

5. **Verify `FACEBOOK_EMAIL`** is also correct:
   - Make sure `FACEBOOK_EMAIL` has your correct email
   - Update if needed

### Step 3: Test Again

1. Go to **Actions** tab
2. Click **Run workflow** → **Run workflow**
3. Monitor the run to see if login succeeds

## Quick Fix Steps

```
1. Go to: https://github.com/Aditya0611/facebook/settings/secrets/actions
2. Click "Update" on FACEBOOK_PASSWORD
3. Enter correct password
4. Click "Update secret"
5. Run workflow again
```

## Important Notes

- ⚠️ **Never share your password** - Only enter it in GitHub Secrets
- ✅ **Test login manually first** - Make sure credentials work in browser
- 🔄 **Run workflow again** - After updating, trigger a new run

## If Login Still Fails

After updating the password, if login still fails, check:

1. **2FA Enabled?** - May need to disable temporarily
2. **Account Locked?** - Check Facebook security settings
3. **Wrong Email?** - Verify `FACEBOOK_EMAIL` is correct
4. **Special Characters?** - Make sure password doesn't have encoding issues

See `LOGIN_TROUBLESHOOTING.md` for more solutions.

