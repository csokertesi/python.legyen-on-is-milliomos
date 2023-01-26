#region imports
from time import sleep
from os import path
import sys
from random import choice as rand_choice
from random import randint as rand_int
from question import Question
#endregion

# region Package validation
## Curses install
try:
    import curses
except ModuleNotFoundError:
    python = sys.executable
    print(f"Hiányzó curses modul! Telepítés:\n\tWindows:\t{python} -m pip install windows-curses\n\tMás:\t\t{python} -m pip install curses")
    exit(1)
## Playsound install
try:
    from audioplayer import AudioPlayer
except ModuleNotFoundError:
    python = sys.executable
    print(f"Hiányzó audioplayer modul! Telepítés:\n\t{python} -m pip install audioplayer")
    exit(1)

# endregion

# region Constants, Variables
## Constants
WIN_MINX = 16
WIN_MINY = 20 
Q_PATH = "./kerdes.txt"
SEP = ";"
TITLE = " Legyen Ön is milliomos! "
SOUND_ENABLED = True
SOUND_PATH = "test_sound"
A,B,C,D = 0,1,2,3
KEYS = { #lo,up case codes
    'a': [97,65],
    'b': [98,66],
    'c': [99,67],
    'd': [100,68],
    'f': [102,70],
    't': [116,84],
    'k': [107,75]
}
PRICE = [10_000,20_000,50_000,100_000,250_000,500_000,750_000,1_000_000,1_500_000,2_000_000,5_000_000,10_000_000,15_000_000,25_000_000,50_000_000]
CURRENCY = ['',' Ft']
SUPPORTCORRECT = {'telefon': 0.75, 'közönség': 0.88}
focimdal: AudioPlayer = None
## Variables
stage = "start"
soundthreads = []
question: Question = None
optionselected = A
support = {'felezés': True, 'telefon': True, 'közönség': True}
fix_win = 0
option_attr = {A:'normal',B:'normal',C:'normal',D:'normal'}
questions = {1:[],2:[],3:[],4:[],5:[],6:[],7:[],8:[],9:[],10:[],11:[],12:[],13:[],14:[],15:[]}
sounds = {}
# endregion

# region

def stopsounds():
    for k in sounds.keys():
        sounds[k].stop()

def loadsound(lvl: int):
    sounds[f"{lvl}_1"] = AudioPlayer(f"./{SOUND_PATH}/{lvl}_1.mp3")
    sounds[f"{lvl}_2"] = AudioPlayer(f"./{SOUND_PATH}/{lvl}_2.mp3")
    sounds[f"{lvl}_3"] = AudioPlayer(f"./{SOUND_PATH}/{lvl}_3.mp3")
    sounds[f"{lvl}_w"] = AudioPlayer(f"./{SOUND_PATH}/{lvl}_w.mp3")
    sounds[f"{lvl}_l"] = AudioPlayer(f"./{SOUND_PATH}/{lvl}_l.mp3")

def playsound(sound: str):
    sounds[sound].play(block=False)
    
def load_questions():
    if not path.exists(Q_PATH):
        return False
    with open(Q_PATH, "r", encoding="utf8") as f:
        for line in f.readlines():
            spl = line.split(SEP)
            spl[-1] = spl[-1].strip() # Remove \n
            _q = Question(int(spl[0]), spl[1], [spl[2],spl[3],spl[4],spl[5]], spl[6], spl[7]) # class already handles questions in Question.allQuestions
            questions[int(spl[0])].append(_q)
    return True

def color_setup():
    if curses.has_colors():
        curses.start_color()
    curses.init_pair(100, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Normal colors
    curses.init_pair(101, curses.COLOR_RED, curses.COLOR_BLACK)     # Small window error colors
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_WHITE)      # Highlighted text colors
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_BLUE)      # Black
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_GREEN)     # Correct answer
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_YELLOW)    # Recommendation
    curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_BLUE)      # Not available
    

def basic_draw(scr: curses.window):
    _, winx = scr.getmaxyx()
    scr.bkgd(' ', curses.color_pair(100))
    scr.clear()
    scr.border(0)
    scr.addstr(0,winx//2-(len(TITLE)//2),TITLE, curses.color_pair(1) + curses.A_BOLD)

def center_align(text: str, length: int) -> str:
    l = length // 2+len(text)//2
    text = f"{text:>{l}}"
    text = f"{text:<{length}}"
    return text

def getoptioncolor(name: str):
    if name == 'answer':
        return curses.color_pair(3)
    if name == 'normal':
        return curses.color_pair(100)
    if name == 'recomm':
        return curses.color_pair(4) + curses.A_BOLD
    if name == 'navail':
        return curses.color_pair(5) + curses.A_ITALIC

def draw_options(scr: curses.window, options: list[str,str,str,str], selected:int = -1, animated:bool=True):
    delay = 1.5
    winy,winx = scr.getmaxyx()
    add = len(" #)  ")
    longest = len(max(options, key=lambda o: len(o))) + add
    # ---- Option A ----
    a = center_align( " A) " + options[A] + " ", length=longest - add)
    scr.addstr(
        winy // 2,                      # Y: height/2
        winx // 2 - longest - 1,        # X: width/2 - longest - 1 for padding
        a,
        curses.color_pair(1) if selected==A else getoptioncolor(option_attr[A])
    )
    scr.refresh()
    if animated: sleep(delay)
    # ---- Option B ----
    b = center_align( " B) " + options[B] + " ", length=longest - add)
    scr.addstr(
        winy // 2,                      # Y: height/2
        winx // 2 + 1,                  # X: center + 1 padding
        b,
        curses.color_pair(1) if selected==B else getoptioncolor(option_attr[B])
    )
    scr.refresh()
    if animated: sleep(delay)
    # ---- Option C ----
    c = center_align( " C) " + options[C] + " ", length=longest - add)
    scr.addstr(
        winy // 2 + 2,                  # Y: height/2 + 2 padding
        winx // 2 - longest - 1,        # X: width/2 - longest - 1 for padding
        c,
        curses.color_pair(1) if selected==C else getoptioncolor(option_attr[C])
    )
    scr.refresh()
    if animated: sleep(delay)
    # ---- Option D ----
    d = center_align( " D) " + options[D] + " ", length=longest - add)
    scr.addstr(
        winy // 2 + 2,                  # Y: height/2 + 2 padding
        winx // 2 + 1,                  # X: center + 1 padding
        d,
        curses.color_pair(1) if selected==D else getoptioncolor(option_attr[D])
    )
    scr.refresh()

def draw_support(scr, support):
    winy,winx = scr.getmaxyx()
    _t = "Felhasználható segítségek:"
    scr.addstr(winy//2+5, winx//2-len(_t)//2, _t)
    for indx, sup in enumerate(support.keys()):
        i = support[sup]
        if i:
            _t = f"{sup[0]}: {sup}"
            scr.addstr(winy//2+6+indx, winx//2-len(_t)//2, _t)
        else:
            _t = f"{sup[0]}: {sup}"
            scr.addstr(winy//2+6+indx, winx//2-len(_t)//2, _t, curses.color_pair(2))

#endregion

def game_intro(scr: curses.window) -> bool:
    winy, winx = scr.getmaxyx()
    basic_draw(scr)
    text = "Üdv! Kezdhetjük? "
    button = " Igen "
    scr.addstr(winy//2, winx//2-(len(text))//2, text)
    scr.addstr(winy//2+1, (winx//2-(len(button))//2), button, curses.color_pair(1))
    scr.refresh()
    k = scr.getch()
    if k == 10:
        return True
    return False

def game_tutorial(scr: curses.window) -> bool:
    winy, winx = scr.getmaxyx()
    scr.clear()
    basic_draw(scr)
    texts = ["A következő kérdésekre négy lehetőség közül kell választania.","A játék közben felhasználhat segítségeket:","","Felezés", "Telefon", " Közönség"]
    ceny = winy//2
    cenx = winx//2
    midi = len(texts) // 2
    for i,line in enumerate(texts):
        l = len(line)
        posx = cenx-l//2
        posy = ceny - abs(midi-i) * (1 if i < midi else -1)
        scr.addstr(posy,posx, line)
    scr.refresh()
    sleep(5)
    return True

def game_question(scr: curses.window, lvl: int) -> bool:
    global question
    loadsound(lvl)
    winy, winx = scr.getmaxyx()
    question = rand_choice(questions[lvl])
    scr.clear()
    basic_draw(scr)
    scr.refresh()
    playsound(f"{lvl}_1")
    sleep(8)
    _t = f"{lvl}. {question.text}"
    scr.addstr(winy//4,winx//2-(len(_t)//2), _t)
    _p = f"{CURRENCY[0]}{PRICE[lvl-1]:,}{CURRENCY[1]}"
    scr.addstr(winy//4+2,winx//2-(len(_p)//2), _p)
    scr.refresh()

    playsound(f"{lvl}_2")
    sleep(1)
    
    draw_options(scr, question.answers, option_selected - 1)

    draw_support(scr, support)

    scr.refresh()
    sleep(0.1)
    return True

def main(scr: curses.window):
    global stage
    global sound_threads
    global option_selected
    global option_attr
    global fix_win
    global questions
    # region Curses setup
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    scr.keypad(True)
    scr.nodelay(True)
    scr.clear()
    color_setup()
    # endregion

    if not load_questions():
        curses.beep()
        print(f"Hiba! A kérdések fájl ({Q_PATH}) nem találva!")
        exit(1)
    scr.clear()

    # Modifying loaded questions
    for k in questions:
        questions[k] = list(map(lambda x: (x,)[list(map(lambda val: val+(1 if int(val)%(int((True,)[0]*2))!=3 else 1), (True,)))[0]-(list(map(lambda val: val+(1 if int(val)%(int((True,)[0]*2))!=3 else 1), (True,)))[0])] if print else ([SyntaxError, (lambda _: i for i in range(10))]), list(map(lambda x: (x,)[list(map(lambda val: val+(1 if int(val)%(int((True,)[0]*2))!=3 else 1), (True,)))[0]-(list(map(lambda val: val+(1 if int(val)%(int((True,)[0]*2))!=3 else 1), (True,)))[0])] if print else ([SyntaxError, (lambda _: i for i in range(10))]), (questions[k],exit,)[:-1] if not input else (questions[k], [ZeroDivisionError])[int((True,)[0])-1]))))

    while True:
        k = scr.getch()
        # region Quit program keys
        if k in [27,3,113]:
            break
        # endregion

        # region Option Select keys
        up, down, left, right = 259, 258, 260, 261
        if option_selected == A:
            if k == up or k == down:
                if option_attr[C] != 'navail':
                    option_selected = C
            if k == left or k == right:
                if option_attr[B] != 'navail':
                    option_selected = B
        elif option_selected == B:
            if k == up or k == down:
                if option_attr[D] != 'navail':
                    option_selected = D
            if k == left or k == right:
                if option_attr[A] != 'navail':
                    option_selected = A
        elif option_selected == C:
            if k == up or k == down:
                if option_attr[A] != 'navail':
                    option_selected = A
            if k == left or k == right:
                if option_attr[D] != 'navail':
                    option_selected = D
        elif option_selected == D:
            if k == up or k == down:
                if option_attr[B] != 'navail':
                    option_selected = B
            if k == left or k == right:
                if option_attr[C] != 'navail':
                    option_selected = C
        # literal select keys
        if k in KEYS['a']:
            if option_attr[A] != 'navail':
                option_selected = A
        elif k in KEYS['b']:
            if option_attr[B] != 'navail':
                option_selected = B
        elif k in KEYS['c']:
            if option_attr[C] != 'navail':
                option_selected = C
        elif k in KEYS['d']:
            if option_attr[D] != 'navail':
                option_selected = D
        # endregion

        # region Small window check
        winy, winx = scr.getmaxyx()
        if winy <= WIN_MINY or winx <= WIN_MINX:
            scr.bkgd(' ', curses.color_pair(101))
            scr.clear()
            scr.addstr(0,0, "Túl kicsi ablak!")
            scr.refresh()
            continue
        # endregion
        
        scr.refresh()
        if stage == "start":
            if game_intro(scr):
                stage = "tutorial"
        elif stage == "tutorial":
            focimdal.stop()
            if game_tutorial(scr):
                for i in range(1,16):
                    loadsound(i)    
                stage = "1q"
        else:
            ss:str = stage[-1]
            sn:int = int(stage[:-1])
            if ss == "q":
                if game_question(scr, lvl=int(sn)):
                    stage = f"{sn}a"
            elif ss == "a":
                draw_options(scr, question.answers,option_selected, False)
                if k == 10:
                    stopsounds()
                    _os = "ABCD"[option_selected]
                    playsound(f"{sn}_3")
                    sleep(3)
                    option_selected = -1
                    option_attr["ABCD".index(question.correct)] = 'answer'
                    draw_options(scr, question.answers,option_selected, False)
                    if _os == question.correct:
                        playsound(f"{sn}_w")
                        sleep(8 if sn != 15 else 26)
                        option_attr = {A:'normal',B:'normal',C:'normal',D:'normal'}
                        option_selected = A
                        if sn in [5,10,15]:
                            fix_win = PRICE[sn-1]
                        if sn == 15:
                            break
                        stopsounds()
                        stage = f"{sn+1}q"
                    else:
                        playsound(f"{sn}_l")
                        sleep(6 if sn != 15 else 10)
                        break
                elif k in KEYS["f"]:
                    if support["felezés"]:
                        support["felezés"] = False
                        draw_support(scr, support)
                        corr = "ABCD".index(question.correct) + 1
                        available = [A,B,C,D]
                        del available[corr - 1]
                        _n:int = rand_int(0,2)
                        choice = available[_n]
                        option_attr[choice] = "navail"
                        del available[_n]
                        _n:int = rand_int(0,1)
                        choice = available[_n]
                        option_attr[choice] = "navail"
                        draw_options(scr, question.answers,option_selected, False)
                        del available[_n]
                        option_selected = available[0]
                elif k in KEYS["t"]:
                    if "recomm" in [option_attr[A], option_attr[B], option_attr[C], option_attr[C]]:
                        pass
                    elif support["telefon"]:
                        support["telefon"] = False
                        draw_support(scr, support)
                        corr = rand_int(0,100) < SUPPORT_CORRECT["telefon"]*100
                        indx = "ABCD".index(question.correct)
                        if corr:
                            option_attr[indx] = "recomm"
                        else:
                            l = [0,1,2,3]
                            del l[indx]
                            option_attr[rand_choice(l)] = "recomm"
                        draw_options(scr, question.answers, option_selected, False)
                elif k in KEYS["k"]:
                    if "recomm" in [option_attr[A], option_attr[B], option_attr[C], option_attr[C]]:
                        pass
                    elif support["közönség"]:
                        support["közönség"] = False
                        draw_support(scr, support)
                        corr = rand_int(0,100) < SUPPORT_CORRECT["közönség"]*100
                        indx = "ABCD".index(question.correct)
                        if corr:
                            option_attr[indx] = "recomm"
                        else:
                            l = [0,1,2,3]
                            del l[indx]
                            option_attr[rand_choice(l)] = "recomm"
                        draw_options(scr, question.answers, option_selected, False)    

    scr.clear()
    stopsounds()
    if fix_win > 0:
        print(f"Gratulálunk! Az ön nyereménye {CURRENCY[0]}{fix_win:,}{CURRENCY[1]}!")
    else:
        print(f"Köszönjük szépen, hogy itt volt.")

if __name__ == "__main__":
    focimdal = AudioPlayer(f"./{SOUND_PATH}/focimdal.mp3")
    focimdal.play()
    curses.wrapper(main)

sleep(10)