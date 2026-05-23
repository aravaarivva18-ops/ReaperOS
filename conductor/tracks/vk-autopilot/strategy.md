# VK Autopilot: Full-Stack Integration Strategy

## 1. Content Pipeline (Conductor)
- **Source**: Webclaw / Research Engine to aggregate relevant news/trends.
- **Generator**: GPT-4o-mini produces draft posts in the group's "Tone of Voice".
- **Review**: Ruflo generates a draft; user gets a "thumbs up/down" notification (Chat/Email).

## 2. Execution Engine (Reaper)
- **Scheduler**: Reaper maintains a "Post Queue" in `db.sqlite`.
- **Publisher**: `vk_api` integration to push at optimal times.
- **Protection**: Semantic Search (sqlite-vec) compares new post vs. history to prevent duplicate content.

## 3. Engagement Loop
- **Moderation**: Bot monitors comments.
- **Strategy**: 
    - Auto-filter spam (Rule-based).
    - Flag "meaningful" questions for human review.
    - Draft replies for common queries (awaiting user approval).

## 4. Analytics
- **Pulse**: Post-performance tracking (likes/shares) stored in `task_log`.
- **Report**: Weekly auto-distilled summary in `Dashboard.md`.

---
## Trinity Integration
- **ISA**: Defines content goals & audience.
- **Plan**: Content calendar + engagement thresholds.
- **Execute**: Reaper auto-publisher loop.
- **Distill**: Recursive distillation of group performance data.
