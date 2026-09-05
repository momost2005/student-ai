import json

from sqlalchemy.orm import Session

from app.ai.gateway import (
    AIGateway
)

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
        response: str,
        expected_concept_codes: list[str]
    ) -> tuple[
        str,
        str,
        dict[str, dict]
    ]:

        text = response.strip()


        # -----------------------------------------
        # Remove Markdown code fences if the model
        # unexpectedly returns them.
        # -----------------------------------------

        if text.startswith("```"):

            lines = text.splitlines()

            if lines:
                lines = lines[1:]

            if (
                lines
                and
                lines[-1].strip().startswith(
                    "```"
                )
            ):

                lines = lines[:-1]

            text = "\n".join(
                lines
            ).strip()


        # -----------------------------------------
        # Parse JSON
        # -----------------------------------------

        try:

            data = json.loads(
                text
            )

        except json.JSONDecodeError:

            return (
                "unknown",
                (
                    "The evaluation response "
                    "could not be processed."
                ),
                {}
            )


        # -----------------------------------------
        # Validate overall AI status
        # -----------------------------------------

        status = (
            str(
                data.get(
                    "status",
                    "unknown"
                )
            )
            .strip()
            .lower()
        )


        allowed_statuses = {
            "correct",
            "partial",
            "incorrect"
        }


        if status not in allowed_statuses:

            status = "unknown"


        feedback = (
            str(
                data.get(
                    "feedback",
                    ""
                )
            )
            .strip()
        )


        # -----------------------------------------
        # Validate concept diagnoses
        # -----------------------------------------

        allowed_diagnosis_statuses = {
            "demonstrated",
            "needs_review",
            "insufficient_evidence"
        }


        concept_diagnoses = {}


        raw_concepts = data.get(
            "concepts",
            []
        )


        if not isinstance(
            raw_concepts,
            list
        ):

            raw_concepts = []


        for item in raw_concepts:

            if not isinstance(
                item,
                dict
            ):

                continue


            concept_code = (
                str(
                    item.get(
                        "concept_code",
                        ""
                    )
                )
                .strip()
            )


            # -------------------------------------
            # The AI is not allowed to invent
            # curriculum concepts.
            # -------------------------------------

            if (
                concept_code
                not in expected_concept_codes
            ):

                continue


            diagnosis_status = (
                str(
                    item.get(
                        "status",
                        ""
                    )
                )
                .strip()
                .lower()
            )


            if (
                diagnosis_status
                not in
                allowed_diagnosis_statuses
            ):

                diagnosis_status = (
                    "insufficient_evidence"
                )


            reason = (
                str(
                    item.get(
                        "reason",
                        ""
                    )
                )
                .strip()
            )


            concept_diagnoses[
                concept_code
            ] = {
                "status":
                    diagnosis_status,

                "reason":
                    reason
            }


        # -----------------------------------------
        # Every expected concept must have a
        # diagnosis.
        #
        # Missing diagnosis never means weak.
        # -----------------------------------------

        for concept_code in (
            expected_concept_codes
        ):

            if (
                concept_code
                not in concept_diagnoses
            ):

                concept_diagnoses[
                    concept_code
                ] = {
                    "status":
                        "insufficient_evidence",

                    "reason":
                        (
                            "The student answer "
                            "does not provide enough "
                            "evidence to assess this "
                            "concept."
                        )
                }


        return (
            status,
            feedback,
            concept_diagnoses
        )


    def _normalize_overall_status(
        self,
        ai_status: str,
        concept_diagnoses: dict[str, dict]
    ) -> str:

        # -----------------------------------------
        # Keep explicit incorrect decisions.
        # -----------------------------------------

        if ai_status == "incorrect":

            return "incorrect"


        # -----------------------------------------
        # Keep explicit partial decisions.
        # -----------------------------------------

        if ai_status == "partial":

            return "partial"


        if ai_status != "correct":

            return ai_status


        diagnosis_statuses = {
            diagnosis.get(
                "status"
            )
            for diagnosis
            in concept_diagnoses.values()
        }


        # -----------------------------------------
        # The AI cannot mark the whole answer
        # correct when one of the concepts required
        # by the question has not been demonstrated.
        # -----------------------------------------

        if (
            "needs_review"
            in diagnosis_statuses
        ):

            return "partial"


        if (
            "insufficient_evidence"
            in diagnosis_statuses
        ):

            return "partial"


        return "correct"


    def _normalize_feedback(
        self,
        ai_status: str,
        normalized_status: str,
        feedback: str
    ) -> str:

        # -----------------------------------------
        # Example:
        #
        # AI says overall "correct" because the
        # final numeric answer is right, but one
        # required concept has insufficient
        # evidence.
        #
        # We normalize the result to partial and
        # make the feedback consistent.
        # -----------------------------------------

        if (
            ai_status == "correct"
            and
            normalized_status == "partial"
        ):

            return (
                "Your final answer is correct, "
                "but you did not provide enough "
                "work to demonstrate all required "
                "parts of the question."
            )


        return feedback


    def evaluate(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        chunk_id: int,
        student_answer: str
    ) -> dict:

        # -----------------------------------------
        # 1. Get trusted curriculum question
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

            feedback = (
                "No verified reference "
                "answer is available for "
                "this question."
            )


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
                    feedback=feedback,
                    solution_source=None,
                    ai_provider=None,
                    ai_model=None,
                    concept_diagnoses=None
                )
            )


            return {
                "attempt_id":
                    attempt.id,

                "status":
                    "cannot_evaluate",

                "feedback":
                    feedback
            }


        # -----------------------------------------
        # 3. Get trusted curriculum concepts
        # -----------------------------------------

        concepts = (
            self.repository
            .get_chunk_concepts(
                db=db,
                chunk_id=chunk_id
            )
        )


        expected_concept_codes = [
            concept.code
            for concept in concepts
        ]


        concept_lines = []


        for concept in concepts:

            concept_lines.append(
                (
                    f"- {concept.code}: "
                    f"{concept.name}"
                )
            )


        concept_context = "\n".join(
            concept_lines
        )


        if not concept_context:

            concept_context = (
                "No explicit curriculum concepts "
                "are mapped to this question."
            )


        # -----------------------------------------
        # 4. Build evaluation prompt
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

CURRICULUM CONCEPTS ASSESSED BY THIS QUESTION:
{concept_context}

Evaluate the overall student answer and diagnose
the evidence for EACH listed curriculum concept.

Important rules:

1. Judge the mathematical answer only against the
   verified reference answer and verified solution.

2. Do not create a different answer key.

3. Accept mathematically equivalent answers.

4. The overall status must be exactly one of:
   correct
   partial
   incorrect

5. For every listed curriculum concept, assign
   exactly one diagnosis status:

   demonstrated
   needs_review
   insufficient_evidence

6. "needs_review" means the student's answer gives
   evidence of a misconception or meaningful error
   related specifically to that concept.

7. Do NOT mark a concept "needs_review" merely because
   the overall answer is incorrect.

8. Use "insufficient_evidence" when the student did not
   show enough work to determine understanding of that
   concept.

9. Use "demonstrated" only when the student's answer
   provides positive evidence of understanding.

10. Do not invent additional concept codes.

11. If the question explicitly asks the student to show
    a method or intermediate work, and the final answer
    is correct but that required work is missing, the
    overall status should be "partial".

12. Return valid JSON only.
    Do not use Markdown.
    Do not use code fences.

Return exactly this JSON structure:

{{
    "status": "correct | partial | incorrect",
    "feedback": "short student-friendly feedback",
    "concepts": [
        {{
            "concept_code": "exact supplied concept code",
            "status": "demonstrated | needs_review | insufficient_evidence",
            "reason": "short evidence-based reason"
        }}
    ]
}}
"""


        # -----------------------------------------
        # 5. AI evaluation
        # -----------------------------------------

        (
            provider_name,
            model_name,
            response
        ) = self.ai_gateway.generate(
            db=db,
            prompt=prompt
        )


        # -----------------------------------------
        # 6. Parse AI response
        # -----------------------------------------

        (
            ai_status,
            feedback,
            concept_diagnoses
        ) = self._parse_evaluation(
            response=response,
            expected_concept_codes=(
                expected_concept_codes
            )
        )


        # -----------------------------------------
        # 7. Deterministic consistency guardrail
        # -----------------------------------------

        evaluation_status = (
            self._normalize_overall_status(
                ai_status=ai_status,
                concept_diagnoses=(
                    concept_diagnoses
                )
            )
        )


        feedback = (
            self._normalize_feedback(
                ai_status=ai_status,
                normalized_status=(
                    evaluation_status
                ),
                feedback=feedback
            )
        )


        # -----------------------------------------
        # 8. Save attempt + concept diagnoses
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
                ai_model=model_name,
                concept_diagnoses=(
                    concept_diagnoses
                )
            )
        )


        # -----------------------------------------
        # 9. Return result
        # -----------------------------------------

        return {
            "attempt_id":
                attempt.id,

            "status":
                evaluation_status,

            "ai_status":
                ai_status,

            "feedback":
                feedback,

            "provider":
                provider_name,

            "model":
                model_name,

            "solution_source":
                solution.solution_source,

            "concept_diagnoses":
                concept_diagnoses
        }