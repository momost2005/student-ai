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
        student_id: int,
        curriculum_id: int,
        chunk_id: int,
        student_answer: str
    ) -> dict:

        # -----------------------------------------
        # 1. Get trusted question from database
        # -----------------------------------------

        chunk = (
            self.repository
            .get_chunk_for_curriculum(
                db=db,
                chunk_id=chunk_id,
                curriculum_id=curriculum_id
            )
        )

        if not chunk:

            return {
                "status":
                    "question_not_found",

                "feedback":
                    (
                        "The requested practice "
                        "question was not found."
                    )
            }


        # -----------------------------------------
        # 2. Get verified reference solution
        # -----------------------------------------

        solution = (
            self.repository
            .get_verified_solution(
                db=db,
                chunk_id=chunk_id
            )
        )


        if not solution:

            attempt = (
                self.repository
                .save_practice_attempt(
                    db=db,
                    student_id=student_id,
                    curriculum_id=curriculum_id,
                    chunk=chunk,
                    student_answer=student_answer,
                    reference_answer=None,
                    evaluation_status=(
                        "cannot_evaluate"
                    ),
                    feedback=(
                        "No verified reference "
                        "answer is available for "
                        "this question."
                    ),
                    solution_source=None,
                    ai_provider=None,
                    ai_model=None
                )
            )

            return {
                "status":
                    "cannot_evaluate",

                "feedback":
                    (
                        "No verified reference "
                        "answer is available for "
                        "this question."
                    ),

                "attempt_id":
                    attempt.id
            }


        # -----------------------------------------
        # 3. Build evaluation prompt
        # -----------------------------------------

        prompt = f"""
You are evaluating a student's mathematics answer.

QUESTION:
{chunk.content}

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


        # -----------------------------------------
        # 4. Ask active AI provider to evaluate
        # -----------------------------------------

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


        # -----------------------------------------
        # 5. Save student attempt
        # -----------------------------------------

        attempt = (
            self.repository
            .save_practice_attempt(
                db=db,
                student_id=student_id,
                curriculum_id=curriculum_id,
                chunk=chunk,
                student_answer=student_answer,
                reference_answer=(
                    solution.final_answer
                ),
                evaluation_status=(
                    evaluation_status
                ),
                feedback=feedback,
                solution_source=(
                    solution.solution_source
                ),
                ai_provider=provider_name,
                ai_model=model_name
            )
        )


        # -----------------------------------------
        # 6. Return evaluation
        # -----------------------------------------

        return {
            "attempt_id":
                attempt.id,

            "status":
                evaluation_status,

            "feedback":
                feedback,

            "provider":
                provider_name,

            "model":
                model_name,

            "solution_source":
                solution.solution_source
        }