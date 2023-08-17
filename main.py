import random
import numpy as np

class NineHoles:
    def __init__(self):
        self.board = np.zeros((3, 3), dtype=int)
        self.player = 1
        self.cpu_player = 2
        # 1 = X pieces
        # 2 = O pieces
        self.player_x_pieces = 3
        self.player_o_pieces = 3

    def draw_board(self):
        print(' ' * 2, 'A', 'B', 'C')
        print(' ' * 1, '-' * 7)
        for i in range(len(self.board)):
            row = self.board[i]
            row_display = np.where(row == self.player, 'X', np.where(row == self.cpu_player, 'O', ' '))
            print(i + 1, '|' + '|'.join(row_display) + '|')
            print(' ' * 1, '-' * 7)
            
    def make_move(self, player_code, row, col, old_row=None, old_col=None):
        if old_row is not None and old_col is not None:
            if self.board[old_row, old_col] != player_code or self.board[row, col] != 0:
                return False
            self.board[old_row, old_col] = 0
        elif self.board[row, col] != 0:
            return False
        self.board[row, col] = player_code
        return True
    
    def get_all_empty_spaces(self):
        moves = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves
    
    def get_all_pieces(self, player_code):
        pieces = []
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] == player_code:
                    pieces.append((i, j))
        return pieces
    
    def cpu_placement_move(self):
        # AI try to win
        win, win_move = self.is_one_move_away(self.cpu_player)
        # AI try not to lose
        loss, move = self.is_one_move_away(self.player)
        if win:
            self.make_move(self.cpu_player, win_move[0], win_move[1])
        elif loss:
            self.make_move(self.cpu_player, move[0], move[1])
        else:
            x, y = random.choice(self.get_all_empty_spaces())
            self.make_move(self.cpu_player, x, y)
        if self.cpu_player == 1:
            self.player_x_pieces -= 1 
        else: 
            self.player_o_pieces -= 1 

    def is_one_move_away(self, player_code):
        # Check if the player is one move away from winning
        for i, row in enumerate(self.board):
            if np.count_nonzero(row == player_code) == 2 and np.count_nonzero(row == 0) == 1:
                for j in range(len(row)):
                    if row[j] == 0:
                        return True, (i, j)
        for col in range(3):
            if np.count_nonzero(self.board[:, col] == player_code) == 2 and np.count_nonzero(self.board[:, col] == 0) == 1:
                for i in range(len(self.board)):
                    if self.board[i][col] == 0:
                        return True, (i, col)
        if np.count_nonzero(np.diag(self.board) == player_code) == 2 and np.count_nonzero(np.diag(self.board) == 0) == 1:
            for i in range(len(self.board)):
                if self.board[i][i] == 0:
                    return True, (i, i)
        if np.count_nonzero(np.diag(np.fliplr(self.board)) == player_code) == 2 and np.count_nonzero(np.diag(np.fliplr(self.board)) == 0) == 1:
            for i in range(len(self.board)):
                if self.board[i][2 - i] == 0:
                    return True, (i, 2 - i)
        return False, None
    
    def is_two_in_a_row(self, player_code, board):
        # Check if the player has two pieces in a row, column, or diagonal and one empty space
        for i in range(3):
            # Check rows
            if np.count_nonzero(board[i, :] == player_code) == 2 and np.count_nonzero(board[i, :] == 0) == 1:
                return True
            # Check columns
            if np.count_nonzero(board[:, i] == player_code) == 2 and np.count_nonzero(board[:, i] == 0) == 1:
                return True
        
        # Check diagonals
        if np.count_nonzero(np.diag(board) == player_code) == 2 and np.count_nonzero(np.diag(board) == 0) == 1:
            return True
        if np.count_nonzero(np.diag(np.fliplr(board)) == player_code) == 2 and np.count_nonzero(np.diag(np.fliplr(board)) == 0) == 1:
            return True
        
        return False
    
    def is_one_gap_one(self, player_code, board):
        # Check if the player has a pattern of one piece, gap, and one piece in a row, column, or diagonal
        for i in range(3):
            # Check rows
            for j in range(len(board[i]) - 2):
                if board[i][j] == player_code and board[i][j+1] == 0 and board[i][j+2] == player_code:
                    return True
            # Check columns
            for j in range(len(board) - 2):
                if board[j][i] == player_code and board[j+1][i] == 0 and board[j+2][i] == player_code:
                    return True
        
        # Check diagonals
        if board[0][0] == player_code and board[1][1] == 0 and board[2][2] == player_code:
            return True
        if board[0][2] == player_code and board[1][1] == 0 and board[2][0] == player_code:
            return True
        
        return False
    
    def evaluate_board(self, board):
        score = 0
        if self.check_win(self.cpu_player, board):
            return float('+inf')
        if self.is_two_in_a_row(self.player, board):
            score += -1000000
        if self.is_one_gap_one(self.player, board):
            score += -1000000
        if self.is_two_in_a_row(self.cpu_player, board):
            score += 1
        if self.is_one_gap_one(self.cpu_player, board):
            score += 1
        return score

    def cpu_movement_move(self):
        empty_spaces = self.get_all_empty_spaces()
        best_score = float('-inf')
        best_move = None
        
        for x1, y1 in self.get_all_pieces(self.cpu_player):
            for x2, y2 in empty_spaces:
                # Make a temporary move and evaluate the resulting board
                temp_board = np.copy(self.board)
                temp_board[x2, y2] = self.cpu_player
                temp_board[x1, y1] = 0
                score = self.evaluate_board(temp_board)
                
                # Update the best move if a higher score is found
                if score > best_score:
                    best_score = score
                    best_move = (x2, y2, x1, y1)
        self.make_move(self.cpu_player, best_move[0], best_move[1], best_move[2], best_move[3])

    def check_win(self, player_code, board):
        for row in board:
            if np.count_nonzero(row == player_code) == 3:
                return True
        for col in range(3):
            if np.count_nonzero(board[:, col] == player_code) == 3:
                return True
        if np.count_nonzero(np.diag(board) == player_code) == 3:
            return True
        if np.count_nonzero(np.diag(np.fliplr(board)) == player_code) == 3:
            return True
        return False
    
    def play(self):
        while self.player_x_pieces > 0 and self.player_o_pieces > 0:
            self.draw_board()
            rowcol = input(f'Player {self.player}, enter row and column example (A1): ')
            if len(rowcol) != 2:
                continue
            start_col = ord(rowcol[0].upper()) - ord('A')
            start_row = int(rowcol[1]) - 1
            if self.make_move(self.player, start_row, start_col):
                if self.check_win(self.player, self.board):
                    self.draw_board()
                    print("Congratulations you win")
                    break
                if self.player == 1:
                    self.player_x_pieces -= 1 
                else: 
                    self.player_o_pieces -= 1 
                self.cpu_placement_move()
                if self.check_win(self.cpu_player, self.board):
                    self.draw_board()
                    print("Sorry you lost")
                    break
        if not self.check_win(self.cpu_player, self.board) and not self.check_win(self.player, self.board):
            while True:
                self.draw_board()
                rowcol = input(f'Player {self.player}, enter row and column to move from and then move to example (A1A2): ')
                if len(rowcol) != 4:
                    continue
                start_col = ord(rowcol[0].upper()) - ord('A')
                start_row = int(rowcol[1]) - 1
                end_col = ord(rowcol[2].upper()) - ord('A')
                end_row = int(rowcol[3]) - 1
                if self.make_move(self.player, end_row, end_col, start_row, start_col):
                    if self.check_win(self.player, self.board):
                        self.draw_board()
                        print("Congratulations you win")
                        break
                    self.cpu_movement_move()
                    if self.check_win(self.cpu_player, self.board):
                        self.draw_board()
                        print("Sorry you lost")
                        break


if __name__ == '__main__':
    game = NineHoles()
    game.play()
