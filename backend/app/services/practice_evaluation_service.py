from sqlalchemy.orm import Session

from app.ai.gateway import AIGateway

from app.repositories.curriculum_repository import (
    CurriculumRepository
)


class PracticeEvaluationService:

    def __init__(
        self,
        repository: CurriculumRepository,
        ai_gateway: AIGateway
    ):

        self.repository = repository
        self.ai_gateway = ai_gateway

    def _parse_evaluation(
        self,
        response: str
    ) -> tuple[str, str]:

        status = "unknown"
        feedback = response.strip()

        for line in response.splitlines():

            line = line.strip()

            if line.startswith("STATUS:"):

                status = (
                    line
                    .replace("STATUS:", "")
                    .strip()
                    .lower()
                )

            elif line.startswith("FEEDBACK:"):

                feedback = (
                    line
                    .replace("FEEDBACK:", "")
                    .strip()
                )

        allowed_statuses = {
            "correct",
            "partial",
            "incorrect"
        }

        if status not in allowed_statuses:
            status = "unknown"

        return status, feedback

    def evaluate(
        self,
        db: Session,
        chunk_id: int,
        question: str,
        student_answer: str
    ) -> dict:

        solution = (
            self.repository
            .get_verified_solution(
                db=db,
                chunk_id=chunk_id
            )
        )


        if not solution:

            return {
                "status":
                    "cannot_evaluate",

                "is_correct":
                    None,

                "feedback":
                    (
                        "No verified reference "
                        "answer is available for "
                        "this question."
                    )
            }


        prompt = f"""
You are evaluating a student's mathematics answer.

QUESTION:
{question}

VERIFIED REFERENCE ANSWER:
{solution.final_answer}

VERIFIED SOLUTION STEPS:
{solution.solution_steps}

STUDENT ANSWER:
{student_answer}

Rules:
- Judge only against the verified reference answer.
- Do not create a different answer key.
- Accept mathematically equivalent answers.
- If the final answer is correct but reasoning is incomplete,
  explain what is missing.
- If incorrect, identify the first important mistake.
- Keep the feedback concise and student-friendly.

Return exactly this format:

STATUS: correct | partial | incorrect
FEEDBACK: <feedback>
"""


        (
            provider_name,
            model_name,
            response
        ) = self.ai_gateway.generate(
            db=db,
            prompt=prompt
        )

        evaluation_status, feedback = (
            self._parse_evaluation(
                response
            )
        )

        return {
            "status": evaluation_status,
            "feedback": feedback,
            "provider": provider_name,
            "model": model_name,
            "solution_source": solution.solution_source
        }