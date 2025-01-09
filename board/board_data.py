from typing import List

class BoardData:
    def __init__(self):
        self.rows: int = 0
        self.cols: int = 0
        self.board: List[List[str]] = []
    
    def __str__(self) -> str:
        result = [f"{self.rows},{self.cols}"]
        for i in range(len(self.board)-1, -1, -1):
            row = ""
            for j in range(len(self.board[0])-1, -1, -1):
                c = self.board[i][j]
                row += '-' if c == '\0' else c
            result.append(row)
        return "\n".join(result) 