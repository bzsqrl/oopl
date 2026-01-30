# How to Upload Oopl to GitHub

Follow these steps to upload your `Oopl` project to a new GitHub repository.

## Prerequisites

1.  **Git Installed**: Make sure you have Git installed on your computer.
    -   Type `git --version` in your terminal to check.
2.  **GitHub Account**: You need an account at [github.com](https://github.com).

## Step 1: Create a New Repository on GitHub

1.  Log in to GitHub.
2.  Click the **+** icon in the top-right corner and select **New repository**.
3.  **Repository Name**: Enter `Oopl` (or whatever you want to name it).
4.  **Description**: (Optional) e.g., "VJ Loop Crossfader Application".
5.  **Public/Private**: Choose who can see this project.
6.  **Initialize this repository with**:
    -   **Do NOT** check any of these boxes (Add a README file, .gitignore, license). We are importing an existing repository, so we want an empty one.
7.  Click **Create repository**.
8.  Keep the page open; you will need the URL (e.g., `https://github.com/YourUsername/Oopl.git`).

## Step 2: Prepare Local Files

I have already created a `.gitignore` file for you in the `Oopl` folder. This ensures that temporary files (like build artifacts, video outputs, and virtual environments) are NOT uploaded.

## Step 3: Initialize and Push

Open your terminal (PowerShell or Command Prompt) and navigate to the Oopl folder:

```powershell
cd c:/Users/beatf/Documents/Antigravity/Oopl
```

Run the following commands one by one:

1.  **Initialize Git**:
    ```bash
    git init
    ```

2.  **Add files to staging**:
    ```bash
    git add .
    ```
    *This stages all files except those in .gitignore.*

3.  **Commit the files**:
    ```bash
    git commit -m "Initial commit: Oopl v1.5 functionality"
    ```

4.  **Rename the branch to main**:
    ```bash
    git branch -M main
    ```

5.  **Link to your GitHub repo** (Replace `YOUR_URL` with the URL from Step 1):
    ```bash
    git remote add origin https://github.com/YourUsername/Oopl.git
    ```

6.  **Push the code**:
    ```bash
    git push -u origin main
    ```

## Success!

Refresh your GitHub page, and you should see all your files listed there.

## Updating in the Future

When you make changes to the code:
1.  `git add .`
2.  `git commit -m "Description of changes"`
3.  `git push`
