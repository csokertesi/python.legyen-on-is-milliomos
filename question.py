from random import choice

class Question:
    allQuestions = []
    categories = []
    def __init__(self, difficulty: int, q_text: str, answers: list[str,str,str,str], correct: str, category: str):
        self.difficulty, self.text, self.answers, self.correct, self.category = difficulty, q_text, answers, correct, category
        Question.allQuestions.append(self)
        Question.categories.append(self.category)

    def __str__(self) -> str:
        return f"[{self.difficulty}-{self.category}] '{self.text}' [{','.join([ans for ans in self.answers])}]<-{self.correct}"

    @classmethod
    def getRandomQuestion(self, difficulty_criteria: int, category_criteria=None):
        if not category_criteria: category_criteria = choice(Question.categories)
        _l = []
        for question in self.allQuestions:
            if question.difficulty == difficulty_criteria:
                _l.append(question)
        return choice(_l)
