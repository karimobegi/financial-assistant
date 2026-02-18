from math import inf
from board import Direction, Rotation, Action, Shape
from random import Random
import time

# how many lines were cleared from a score delta to use in a function later
LINES_SCORE = {25:1,100:2,400:3,1600: 4}

class Player:
    def choose_action(self, board):
        raise NotImplementedError

class RandomPlayer(Player):
    def __init__(self, seed=None):
        self.random = Random(seed)

    def print_board(self, board):
        print("--------")
        for y in range(24):
            s = ""
            for x in range(10):
                s += "#" if (x, y) in board.cells else "."
            print(s, y)

    def choose_action(self, board):
        self.print_board(board)
        time.sleep(0.5)
        if self.random.random() > 0.97:
            return self.random.choice([Action.Discard, Action.Bomb])
        else:
            return self.random.choice([
                Direction.Left,
                Direction.Right,
                Direction.Down,
                Rotation.Anticlockwise,
                Rotation.Clockwise,
            ])
#this functino is used to roate a block
def rotate_piece(block, board, n):
    for i in range(n):
        block.rotate(Rotation.Clockwise, board)
#this function moves the block horizontally
def move_piece_horiz(block, board, dx):
    if dx>0:
        for _ in range(dx):
            block.move(Direction.Right, board)
    elif dx<0:
        for _ in range(-dx):
            block.move(Direction.Left, board)
#holes will be used in the code later
def count_holes(board):
    holes=0
    for x in range(board.width):
        seen_block= False
        for y in range(board.height):
            if (x,y) in board.cells:
                seen_block =True
            elif seen_block:
                holes+= 1
    return holes
def column_heights(board):
    h =[0]* board.width
    for x in range(board.width):
        ys =[y for (cx,y) in board.cells if cx==x]
        h[x]= board.height-min(ys) if ys else 0
    return h
def bumpiness(heights):
    return sum(abs(heights[i]-heights[i+1])
               for i in range(len(heights)-1))
#wells can be good or bad because i can try to score points on them being deep
def wells(heights):
    total=0
    W=len(heights)
    for i in range(1,W-1):
        rim = min(heights[i-1], heights[i+1])
        if rim>heights[i]:
            depth=rim-heights[i]
            if depth >=3:
                total+= depth
    if W >=2:
        total +=max(0, heights[1] - heights[0])
        total +=max(0, heights[-2] - heights[-1])
    return total
def cliff_penalty(h):
    #Sometimes, I die early becasue of cliffs so I have to penalise that
    pen=0
    W=len(h)
    for i in range(1,W- 1):
        L = h[i]- h[i-1]
        R = h[i]-h[i+ 1]
        spike = max(L, R)
        if spike > 2:
            pen += (spike - 2) * 7
    return pen
#a high plateau can also be bad so  need to evalute that
def high_plateau_penalty(h, H):
    p=0
    for i in range(len(h)-3):
        seg=h[i:i+4]
        if min(seg) >= H - 8:
            p += sum(seg)
    return p
def blocked_cells(board):
    blocked=0
    for x in range(board.width):
        for y in range(board.height-1,-1,-1):
            if (x, y) not in board.cells:
                left_blocked=x==0 or (x-1,y) in board.cells
                right_blocked=x== board.width-1 or (x+1,y) in board.cells
                top_blocked =y > 0 and (x,y -1) in board.cells
                if left_blocked and right_blocked and top_blocked:
                    blocked += 1
    return blocked
def row_transitions(board):
    trans= 0
    for y in range(board.height):
        for x in range(board.width-1):
            if ((x,y) in board.cells) != ((x+1,y) in board.cells):
                trans+=1
    return trans
def col_transitions(board):
    trans=0
    for x in range(board.width):
        for y in range(board.height-1):
            if ((x,y) in board.cells) != ((x,y+1) in board.cells):
                trans+=1
    return trans
def tetris_setup_bonus(board, well_x=0):
    bonus_rows=0
    for y in range(board.height):
        filled_non_well=0
        gap_in_well=((well_x,y) not in board.cells)
        bad_gap=False
        for x in range(board.width):
            if x==well_x:
                if (x,y) in board.cells:
                    bad_gap= True
                    break
            else:
                if (x,y) in board.cells:
                    filled_non_well += 1
                else:
                    bad_gap =True
                    break
        if not bad_gap and gap_in_well and filled_non_well == board.width - 1:
            bonus_rows+= 1
    return bonus_rows
def score(board, base_score=0, W=None, prev_holes=None):
    if W is None:
        W = {
            "holes":       29.5,#29.5
             "aggH":        0.38,#0.38
              "bump":        0.22,#0.22
            "maxH":        0.20,#0.20
             "score":       1.0,#1.0
             "new_holes":   2.5,#2.5
              "plateau":     0.04,#0.04
             "cliff":       0.6,#0.6
             "left_col":    0.8,#0.8
              "wells":      -0.3,  #-0.3
            
        }
    h = column_heights(board)
    agg = sum(h)
    mx = max(h) if h else 0
    bum = bumpiness(h)
    hol = count_holes(board)
    wel = wells(h)
    sd = board.score - base_score
    h0 = h[0] if h else 0
    ts = tetris_setup_bonus(board, well_x=0)
    val = (W["score"] * sd- W["holes"] * hol - W["aggH"] * agg- W["bump"] * bum- W["maxH"] * mx-W["plateau"] * high_plateau_penalty(h, board.height)- W["cliff"] * cliff_penalty(h)- W["left_col"] * h0+W["wells"] * wel
+ W["tetris_setup"] * ts)
    if prev_holes is not None:
        new_h=max(0, hol - prev_holes)
        val -= W["new_holes"] * new_h
    return val
def count_clearable_lines(board):
    count =0
    for y in range(board.height):
        if all((x,y) in board.cells for x in range(board.width)):
            count+=1
    return count


def simulate_board(board):
    best_eval=-inf
    best_rotation=0
    best_position=0
    any_valid=False
    base_score0=board.score
    prev_holes0=count_holes(board)
    h0=column_heights(board)
    mx0=max(h0) if h0 else 0
    for rot1 in range(4):
        cloned1=board.clone()
        if cloned1.falling is None:
            continue       
        rotate_piece(cloned1.falling,cloned1,rot1)
        piece_w1=cloned1.falling.right -cloned1.falling.left+ 1
        min_left1 =0
        max_left1= cloned1.width- piece_w1
        for x1 in range(min_left1, max_left1 + 1):
            temp1 =cloned1.clone()
            dx1 =x1 - temp1.falling.left
            move_piece_horiz(temp1.falling, temp1, dx1)
            dropped1 = temp1.falling.move(Direction.Drop, temp1)
            if not dropped1:
                continue
            temp1.land_block()
            if not temp1.alive:
                continue
            delta1= temp1.score- base_score0
            lines1=LINES_SCORE.get(delta1, 0)
            if lines1> 4:
                lines1= 0
            if lines1 ==4:
                return rot1,x1,99999 #basically if we can clear more than 3 lines we should immediately do it
            if lines1 == 3:
                return rot1,x1,90000
            val1 =score(temp1, base_score0, prev_holes=prev_holes0)
            if lines1== 2:
                val1 +=150
            h1=column_heights(temp1)
            mx1= max(h1) if h1 else 0
            danger1 =(mx1>=board.height- 6)
            height_penalty=0
            if danger1 and mx1 > mx0:
                height_penalty= 60 *(mx1- mx0)
            val1 -=height_penalty
            best_follow=-inf
            if temp1.falling is not None:
                base_score1=temp1.score
                prev_holes1= count_holes(temp1)
                for rot2 in range(4):
                    cloned2 =temp1.clone()
                    if cloned2.falling is None:
                        continue
                    rotate_piece(cloned2.falling, cloned2, rot2)
                    piece_w2 = cloned2.falling.right - cloned2.falling.left + 1
                    min_left2 = 0
                    max_left2 = cloned2.width - piece_w2
                    for x2 in range(min_left2, max_left2 + 1):
                        sim2=cloned2.clone()
                        dx2 =x2 -sim2.falling.left
                        move_piece_horiz(sim2.falling,sim2,dx2)
                        dropped2=sim2.falling.move(Direction.Drop, sim2)
                        if not dropped2:
                            continue
                        sim2.land_block()
                        if not sim2.alive:
                            continue
                        delta2 = sim2.score - base_score1
                        lines2 = LINES_SCORE.get(delta2, 0)
                        if lines2 > 4:
                            lines2 = 0
                        val2=score(sim2, base_score1, prev_holes=prev_holes1)
                        if lines2==4:
                            val2 +=400
                        elif lines2 ==3:
                            val2 +=180
                        elif lines2== 2:
                            val2 +=60
                        if val2>best_follow:
                            best_follow=val2
            if best_follow== -inf:
                total_val =val1
            else:
                if danger1:
                    alpha= 2.0
                    beta= 0.15
                else:
                    alpha=0.55
                    beta=1.1
                total_val =alpha* val1+beta * best_follow
            if total_val>best_eval:
                best_eval=total_val
                best_rotation=rot1
                best_position = x1
                any_valid =True
    if not any_valid:
        return None, None, -inf
    return best_rotation, best_position, best_eval
class myTetrisAI(Player):
    def __init__(self, weights=None):
        self.weights = weights
        self.discard_threshold = -175
        self.pieces_played = 0
        self.desperate_mode = False
    def choose_action(self, board):
        if board.falling is None:
            return None
        self.pieces_played += 1
        h = column_heights(board)
        max_h = max(h) if h else 0
        self.desperate_mode = (max_h >= board.height - 5)
        rot, target_x, eval_score = simulate_board(board)
        if rot is None or target_x is None:
            if board.bombs_remaining > 0:
                return [Action.Bomb]
            elif board.discards_remaining > 0:
                return [Action.Discard]
            return [Direction.Drop]
        if eval_score<self.discard_threshold and board.discards_remaining>0:
            if self.pieces_played<50 or self.desperate_mode:
                return [Action.Discard]
        if self.desperate_mode and board.bombs_remaining>0 and eval_score<-100:
            clearable = count_clearable_lines(board)
            if max_h >= board.height-4 and clearable <= 3:
                return [Action.Bomb]
        probe=board.clone()
        rotate_piece(probe.falling, probe, rot)
        dx=target_x- probe.falling.left
        path=[]
        path+=[Rotation.Clockwise] * rot
        if dx>0:
            path+= [Direction.Right]*dx
        elif dx <0:
            path += [Direction.Left]*(-dx)
        path += [Direction.Drop]
        return path
SelectedPlayer = myTetrisAI
