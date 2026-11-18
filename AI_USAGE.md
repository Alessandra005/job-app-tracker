# AI Usage Documentation

## 1. AI Tools Used

- **ChatGPT:** Used for debugging, understanding Flask and MySQL integration, and improving the job-matching algorithm.
- **Google Gemini API (Gemini 3.8 Flash):** Integrated into the Job Match feature to identify direct equivalencies between user skills and job requirements.

## 2. Key Prompts and Implementation

### Skill Equivalency Detection

Gemini was prompted to compare a user's skills with job requirements and identify direct technical skill equivalencies.

Example:
- User skill: PostgreSQL
- Job requirement: SQL
- Expected equivalency: PostgreSQL -> SQL

The prompt instructed Gemini to:
- Only use skills from the supplied lists.
- Exclude exact matches.
- Identify only genuine, direct equivalencies.
- Avoid treating broadly related skills as equivalent.
- Return results in JSON format.

### Job Matching Algorithm

A Python algorithm calculates job match percentages using:
- Required skills: 70% of the score.
- Preferred skills: 30% of the score.

Gemini identifies potential equivalencies, but Python validates the results and calculates the final score.

## 3. What Worked

- Gemini successfully identified PostgreSQL as an equivalent to SQL.
- JSON responses made it possible to process the results programmatically.
- Validating AI responses helped prevent unsupported skill matches.
- Filtering equivalencies by individual job requirements prevented an equivalency from being applied to unrelated jobs.
- The application can still perform exact skill matching if the Gemini API is unavailable.

## 4. What Was Changed

During development, the AI integration was improved to:
- Exclude exact skill matches from AI-generated equivalencies.
- Validate that returned skills exist in the original input lists.
- Associate equivalencies with the relevant job instead of applying them globally.
- Keep final match calculations in Python rather than allowing the AI model to assign scores.

## 5. Lessons Learned

- AI-generated results should be validated before being used in an application.
- Structured JSON responses make AI integrations easier to process.
- AI should support the matching process without replacing deterministic business logic.
- Keeping the scoring algorithm separate from the AI component makes results more consistent and explainable.
- API failures should not prevent the application's core functionality from working.
