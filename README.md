# AWS AIF-C01 Exam Prep Tool

Interactive HTML study tool for **AWS Certified AI Practitioner (AIF-C01)** exam.

## How to use

Open `AWS_AIF_C01_Learning_Tool.html` in any modern browser.

### iOS / Safari
iOS blocks `localStorage` on `file://` URLs. To use on iPhone:
```
python3 -m http.server 8000
```
Then open `http://192.168.86.156:8000/AWS_AIF_C01_Learning_Tool.html` in Chrome.

## Features
- **Learning Mode**: 5 domains, 14 subtopics with detailed explanations
- **Quiz Mode**: 5 iterations × 5 rounds × 13 questions (65 per iteration)
- 95 practice questions (MCQ, multi-select, true/false)
- Pass score: 70%
- Progress & notes saved to localStorage
- All CSS/JS embedded — zero dependencies