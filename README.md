# HobbyMatch

**HobbyMatch** is a social discovery platform designed to connect users through shared hobbies and interests. Utilizing ranked hobby preferences, the application intelligently recommends compatible matches, events, and content to foster meaningful connections. By blending social networking, ephemeral content, and gamified interactions. HobbyMatch encourages engagement both online and in real life.

Built on a modern full-stack architecture leveraging ***React***, ***FastAPI***, ***PostgreSQL***, and ***Firebase Authentication***. HobbyMatch exemplifies scalable design, robust relational data modeling, and a user-centric approach.

> **Note:** Each major directory in the project — `/backend` and `/frontend` — includes its own `README.md` file. These contain detailed explanations of the internal architecture, module responsibilities, API usage, and how each layer fits together within the full-stack ecosystem. Contributors are encouraged to read them before diving into the codebase.

> **Progress.md** outlines the current development status of the application, including implemented features through quick video walkthroughs.

### Project Objectives

HobbyMatch is designed to:

- Facilitate friendships and activity-based connections through shared hobbies.
- Encourage real-world interaction with events, hobby hotspots, and time-limited user posts.
- Motivate consistent participation via a gamification system featuring points, streaks, and reliability scores.

### Key Features

- Secure Google Sign-In with optional domain/email restrictions
- Hobby-based user matching using ranked preferences (top three hobbies)
- Advanced matching algorithm to suggest highly compatible users
- Story-style ephemeral hobby posts, visible for 24 hours
- Match and chat functionality for direct user communication
- RSVP system for events and live hobby spots
- Flake Score metric to discourage unreliable behavior
- Points and streaks system to promote engagement and habit formation
- Rich user profiles including bios, profile photos, and an optional photo gallery (up to three images)
- In-app notifications for matches, messages, RSVPs, and other activities
- Responsive user interface optimized for desktop (mobile support forthcoming)

#### Technology Stack

| Layer          | Technology                          |
| -------------- | --------------------------------- |
| Frontend       | React (JavaScript, JSX, HTML, CSS)|
| Authentication | Firebase                          |
| Backend        | FastAPI with PostgreSQL           |
| Image Storage  | Cloudinary                       |
| Hosting        | Firebase                         |

#### High-Level Architecture

```plaintext
+---------------------------+        +------------------------------+        +------------------+
|         Frontend          | <----> |           Backend            | <----> |     Database     |
|   (React / JavaScript,    |        |  (FastAPI / SQLAlchemy ORM)  |        |   (PostgreSQL)   |
|    JSX, HTML, CSS)        |        |                              |        |                  |
+---------------------------+        +------------------------------+        +------------------+
```

### Why Open Source?

Although ***HobbyMatch*** is a personal project, it is intentionally open source to encourage collaboration and shared learning within the developer community. Whether you're interested in fixing bugs, improving documentation, or contributing new features, you're welcome to get involved. Contributions will be managed through pull requests and code reviews to ensure both quality and transparency.

This project is open source primarily for educational purposes, for both for myself and for others, especially college students and recent graduates aiming to build skills and portfolios. By keeping the project open, the goal is to:
- Promote ***collaborative growth***, enabling developers to learn and build together.
- Maintain ***transparency***, making the app’s architecture, design decisions, and codebase accessible to all.
- Serve as a ***learning resource*** for full-stack development using modern technologies like React, FastAPI, and PostgreSQL.

***Currently, communication is handled via email, but as the community grows, we plan to introduce a Discord server and a public Jira board to better organize discussions, issues, and feature planning.***

### Contributing

**HobbyMatch** is still in early development; core data models, API endpoints, and schema definitions are being actively prototyped. Additional features will be rolled out incrementally. Your help is welcome at any stage, whether it’s fixing bugs, improving docs, or building features!

#### How to Contribute via Pull Request

1. **Fork the repository** to your GitHub account.

2. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/your-username/hobbymatch.git
   cd hobbymatch
   ```

3. In the root of the backend directory, create a secrets/ folder and add the required private credentials:
    ```bash
        /secrets/firebase-admin.json
    ```

4. Create a .env file with the following:
    ```bash
        # PostgreSQL async database URL
        HOBBYMATCH_DATABASE_URL=postgresql://user:password@host:port/dbname

        # Cloudinary credentials
        CLOUDINARY_CLOUD_NAME=
        CLOUDINARY_API_KEY=
        CLOUDINARY_API_SECRET=
    ```
⚠️ Never commit secrets or credentials. Make sure secrets/ and .env are in .gitignore.


5. In the root of the frontend directory, create a .env file:
    ```bash
        VITE_FIREBASE_API_KEY=
        VITE_FIREBASE_AUTH_DOMAIN=
        VITE_FIREBASE_PROJECT_ID=
        VITE_FIREBASE_STORAGE_BUCKET=
        VITE_FIREBASE_MESSAGING_SENDER_ID=
        VITE_FIREBASE_APP_ID=
    ```
⚠️ Ensure Firebase Auth and Cloudinary integrations are properly configured and working locally.

3. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. Make your changes and **commit**:
   ```bash
   git add .
   git commit -m "Add [your feature or fix description]"
   ```
5. **Push** the changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
6. Open a **pull request** on the original repository. Be sure to:
    - Clearly describe the purpose of your changes.
    - Include screenshots or a demo if applicable.
    - List any breaking changes or migration steps.

7. Be open to feedback. All contributions will go through a code review process to ensure quality and alignment with the project’s goals.

#### Coding and Documentation

- Please write **clear, minimalistic comments** in your code for complex logic or non-obvious decisions.
- Follow the existing code style and formatting for consistency.
- Keep commit messages concise and descriptive, e.g., `fix: handle null user in profile` or `feat: add location prompt modal`.
- Update documentation if you add new APIs or change existing behavior.

#### Pull Request Process

1. Fork the repo and create a feature branch.
2. Write tests if applicable.
3. Make sure your code passes all linting and tests.
4. Submit a pull request with a clear description of your changes.
5. Be responsive to code review comments and update your PR as needed.


#### Contributor License Agreement

By submitting a contribution, you agree that:

- You are the original author of your contribution, and you have the right to submit it.
- You grant the project maintainer *Richard Maliyetu* a perpetual, worldwide, non-exclusive license to use, modify, and distribute your contribution as part of this project.
- You do not acquire any ownership or control over the project or its direction by contributing.
- The project will remain under the sole ownership and discretion of its creator, even though it is open source.

*- Thank you for helping improve HobbyMatch! Your contributions whether large or small are truly appreciated.*