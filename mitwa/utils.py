from langchain.schema import BaseOutputParser


class BulletListOutputParser(BaseOutputParser[str]):
    def __init__(self, bullet: str = "-"):
        self.bullet = bullet

    def parse(self, output: str) -> list[str]:
        return [
            line[len(self.bullet) + 1 :]
            for line in output.split("\n")
            if line.startswith(f"{self.bullet} ")
        ]
