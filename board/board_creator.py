import random
from typing import List, Tuple, Optional
from datetime import datetime
from cell import Cell
from placement import Placement, PlacementType
from board_data import BoardData

class Board:
    def __init__(self, x_cells: int, y_cells: int):
        self.x_cells = x_cells
        self.y_cells = y_cells
        self.grid: List[List[Cell]] = []
        self.rand = random.Random()
        self.placed_verticals: List[bool] = []
        
        # Initialize grid
        for x in range(x_cells):
            self.grid.append([])
            self.placed_verticals.append(False)
            for y in range(y_cells):
                cell = Cell(x, y)
                self.grid[x].append(cell)

class BoardCreator:
    @staticmethod
    def create(shuffle: bool, words: List[str], preferred_rows: int, preferred_cols: int, seed: int = 0) -> Optional[BoardData]:
        start = datetime.now()
        rand = random.Random(seed if seed != 0 else 99)
        
        # Try creating board with increasing size until success
        add = 0
        for i in range(1000):
            rows = preferred_rows + add
            cols = preferred_cols + add
            
            # Create blank board
            board = Board(cols, rows)
            board.rand = rand
            
            # Try to place all words
            if BoardCreator._place_words(board, words, 0):
                seconds = (datetime.now() - start).total_seconds()
                print(f"board create finish:{seconds},rows={rows},cols={cols}")
                return BoardCreator._create_board_data(board)
            
            add += 1
        
        print(f"[BoardCreator] Failed creating a board with the given input row={preferred_rows} col={preferred_cols}")
        return None

    @staticmethod
    def _place_words(board: Board, words: List[str], next_word_index: int) -> bool:
        if next_word_index >= len(words):
            return True
            
        word_to_place = words[next_word_index]
        possible_placements, num_horizontal = BoardCreator._get_possible_starting_placements(
            board, len(word_to_place), next_word_index == 0)
            
        # Try random placements until success
        for i in range(len(possible_placements)):
            if num_horizontal != 0:
                if random.randint(0, 100) % 2 == 0:
                    # Pick horizontal word
                    rand_index = board.rand.randint(
                        len(possible_placements) - num_horizontal,
                        len(possible_placements) - 1
                    )
                    num_horizontal -= 1
                else:
                    # Pick vertical word
                    rand_index = board.rand.randint(0, num_horizontal - 1)
            else:
                rand_index = board.rand.randint(i, len(possible_placements) - 1)
                
            placement = possible_placements[rand_index]
            possible_placements[rand_index], possible_placements[i] = possible_placements[i], placement
            
            # Place word and try to place remaining words
            BoardCreator._place_word_at(board, word_to_place, placement)
            
            if BoardCreator._place_words(board, words, next_word_index + 1):
                return True
                
            # If we get here, placement failed - undo and try again
            BoardCreator._undo_placement(board, placement)
            
        return False

    @staticmethod
    def _create_board_data(board: Board) -> BoardData:
        board_data = BoardData()
        board_data.rows = board.y_cells
        board_data.cols = board.x_cells
        
        # Initialize the board with empty lists
        for _ in range(board_data.rows):
            board_data.board.append(['\0'] * board_data.cols)
            
        # Convert the Board's grid to BoardData's board
        for row in range(board.y_cells):
            for col in range(board.x_cells):
                board_data.board[row][col] = board.grid[col][row].letter
                
        BoardCreator._trim_board_data(board_data)
        return board_data

    @staticmethod
    def _trim_board_data(board_data: BoardData):
        # Trim blank columns
        col = board_data.cols - 1
        while col >= 0:
            if board_data.board[0][col] == '\0':
                for row in range(board_data.rows):
                    board_data.board[row].pop(col)
                board_data.cols -= 1
            col -= 1

        # Trim blank rows
        row = board_data.rows - 1
        while row >= 0:
            is_blank = True
            for col in range(board_data.cols):
                if board_data.board[row][col] != '\0':
                    is_blank = False
                    break
            if not is_blank:
                break
            board_data.board.pop(row)
            board_data.rows -= 1
            row -= 1

    @staticmethod
    def _get_possible_starting_placements(board: Board, word_length: int, is_first_word: bool) -> Tuple[List[Placement], int]:
        num_horizontal = 0
        possible_placements = []
        col_blanks = [0] * board.x_cells

        for y in range(board.y_cells - 1, -1, -1):
            h_max_len = 0
            h_min_len = 1
            bottom_row = (y == 0)
            bottom_blank_cells = 0
            bottom_blank_cells_seen = 0

            if bottom_row:
                for x in range(board.x_cells):
                    if board.grid[x][y].letter == '\0':
                        bottom_blank_cells += 1
                h_min_len = -1

            for x in range(board.x_cells - 1, -1, -1):
                cur_cell = board.grid[x][y]
                below_cell = board.grid[x][y-1] if y > 0 else None

                if cur_cell.letter == '\0':
                    col_blanks[x] += 1
                    if bottom_row:
                        bottom_blank_cells_seen += 1
                elif bottom_row and word_length <= board.y_cells:
                    if (bottom_blank_cells_seen > 0 and x > 0 and 
                        board.grid[x-1][0].letter != '\0'):
                        possible_placements.insert(0, Placement(cur_cell, PlacementType.SHIFT_RIGHT))
                    if (bottom_blank_cells - bottom_blank_cells_seen > 0 and 
                        x < board.x_cells - 1 and board.grid[x+1][0].letter != '\0'):
                        possible_placements.insert(0, Placement(cur_cell, PlacementType.SHIFT_LEFT))

                if col_blanks[x] > 0 and (below_cell is None or below_cell.letter != '\0'):
                    h_max_len += 1
                else:
                    h_max_len = 0

                if is_first_word or cur_cell.letter != '\0':
                    h_min_len = 1
                elif h_min_len != -1:
                    h_min_len += 1

                if h_min_len != -1 and word_length <= h_max_len and word_length >= h_min_len:
                    possible_placements.append(Placement(cur_cell, PlacementType.HORIZONTAL))
                    num_horizontal += 1

                if (not board.placed_verticals[x] and col_blanks[x] >= word_length and
                    ((bottom_row and is_first_word) or cur_cell.letter != '\0')):
                    possible_placements.insert(0, Placement(cur_cell, PlacementType.VERTICAL))

        return possible_placements, num_horizontal

    @staticmethod
    def _place_word_at(board: Board, word: str, placement: Placement):
        if placement.type == PlacementType.VERTICAL:
            BoardCreator._push_letters_up(board, placement.cell.x, placement.cell.y, len(word))
        elif placement.type == PlacementType.SHIFT_RIGHT:
            BoardCreator._shift_columns_right(board, placement.cell.x)
        elif placement.type == PlacementType.SHIFT_LEFT:
            BoardCreator._shift_columns_left(board, placement.cell.x)

        # 50% chance to flip the word
        flip_word = board.rand.randint(0, 1) == 0

        for i in range(len(word)):
            cell_x = placement.cell.x + (i if placement.type == PlacementType.HORIZONTAL else 0)
            cell_y = placement.cell.y + (i if placement.type == PlacementType.VERTICAL else 0)
            cell = BoardCreator._get_cell(board, cell_x, cell_y)

            if placement.type == PlacementType.HORIZONTAL:
                BoardCreator._push_letters_up(board, cell_x, cell_y, 1)

            letter_index = len(word) - i - 1 if flip_word else i
            cell.letter = word[letter_index]

        if placement.type != PlacementType.HORIZONTAL:
            board.placed_verticals[placement.cell.x] = True

    @staticmethod
    def _push_letters_up(board: Board, x: int, y: int, num_spaces: int):
        cell = BoardCreator._get_cell(board, x, y)
        if cell.letter == '\0':
            return

        BoardCreator._push_letters_up(board, x, y + 1, num_spaces)
        target_cell = BoardCreator._get_cell(board, x, y + num_spaces)
        target_cell.letter = cell.letter
        cell.letter = '\0'

    @staticmethod
    def _shift_columns_left(board: Board, col_x: int):
        for x in range(1, col_x + 1):
            for y in range(board.y_cells):
                from_cell = board.grid[x][y]
                to_cell = board.grid[x-1][y]
                to_cell.letter = from_cell.letter
                if x == col_x:
                    from_cell.letter = '\0'
            board.placed_verticals[x-1] = board.placed_verticals[x]

    @staticmethod
    def _shift_columns_right(board: Board, col_x: int):
        for x in range(board.x_cells - 2, col_x - 1, -1):
            for y in range(board.y_cells):
                from_cell = board.grid[x][y]
                to_cell = board.grid[x+1][y]
                to_cell.letter = from_cell.letter
                if x == col_x:
                    from_cell.letter = '\0'
            board.placed_verticals[x+1] = board.placed_verticals[x]

    @staticmethod
    def _get_cell(board: Board, x: int, y: int) -> Cell:
        while y >= board.y_cells:
            for i in range(board.x_cells):
                cell = Cell(i, board.y_cells)
                board.grid[i].append(cell)
            board.y_cells += 1
        return board.grid[x][y]

    @staticmethod
    def _undo_placement(board: Board, placement: Placement):
        if placement.type == PlacementType.VERTICAL:
            board.placed_verticals[placement.cell.x] = False
        # Clear letters
        for y in range(board.y_cells):
            for x in range(board.x_cells):
                board.grid[x][y].letter = '\0' 