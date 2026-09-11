# Freshbox Plánovač

A small app to plan your weekly Freshbox lunch orders, track what you're spending, and export the week to your calendar.

## Why this needs to be hosted online (not just opened as a file)

Freshbox.cz doesn't allow other websites to read its pages directly from a browser (a security rule called CORS). To work around that reliably, a **GitHub Action fetches the menu on GitHub's servers** (where that rule doesn't apply) once or twice a week and saves it as `menu.json` right in this repository. The app then just reads that file from its own address — which always works, with no proxies or workarounds needed.

This *only* works if the app is served over a real web address (`https://...`), which is exactly what GitHub Pages gives you for free. Opening `index.html` by double-tapping it from your Files app will not work — browsers block this kind of file loading for local files entirely.

## Setup (10 minutes, one time)

1. **Create a GitHub account** if you don't have one (github.com — free).
2. **Create a new repository**: click the `+` in the top right → *New repository*. Name it anything, e.g. `freshbox-planner`. Keep it public. Don't add a README (you already have one here).
3. **Upload these files** to the repo: on the repo page, click *Add file → Upload files*, and drag in everything from this folder — `index.html`, `menu.json`, `README.md`, and the whole `.github` folder (including the `workflows` subfolder — GitHub's uploader preserves folder structure if you drag the folder itself, or use `git` locally if you prefer). Commit.
4. **Enable GitHub Pages**: go to *Settings → Pages*. Under "Build and deployment", set Source to "Deploy from a branch", branch `main`, folder `/ (root)`. Save. After a minute or two your app will be live at `https://<your-username>.github.io/freshbox-planner/`.
5. **Allow the Action to commit**: go to *Settings → Actions → General → Workflow permissions*, choose "Read and write permissions", save. (Without this, the scheduled Action can fetch the menu but won't be able to save it back.)
6. **Run the Action once manually** to confirm it works: go to the *Actions* tab → "Update Freshbox menu" → *Run workflow*. After it finishes (~30 seconds), check that `menu.json` in the repo has an updated `fetched_at` timestamp.

That's it — from here on, the Action runs automatically every Monday and Thursday morning to keep the menu current, and you just open your GitHub Pages link on your phone (add it to your home screen for an app-like feel).

## Using the app

- Each day: pick a lunch option (or none), a size, and any soup/dessert/smoothie add-ons.
- The bottom bar shows your running total and item counts for the visible week; switch weeks with the tabs at the top if two weeks are published.
- **Export to calendar** creates a `.ics` file with one event per day listing exactly what you ordered and the price — import it into Google/Apple/Outlook calendar.
- Your choices are saved on your phone (not shared anywhere) per week, so closing and reopening the app keeps everything.

## If something ever looks stale or wrong

- Tap the ⟳ button in the top right to try fetching the very latest menu live from freshbox.cz (bonus path, not required for normal use).
- Trigger the GitHub Action manually any time from the *Actions* tab.
- Worst case, open `freshbox.cz/tydenni-menu/`, view its page source, and paste it into the fallback box the app shows if it can't load anything.

## Files

- `index.html` — the app itself.
- `menu.json` — the current menu data, kept fresh by the GitHub Action. Seeded here with the menu for 7–11 Sep and 14–18 Sep 2026 so the app works immediately even before the Action first runs.
- `.github/workflows/update-menu.yml` — the scheduled job.
- `scripts/fetch_menu.py` — the parser it runs.
