KISMET HARBOR — STATIC TAKEN FACECLAIMS SPEED TEST

WHAT THIS DOES
Instead of making Tumblr visitors wait for Google Apps Script, GitHub Actions
periodically downloads the already public, approved faceclaim data from your
existing Apps Script test deployment. GitHub Pages hosts a fast static JSON file.
Your Tumblr page fetches that public JSON directly. No private Sheets API key,
Apps Script code change, or Google Sheets restructuring is needed.

IMPORTANT: The existing Apps Script deployment must already serve
  YOUR_APP_SCRIPT_EXEC_URL?feed=takenfcs
as JavaScript beginning with window.khTakenFcReceive(...).
This came with the previous Tumblr-native test. Verify that URL in a browser.

SETUP (ONE TIME)
1. Sign in to github.com, create a NEW PUBLIC repository (for example
   kh-public-directory). Keep it separate from your private admin scripts.
2. Upload ALL files from this package to the repository while keeping the folder
   structure, especially .github/workflows/publish-faceclaims.yml,
   scripts/update_faceclaims.py, docs/index.html, and docs/tumblr-takenfcs.html.
   IMPORTANT: Ensure the hidden .github/workflows folder is really included.
3. In the repository, open Settings > Secrets and variables > Actions > Variables.
   Create a repository VARIABLE (not a secret):
      Name: KH_FEED_URL
      Value: your deployed Google Apps Script /exec URL from the earlier
             Taken Faceclaims native test (NOT /dev, no ?feed parameter).
4. In Settings > Pages > Build and deployment, set Source to GitHub Actions.
   There is no branch or /docs selection: the workflow will publish /docs.
5. In Actions > Publish public Taken Faceclaims > Run workflow, run the job.
   Check that it succeeds. It validates the feed and deploys GitHub Pages.
6. Find the deployed site URL under Settings > Pages, or in the completed run.
   Confirm that the JSON link on its landing page works.
7. Open the public JSON URL in your browser:
      https://YOUR-GITHUB-USERNAME.github.io/YOUR-REPOSITORY/takenfcs.json
   It must show JSON with version, generated, theme, and characters.
8. Open docs/tumblr-takenfcs.html in a text editor. Change DATA_URL to the
   exact GitHub Pages URL above. Optionally replace PROFILE_WEB_APP_URL
   if your profile links should use a different deployed Apps Script URL.
   Copy the full HTML into a NEW Tumblr custom HTML test page, e.g.
   /takenfcs-static-test. Leave your current Taken Faceclaims page untouched.
9. Compare speed on mobile and desktop. Test the alphabet anchors, search,
   active and retired entries, and clicking character names. Confirm that
   drafts and unpublished characters are excluded.
10. Change one public faceclaim in Sheets, wait for the next scheduled workflow
    and GitHub Pages publication, then refresh the test page. Changes are
    automatic, but the delay can exceed 5 minutes due to Apps Script cache,
    GitHub Actions scheduling delays, and GitHub Pages publication.

NOTES
- THEME SETTINGS colors are included in the periodically published feed.
- No Code.gs replacement is needed for this speed trial. Index.html also stays
  unchanged. The existing live Tumblr directory is untouched.
- The repository MUST be PUBLIC for this public GitHub Pages test and will
  contain a PUBLIC copy of taken faceclaims and theme colors. Do not add private
  information, scripts with secrets, or spreadsheet exports.
- If a formerly public person becomes unpublished, there may be a publication
  delay before GitHub Pages stops displaying them. For immediate takedown,
  remove or correct the static JSON and trigger a new publication manually.
- GitHub scheduled workflows can be delayed or disabled after extended
  inactivity; check Actions if data stops refreshing.
- The Pages URL may use a different layout for account-level repos or custom
  domains; use the exact published URL from Settings > Pages.
- If Tumblr disallows fetch from GitHub Pages or rewrites your HTML, the browser
  console will show the issue; this is a test, not a guaranteed production fit.
