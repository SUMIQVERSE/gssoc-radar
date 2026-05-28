# 🚀 GSSoC Radar

A modern, full-stack web application designed to track and analyze real-time GitHub metrics for GirlScript Summer of Code (GSSoC) projects. It intelligently aggregates data from the GSSoC API and GitHub API, processing over 300+ repositories, and displays them on a sleek, high-performance dashboard.

## ✨ Key Features

* **📊 Unified Project Dashboard:** Explore all 300+ active GSSoC repositories in one clean, modern, and easy-to-navigate interface.
* **🎯 Issue Availability Tracking:** Instantly see the exact count of 'Total Opened', 'Open & Assigned', and 'Closed' issues so contributors know exactly where help is needed.
* **❤️ Activity Health Score:** A dynamic metric (0-100%) that highlights how active and responsive a repository currently is, helping contributors choose the best projects.
* **🛠️ Tech-Stack Filtering:** Quickly identify the core technologies used in each project (e.g., React, TypeScript, Python) to find repositories that match your specific skill set.
* **🚀 Seamless Contributor Workflow:** Save time with direct repository links and clear visibility of unassigned tasks, eliminating the guesswork from open-source contributions.

## 🛠️ Tech Stack 

This project leverages a modern, high-performance architecture:

* **Frontend:** [Next.js](https://nextjs.org/) (React, TypeScript)
* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
* **Database:** [Supabase](https://supabase.com/) (PostgreSQL)
* **External APIs:** GitHub REST API, GSSoC Projects API
* **Deployment:** Vercel (Frontend) & Render (Backend)

## ⚙️ Environment Variables

Create `.env` files in their respective directories (Frontend and Backend):

**Backend (`backend/.env`)**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
GITHUB_TOKEN=your_github_personal_access_token
