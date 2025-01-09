import random
from board_creator import BoardCreator

def get_random_char() -> str:
    return random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

def main():
    words = ["WORD", "CAT", "DOG", "MANAGER", "FLOWER"]

      # Calculate dimensions based on words
    max_word_length = max(len(word) for word in words)
    cols = max_word_length + 2  # 最长单词长度 + 2
    rows = len(words) + 2       # 单词数量 + 2
    
    data = BoardCreator.create(True, words, rows, cols)
    
    if data:
        # 倒序打印words 在一行
        print(" ".join(words[::-1]))
        
        # Fill empty cells with random letters
        for row in range(len(data.board)):
            for col in range(len(data.board[row])):
                if data.board[row][col] == '\0':
                    data.board[row][col] = get_random_char()
        
        print(data)

if __name__ == "__main__":
    main() 