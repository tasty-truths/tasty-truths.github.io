Instructions to ensure how to safely branch, commit, and push changes to our project while keeping the main branch stable. 

1. Clone the Repository

If this is your first time contributing, start by cloning the project to your local machine:

git clone https://gitlab.cci.drexel.edu/cid/2526/fw1023/d3/tasty_truths.git

This creates a local copy of the repository that you can work on.

2. Create a New Branch

Before making any changes, make sure you’re not working on the main branch.
Create a new branch for your work:

git checkout -b your-branch-name

Replace your-branch-name with something descriptive (e.g., fix-navbar-bug or add-recipe-page).
This keeps your work isolated and prevents breaking the main project.

3. Make and Test Your Changes

Open your preferred code editor and begin writing or editing code.
Once finished, test your changes to make sure everything works properly.

Save all modified files before continuing.

4. Stage and Commit Your Changes

Add your changes to the staging area:

git add .

Then commit your changes with a clear, descriptive message:

git commit -m "Added responsive design to homepage"

A good commit message briefly explains what was changed or fixed.

5. Push Your Branch

When your code is tested and committed, push your branch to GitLab:

git push origin your-branch-name

Make sure to replace your-branch-name with the branch you created.

6. Create a Merge Request (Pull Request)

After pushing your branch, open GitLab and click “Compare & Merge Request” next to your branch.
Add a short description explaining what you changed or added.

Once submitted, another team member will review and approve your merge request before it’s added to the main branch.

7. Sync with Main (If Needed)

If you encounter merge conflicts or your branch is out of sync with the latest main, do the following:

git checkout main
git pull origin main
git checkout your-branch-name
git merge main

Resolve any conflicts if prompted, test your changes again, and push the updated branch.

8. Final Merge

After your merge request is approved, it will be merged into main.
Your changes are now part of the official project — great job!

Thank you for following these steps and helping keep our project organized and stable.
Happy coding!