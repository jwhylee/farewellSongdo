# ------------------------------- 모듈 -------------------------------#
import os
import pickle


# ------------------------------- 객체 -------------------------------#


# 아이템 객체: 이름 / HP 회복량
class Item:
    def __init__(self, name: str, recovery: int):
        self.name = name
        self.recovery = recovery


# 임무 객체: 임무 이름 / 설명 / 수령 여부 / 완료 여부
class Quest:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.received = False
        self.cleared = False


# 장소 객체: 구매 / 판매 / 정보 / 임무 여부 / 정답 여부
class Place:
    def __init__(
        self,
        name: str,
        buy_menu: dict = {},
        sell_menu: dict = {},
        info: str = "",
        quest_give: "Quest" = None,
        quest_solve: "Quest" = None,
        answer: str = "",
        game_clear: bool = False,
    ):
        self.name = name
        self.buy_menu = buy_menu
        self.sell_menu = sell_menu
        self.info = info
        self.quest_give = quest_give
        self.quest_solve = quest_solve
        self.answer = answer
        self.game_clear = game_clear

    # 해당 장소의 상호작용 목록 확인
    def interactions(self) -> list:
        labels = []
        if self.buy_menu:
            labels.append("구매")
        if self.sell_menu:
            labels.append("판매")
        if self.quest_give or self.quest_solve or self.game_clear:
            labels.append("임무")
        return labels

    # 구매 가능 여부 확인
    def can_buy(self) -> bool:
        return bool(self.buy_menu)

    # 판매 가능 여부 확인
    def can_sell(self) -> bool:
        return bool(self.sell_menu)

    # 임무 존재 여부 확인
    def has_quest(self) -> bool:
        return self.quest_give is not None or self.quest_solve is not None


# 플레이어 객체: 체력 / 잔액 / 위치 / 가방 / 임무 - 이동 기능 포함
class Player:
    def __init__(
        self,
        hp: int,
        money: int,
        location: str,
        location_idx: list,
        bag: dict = {},
        tasks: list = [],
    ):
        self.hp = hp
        self.money = money
        self.location = location
        self.location_idx = list(location_idx)
        self.bag = bag
        self.tasks = tasks

    # 가방 아이템 존재 여부 확인: check_bag에 전달
    def has_bag_items(self) -> bool:
        return bool(self.bag)

    # 가방에서 아이템 제거: sell_item에서 사용
    def clean_bag(self):
        self.bag = {k: v for k, v in self.bag.items() if v > 0}

    # 임무 진행 여부 확인: check_task에 전달
    def has_task(self) -> bool:
        return any(q.received and not q.cleared for q in self.tasks)

    # 임무 수령: quest_output에서 사용
    def add_task(self, quest: "Quest"):
        if quest not in self.tasks:
            self.tasks.append(quest)
        quest.received = True

    # 이동 기능: check_move 함수로 이동 가능 여부를 확인 후 이동 및 반영
    def move(self, direction: str, school_map: list, difficulty: str) -> str:
        directions = {
            "북": (0, 1),
            "남": (0, -1),
            "동": (1, 1),
            "서": (1, -1),
        }
        fatigue = {"보통": 1, "어려움": 2}

        if direction not in directions:
            return "잘못된 입력입니다."

        idx, num = directions[direction]
        if not self.check_move(school_map, idx, num):
            return "그 방향은 막혔어."

        self.hp -= fatigue[difficulty]
        self.location_idx[idx] += num
        self.location = school_map[self.location_idx[0]][self.location_idx[1]]
        return f"{self.location}(으)로 이동했습니다."

    # 이동 가능 여부 확인 함수: move 함수에 전달
    def check_move(self, school_map: list, axis_idx: int, delta: int) -> bool:
        after = self.location_idx.copy()
        after[axis_idx] += delta
        if after[0] < 0 or after[1] < 0:
            return False
        try:
            cell = school_map[after[0]][after[1]]
        except IndexError:
            return False
        return cell is not None

    # 상태 출력： ui mode에 따라 출력이 다름
    def print_status(self, school_map: list, ui_mode: str) -> list:
        # 위치가 None일 때 막힘 출력
        def adjust_dirstr(v):
            return v if v is not None else "막힘"

        r, c = self.location_idx[0], self.location_idx[1]
        east = school_map[r][c + 1] if c + 1 < len(school_map[r]) else None
        west = school_map[r][c - 1] if c - 1 >= 0 else None
        south = school_map[r - 1][c] if r - 1 >= 0 else None
        north = school_map[r + 1][c] if r + 1 < len(school_map) else None

        if ui_mode == "minimal":
            return [
                "< 상태창 >",
                f"계좌의 잔액 = {self.money:,}원",
                f"HP = {self.hp}",
                f"현재위치 = {self.location}",
                f"동서남북 = {adjust_dirstr(east)}, {adjust_dirstr(west)}, {adjust_dirstr(south)}, {adjust_dirstr(north)}",
            ]

        else:
            return [
                "< 상태창 >",
                f"1. 소지금: {self.money}원",
                f"2. 체력:   {self.hp}",
                f"3. 위치: {self.location}",
                f"4. 동쪽위치: {adjust_dirstr(east)}",
                f"5. 서쪽위치: {adjust_dirstr(west)}",
                f"6. 남쪽위치: {adjust_dirstr(south)}",
                f"7. 북쪽위치: {adjust_dirstr(north)}",
            ]


# ------------------------- I/O 로깅 / 카운터 -------------------------#
io_counter = 0
input_log = []
f_input_log = []
f_output_log = []

# 텍스트 출력 함수: minimal일 때 [N] 추가
def game_output(text: str = ""):
    global io_counter
    io_counter += 1
    
    if settings["ui_mode"] == "minimal":
        lines = text.split("\n") if text else [""]
        f_output_log.append(f"[{io_counter}] {lines[0]}")
        print(f"[{io_counter}] {lines[0]}")
        for line in lines[1:]:
            f_output_log.append(f"{line}")
            print(line)
    else:
        print(text)


# 리스트를 받아 이를 텍스트 출력 함수로 보내는 기능
def game_output_block(texts: list):
    cleaned = [t for t in texts if t not in ("", None)]
    if not cleaned:
        return
    formatted = [cleaned[0]] + ["     " + t for t in cleaned[1:]]
    game_output("\n".join(formatted))


# 텍스트 입력 함수: minimal일 때 [N] 추가
def game_input(text: str = "> ") -> str:
    global io_counter
    io_counter += 1
    if settings["ui_mode"] == "minimal":
        user_input = input(f"[{io_counter}] 입력: ")
    else:
        user_input = input(text)
    input_log.append(user_input)
    f_input_log.append((f"[{io_counter}] {user_input}"))
    return user_input


# 입출력 로그 저장: minimal에서만 실행 - 채점용
def dump_log():
    if settings["ui_mode"] == "minimal":    
        with open("player_input.txt", "w") as f:
            for line in f_input_log:
                f.write(line + "\n")
        with open("game_output.txt", "w") as f:
            for line in f_output_log:
                f.write(line + "\n")
    else:
        return


# ---------------------------- UI 분리  ----------------------------#


# 기본 화면 출력
def render_main(message: str):
    if settings["ui_mode"] == "full":
        main_output(message)
    else:
        game_output(message)


# 특수 화면 출력(가방, 상태출력, 임무 등)
def render_panel(texts: list, message: str, activate: bool = True, notification: bool = False):
    if settings["ui_mode"] == "full":
        texts = [t.strip() for t in texts]
        common_output(texts, message.strip())
        if notification:
            while game_input().strip() != "닫기":
                common_output(texts, "잘못된 입력입니다.")
            render_main("창을 닫았습니다.")
    else:
        block = list(texts)
        if message and activate:
            block.append(message)
        game_output_block(block)


# ---------------------------- 기초 출력 -----------------------------#


# 초기 출력 : UI 모드 선택 → 게임 설명 및 난이도 설정
def uiselect_output():
    while True:
        game_output(
            "보조 인터페이스를 사용하시겠습니까?\n"
            "    1) 사용 O - 박스, 지도 그림, 상태 패널 등을 화면에 표시\n"
            "    2) 사용 X - 텍스트만 [번호] 와 함께 표시"
        )
        choice = game_input()
        if choice == "1":
            settings["ui_mode"] = "full"
            return
        elif choice == "2":
            settings["ui_mode"] = "minimal"
            return
        else:
            game_output("잘못된 입력입니다.")


# 초기 출력 : 게임 설명 및 난이도 설정
def initial_output(texts: list, message: str, width: int = 85, height: int = 13):
    prepGame = True
    difficulty = ["보통", "어려움"]
    while prepGame:
        prepGame = False
        if settings["ui_mode"] == "full":
            print("=" * width)
            print(f"[↑] 해당 게임은 화살표 위에 있는 === 줄에")
            print(f"    터미널 사이즈를 맞추는 것을 추천드립니다.")
            print("=" * width)
            for text in texts:
                print(text)
            for _ in range(max(0, height - len(texts))):
                print()
            print("=" * width)
            print(message)
            print("=" * width)
            user_input = input("> ").strip()
        else:
            # minimal 모드: 안내 한 줄 + 입력
            game_output("난이도를 선택하세요. (1: 보통 | 2: 어려움)")
            user_input = game_input()

        if user_input == "1" or user_input == "보통":
            settings["difficulty"] = difficulty[0]
        elif user_input == "2" or user_input == "어려움":
            settings["difficulty"] = difficulty[1]
        else:
            message = "잘못된 입력입니다."
            if settings["ui_mode"] == "minimal":
                game_output(message)
            prepGame = True


# 범용 출력 : 특수 출력에 사용되는 공통 출력 양식
def common_output(texts: list, message: str, width: int = 85, height: int = 13):
    print("=" * width)
    print(f"[위치]: {player.location}")
    print(f"[HP]: {player.hp}")
    print("=" * width)
    for text in texts:
        print(text)
    for _ in range(max(0, height - len(texts))):
        print()
    print("=" * width)
    print(message)
    print("=" * width)


# 기본 출력 : 게임의 기본 화면
def main_output(message: str, col: int = 6, row: int = 7):
    cell_w = 13
    h_line = "+" + (("-" * cell_w + "+") * col)
    eq_line = "=" * (cell_w * col + col + 1)
    lines = []
    loc_idx = player.location_idx
    print(eq_line)
    print(f"[위치]: {player.location}")
    print(f"[HP]: {player.hp}")
    for r in range(row - 1, -1, -1):
        if r == row - 1:
            lines.append(eq_line)
        else:
            lines.append(h_line)
        row_str = "|"
        for c in range(col):
            if r == loc_idx[0] and c == loc_idx[1]:
                cell = "★".center(cell_w)
            elif schoolMap[r][c] is None:
                cell = "|" * cell_w
            else:
                cell = "·".center(cell_w)
            row_str += cell + "|"
        lines.append(row_str)
    lines.append(eq_line)
    print("\n".join(lines))
    print(message)
    print(eq_line)


# ---------------------------- 기능 출력 -----------------------------#


# 도움말 출력
def help_output(texts: list, message: str):
    if settings["ui_mode"] == "minimal":
        game_output_block(texts)
        return

    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "닫기":
            render_main("게임조작법창을 닫았습니다.")
            break
        else:
            message = "잘못된 입력입니다."


# 상태 출력 : 상태창 출력
def status_output(texts: list, message: str):
    if settings["ui_mode"] == "minimal":
        game_output_block(texts)
        return

    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "닫기":
            render_main("상태창을 닫았습니다.")
            break
        else:
            message = "잘못된 입력입니다."


# 가방 출력 : 가방 출력 및 아이템 사용
def bag_output(texts: list, message: str):
    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "종료" or user_input == str(len(player.bag) + 1):
            render_main("가방을 닫았습니다.")
            break
        else:
            useItem = use_item(user_input)
            if check_bag():
                texts = open_bag()
                message = useItem
            else:
                render_main(useItem)
                break


# 임무 출력 : 현재 사용자의 임무 출력
def task_output(texts: list, message: str):
    if settings["ui_mode"] == "minimal":
        game_output_block(texts)
        return

    while True:
        render_panel(texts, message)
        user_input = game_input().strip()
        if user_input == "닫기":
            render_main("임무창을 닫았습니다.")
            break
        else:
            message = "잘못된 입력입니다."


# 불러오기 출력 : 저장된 파일 목록 출력 및 불러오기
def load_output(save_dir: str, message: str):
    save_dir_ = save_dir
    texts = load_game_list(save_dir)[0]
    dir_list = load_game_list(save_dir)[1]
    change_dir = False
    while True:
        render_panel(texts, message)

        if change_dir:
            save_dir = game_input().strip()
            if check_load_empty(save_dir):
                message = "잘못된 입력입니다."
                save_dir = save_dir_
            else:
                texts = load_game_list(save_dir)[0]
                dir_list = load_game_list(save_dir)[1]
                message = f"{os.path.basename(save_dir)}(으)로 폴더를 변경했습니다."
                save_dir_ = save_dir
            change_dir = False
            continue
        else:
            user_input = game_input().strip()

        if user_input == "닫기":
            render_main("불러오기를 종료합니다.")
            break
        elif user_input == "0":
            change_dir = True
            message = "변경할 폴더를 입력하세요."
        elif user_input.isdigit() and 1 <= int(user_input) <= len(dir_list):
            file_name = dir_list[int(user_input) - 1]
            message = load_game(save_dir, file_name)
            render_main(message)
            break
        else:
            message = "잘못된 입력입니다. (0: 폴더 변경)"


# 구매 출력 : 상점 출력 및 아이템 구매
def buy_output(texts: list, message: str, location_name: str):
    place = places.get(location_name)
    if place is None or not place.can_buy():
        render_main("이 장소에서는 구매할 수 없습니다.")
        return

    while True:
        render_panel(texts, message)
        user_input = game_input().strip()

        menu_items = list(place.buy_menu.items())
        exit_idx = len(menu_items) + 1
        if user_input == "종료" or user_input == str(exit_idx):
            render_main("상점 이용을 종료합니다.")
            break

        target_item = None
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(menu_items):
                target_item = menu_items[idx][0]
            else:
                message = "잘못된 입력입니다."
                continue
        else:
            for item, _ in menu_items:
                if item.name == user_input:
                    target_item = item
                    break
            if target_item is None:
                message = "잘못된 입력입니다."
                continue

        price = place.buy_menu[target_item]
        if player.money >= price:
            player.money -= price
            player.bag[target_item.name] = player.bag.get(target_item.name, 0) + 1
            message = f"→ {target_item.name} 구매 완료 (잔액: {player.money}원)"
            texts = show_shop(location_name)
        else:
            message = f"돈이 부족합니다. (필요: {price}원, 보유: {player.money}원)"


# 판매 출력 : 상점 출력 및 아이템 판매
def sell_output(texts: list, message: str, location_name: str):
    place = places[location_name]
    sale_message = ''
    if place is None or not place.can_sell():
        render_main("이 장소에서는 판매할 수 없습니다.")
        return

    while True:
        sellable_items = check_sell(location_name)

        if not sellable_items:
            render_main(f"{(sale_message + ' | 판매할 아이템이 없어 종료합니다.') if sale_message else '판매할 아이템이 없습니다.'}")
            return

        render_panel(texts, message)
        user_input = game_input().strip()

        exit_idx = len(sellable_items) + 1
        if user_input == "종료" or user_input == str(exit_idx):
            render_main("판매를 종료합니다.")
            return

        target = None
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(sellable_items):
                target = sellable_items[idx]
            else:
                message = "잘못된 입력입니다."
                continue
        else:
            for item, price, count in sellable_items:
                if item.name == user_input:
                    target = (item, price, count)
                    break
            if target is None:
                message = "잘못된 입력입니다."
                continue

        player.money += target[1]
        player.bag[target[0].name] -= 1
        player.clean_bag()
        sale_message = (
            f"→ {target[0].name}을(를) 판매해서 {target[1]}원을 벌었다. "
            f"(계좌 잔액: {player.money}원)"
        )  
        message = sale_message
        texts = show_sell(location_name)


# ---------------------------- 기타 출력 -----------------------------#


# 도움말 출력 리스트
def print_help():
    printHelp = []
    printHelp.append("< 게임 조작법 >")
    printHelp.append(f"- 동/서/남/북\t| 해당 방향으로 한 칸 이동")
    printHelp.append(f"- 구매/판매/임무\t| 현재 장소에서 구매/판매/임무 상호작용")
    printHelp.append(f"- 가방\t\t| 가방 확인 및 아이템 사용")
    printHelp.append(f"- 임무목록/상태\t| 보유 임무/현재 상태 확인")
    printHelp.append(f"- 도움말\t\t| 도움말 확인")
    printHelp.append(f"- 난이도\t\t| 난이도 확인 및 변경")
    printHelp.append(f"- 저장/불러오기\t| 게임 저장/불러오기")
    printHelp.append(f"- 닫기\t\t| 현재 탭 닫기(보조 인터페이스용)")
    printHelp.append(f"- 종료\t\t| 게임 종료")
    return printHelp


# 난이도 출력 리스트
def print_setdifficulty():
    printSetdifficulty = []
    printSetdifficulty.append("")
    printSetdifficulty.append("< 난이도 설정 >")
    printSetdifficulty.append(f"  1. 보통 | 2. 어려움")
    return printSetdifficulty


# 이동 후 상호작용 가능 장소 도착 시 표시
def show_interaction(location_name: str) -> str:
    place = places.get(location_name)
    if place is None:
        return ""
    labels = place.interactions()
    if not labels:
        return ""
    return "[" + ", ".join(labels) + "]"


# ---------------------------- 가방 함수 -----------------------------#


# 가방 확인 : T/F 반환
def check_bag() -> bool:
    return player.has_bag_items()


# 가방 열기 : 아이템 이름 및 특성 출력
def open_bag() -> list:
    openBag = []
    openBag.append("< 가방 >")
    for i, (name, count) in enumerate(player.bag.items(), 1):
        hp_recover = items[name].recovery if name in items else 0
        openBag.append(f"{i}) {name}  x{count}  (HP +{hp_recover})")
    openBag.append(f"{len(player.bag) + 1}) 종료")
    return openBag


# 아이템 사용 : idx 기반 및 이름 기반 처리
def use_item(user_input: str) -> str:
    bag_items = list(player.bag.items())

    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(bag_items):
            name = bag_items[idx][0]
        else:
            return "가방에 없는 번호입니다."
    elif user_input in player.bag:
        name = user_input
    else:
        return "가방에 없는 아이템입니다."

    recover = items[name].recovery if name in items else 0
    player.hp += recover
    player.bag[name] -= 1
    player.clean_bag()
    item_message = f"→ {name}(을)를 먹었습니다. (HP: {player.hp})"
    return item_message if player.has_bag_items() else item_message + " | 아이템이 없어서 가방을 닫았습니다."


# ---------------------------- 임무 함수 -----------------------------#


# 임무 확인 : T/F 반환
def check_task() -> bool:
    return player.has_task()


# 임무 열기 : 진행 중 임무들의 이름과 설명 출력
def open_task() -> list:
    openTask = []
    openTask.append("< 임무 >")
    active = [q for q in player.tasks if q.received and not q.cleared]
    for q in active:
        openTask.append(f"{q.name} - {q.description}")
    return openTask


# 임무 진행 : 전반적인 임무의 처리
def do_task():
    place = places.get(player.location)
    if place is None:
        render_main("이 장소에서는 임무 상호작용을 할 수 없습니다.")
        return None

    loc = player.location

    if loc == "정문":
        guide = quests["독수리의 전언"]
        if guide.received or guide.cleared:
            render_main("이미 수령한 임무입니다.")
            return None
        player.add_task(guide)
        render_panel(
            [
                guide.description,
                f"< {guide.name} > 임무가 추가되었습니다.",
            ],
            "임무가 추가되었습니다.",
            activate=False,
            notification=True,
        )
        return None

    if loc == "독수리상":
        guide = quests["독수리의 전언"]
        if not guide.received:
            render_main("정문으로 이동하여 임무를 수령하시오.")
            return None
        if guide.cleared:
            render_main("이미 받은 임무입니다.")
            return None

        guide.cleared = True
        q1 = quests["교내 부조리 수사"]
        q2 = quests["교내 위생사건 수사"]
        player.add_task(q1)
        player.add_task(q2)
        render_panel(
            [
                f"< {guide.name} > 임무가 해결되었습니다!",
                "새로운 임무들이 추가되었습니다!",
                f"< {q1.name} >",
                f"{q1.description}",
                f"< {q2.name} >",
                f"{q2.description}",
            ],
            "임무가 해결되었고 새 임무가 추가되었습니다.",
            activate=False,
            notification=True,
        )
        return None

    if place.quest_solve is not None:
        target = place.quest_solve
        if not target.received:
            render_main("아직 받지 않은 임무입니다.")
            return None
        if target.cleared:
            render_main("이미 해결된 임무입니다.")
            return None

        if loc == "본관":
            question = "교내 어디에 부조리가 있나?"
        elif loc == "세브란스병원":
            question = "교내 어디에 식중독 원인이 있나?"
        else:
            question = "정답을 입력하시오."

        render_main(question)
        answer = game_input().strip()

        if answer == place.answer:
            target.cleared = True
            render_panel(
                [
                    f"다음의 임무가 해결되었다! [{target.name}]",
                    "수업들으러 이윤재관 가야지!",
                ],
                "임무가 해결되었습니다.",
                activate=False,
                notification=True,
            )
        else:
            render_main("틀렸습니다. 다시 조사해 보세요.")
        return None

    if place.game_clear:
        q1_done = quests["교내 부조리 수사"].cleared
        q2_done = quests["교내 위생사건 수사"].cleared
        if q1_done and q2_done:
            render_main("부조리와 식중독 수사를 완료했구나! 수업은 이걸로 끝입니다. 또 만나요~")
            return "finish"
        elif q1_done:
            render_main("부조리 수사를 완료했구나! 식중독 원인도 찾아주세요~")
        elif q2_done:
            render_main("식중독 수사를 완료했구나! 부조리도 찾아주세요~")
        else:
            render_main("아직 완료된 임무가 없습니다. 부조리와 식중독 원인을 찾아주세요~")
        return None

    render_main("이 장소에서는 임무 상호작용을 할 수 없습니다.")
    return None


# ------------------------- 구매/판매 함수 --------------------------#


# 상점 메뉴 텍스트 리스트 (구매창에 표시할 라인들)
def show_shop(location_name: str) -> list:
    place = places.get(location_name)
    shop_list = []
    shop_list.append(f"[ {location_name} 상점 ] - 소지금 {player.money}원")
    if place is None or not place.can_buy():
        return shop_list
    for i, (item, price) in enumerate(place.buy_menu.items(), 1):
        shop_list.append(
            f"{i}) {item.name}: {price}원, HP가 {item.recovery}만큼 증가한다."
        )
    shop_list.append(f"{len(place.buy_menu) + 1}) 종료")
    return shop_list


# 판매 가능 항목 = 보유 ∩ sell_menu. (보유한 Item 객체, 가격, 보유수량) 의 리스트로 반환.
def check_sell(location_name: str) -> list:
    place = places.get(location_name)
    if place is None or not place.can_sell():
        return []
    result = []
    for item, price in place.sell_menu.items():
        count = player.bag.get(item.name, 0)
        if count > 0:
            result.append((item, price, count))
    return result


# 판매 메뉴 텍스트 리스트
def show_sell(location_name: str) -> list:
    sellables = check_sell(location_name)
    sell_list = [f"[ {location_name} 판매점 ] - 소지금 {player.money}원"]
    for i, (item, price, count) in enumerate(sellables, 1):
        sell_list.append(f"{i}) {item.name} x{count}  ({price}원)")
    sell_list.append(f"{len(sellables) + 1}) 종료")
    return sell_list


# ------------------------- 저장/불러오기 함수 --------------------------#


# 게임 저장하기 : 이름 입력 후 저장
def save_game():
    file_name = game_input().strip()
    os.makedirs("saves", exist_ok=True)
    with open(f"saves/{file_name}.txt", "w") as f:
        f.write(f"hp: {player.hp}\n")
        f.write(f"money: {player.money}\n")
        f.write(f"bag: {player.bag}\n")
        f.write(f"location: {player.location}\n")
        f.write(f"location_idx: {player.location_idx}\n")
        quest_state = {q.name: (q.received, q.cleared) for q in quests.values()}
        f.write(f"quest_state: {quest_state}\n")
        f.write(f"difficulty: {settings['difficulty']}\n")
        f.write(f"inputs: {input_log}\n")
    return f"{file_name}으로 저장되었습니다."


# 게임 불러오기 : 폴더에서 파일 선택 후 각 요소 불러오기 - 폴더 변경 가능
def load_game_list(save_dir: str):
    file_list = [
        f for f in os.listdir(save_dir) if not f.startswith(".") and f.endswith(".txt")
    ]
    load_list = []
    load_list.append("< 저장된 파일 목록 >")
    for i, file in enumerate(file_list):
        load_list.append(f"{i + 1}. {file}")
    return load_list, file_list


# 저장 폴더 확인 : 폴더가 없거나 파일이 없으면 True 반환
def check_load_empty(save_dir: str):
    if not os.path.isdir(save_dir):
        return True
    file_list = [
        f for f in os.listdir(save_dir) if not f.startswith(".") and f.endswith(".txt")
    ]
    if len(file_list) == 0:
        return True
    return False


# 게임 불러오기 : 파일 선택 후 각 요소 불러오기
def load_game(save_dir, file_name):
    global input_log
    with open(os.path.join(save_dir, file_name), "r") as save_file:
        for line in save_file:
            line = line.rstrip("\n")
            if line.startswith("hp: "):
                player.hp = float(line[4:]) if "." in line[4:] else int(line[4:])
            elif line.startswith("money: "):
                player.money = int(line[7:])
            elif line.startswith("bag: "):
                player.bag = eval(line[5:])
            elif line.startswith("location: "):
                player.location = line[10:]
            elif line.startswith("location_idx: "):
                player.location_idx = eval(line[14:])
            elif line.startswith("quest_state: "):
                state = eval(line[13:])
                player.tasks = []
                for qname, (received, cleared) in state.items():
                    if qname in quests:
                        q = quests[qname]
                        q.received = received
                        q.cleared = cleared
                        if received and q not in player.tasks:
                            player.tasks.append(q)
            elif line.startswith("difficulty: "):
                settings["difficulty"] = line[12:]
            elif line.startswith("inputs: "):
                input_log = eval(line[8:])
    return f"{os.path.basename(file_name)}을 불러왔습니다."


# ---------------------------- 기타 함수 ----------------------------#


# 지도 생성 : 리스트 - 지도, 지도 좌표
def create_map(col: int, location: list) -> list:
    schoolMap = []
    rMap = []
    for idx, loc in enumerate(location):
        rMap.append(loc)
        if (idx + 1) % col == 0:
            schoolMap.append(rMap)
            rMap = []
    return schoolMap


# pickle 사용 임무 정보 불러오기
def load_tasks(path: str):
    with open(path, "rb") as f:
        data = pickle.load(f)

    for place_name, info_text in data["events"].items():
        if place_name in places:
            places[place_name].info = info_text
    quest_to_place = {}
    for p in places.values():
        if p.quest_solve is not None:
            quest_to_place[p.quest_solve.name] = p
    for quest_name, answer_loc in data["answers"].items():
        if quest_name in quest_to_place:
            quest_to_place[quest_name].answer = answer_loc


# ---------------------------- 변수 목록 -----------------------------#

# 학교 위치: 연대앞 버스정류장 ~ 이윤재관 (지도 raw 데이터)
school_locations = [
    "연대앞 버스정류장",
    "정문",
    "스타벅스",
    "세브란스병원 버스정류장",
    None,
    None,
    "공학원",
    "백양로1",
    "공터1",
    "암병원",
    "의과대학",
    None,
    "공학관",
    "백양로2",
    "백주년기념관",
    "안과병원",
    "제중관",
    None,
    "체육관",
    "백양로3",
    "공터2",
    "광혜원",
    "어린이병원",
    "세브란스병원",
    "중앙도서관",
    "독수리상",
    "학생회관",
    "루스채플",
    "재활병원",
    "치과대학",
    "백양관",
    "백양로5",
    "대강당",
    "음악관",
    "알렌관",
    "ABMRC",
    "종합관",
    "본관",
    "경영관",
    "노천극장",
    "새천년관",
    "이윤재관",
]

# 지도 생성
schoolMap = create_map(6, school_locations)

# 학교 장소 생성 - 객체 넣기
places = {}
for loc_name in school_locations:
    if loc_name is None:
        continue
    places[loc_name] = Place(loc_name)

# 아이템 정의
items = {
    "두쫀쿠": Item("두쫀쿠", recovery=10),
    "카페라떼": Item("카페라떼", recovery=5),
}

# 구매 그룹: 각 객체에 배정(장소들의 리스트, 물건 가격 dict로 이루어진 튜플)
buy_group = [
    (["학생회관"], {"두쫀쿠": 5000, "카페라떼": 3000}),
    (["스타벅스", "ABMRC"], {"두쫀쿠": 4000, "카페라떼": 2000}),
]

for names, prices in buy_group:
    for name in names:
        places[name].buy_menu = {
            items[item_name]: price for item_name, price in prices.items()
        }

# 판매 그룹: 각 객체에 배정(장소들의 리스트, 물건 가격 dict로 이루어진 튜플)
sell_group = [
    (
        ["체육관", "공학관", "공학원", "재활병원", "어린이병원", "종합관", "노천극장"],
        {"두쫀쿠": 7000, "카페라떼": 4000},
    ),
    (
        [
            "중앙도서관",
            "백양관",
            "대강당",
            "백주년기념관",
            "안과병원",
            "암병원",
            "새천년관",
            "알렌관",
            "제중관",
            "의과대학",
            "치과대학",
            "세브란스병원",
            "본관",
            "경영관",
        ],
        {"두쫀쿠": 6000, "카페라떼": 3000},
    ),
]

for names, prices in sell_group:
    for name in names:
        places[name].sell_menu = {
            items[item_name]: price for item_name, price in prices.items()
        }

# 임무 생성
quests = {
    "독수리의 전언": Quest(
        name="독수리의 전언",
        description=(
            "학교에서 어떤 일들이 일어나고있는지 소식들이 모이는 독수리상에서 알아보자."
        ),
    ),
    "교내 부조리 수사": Quest(
        name="교내 부조리 수사",
        description=(
            "교내 어딘가에서 부조리가 일어나고있다. "
            "이동하고 상호작용을 해서 부조리를 찾아서 본관에 보고하라."
        ),
    ),
    "교내 위생사건 수사": Quest(
        name="교내 위생사건 수사",
        description=(
            "학생들이 단체로 식중독에 걸렸다. "
            "이동하고 상호작용을 해서 위생사건의 원인을 찾아서 세브란스에 보고하라."
        ),
    ),
}

# 기본 임무 환경 할당
places["정문"].quest_give = quests["독수리의 전언"]
places["독수리상"].quest_give = quests["교내 부조리 수사"]
places["본관"].quest_solve = quests["교내 부조리 수사"]
places["세브란스병원"].quest_solve = quests["교내 위생사건 수사"]
places["이윤재관"].game_clear = True

# 게임 기본 설정
settings = {"difficulty": "보통", "ui_mode": "minimal"}

# 플레이어 생성
player = Player(hp=10, money=10000, location="연대앞 버스정류장", location_idx=[0, 0])

# 기본 임무 로드
load_tasks("event.bin")

# ---------------------------- 메인 함수 -----------------------------#
if __name__ == "__main__":
    uiselect_output()
    initial_output(print_help() + print_setdifficulty(), "난이도를 입력하면 게임이 시작됩니다.")
    render_main("송도 생활을 마치고 신촌에 처음 도착했다. 연대앞 버스정류장이다.")
    
    while True:
        user_input = game_input().strip()

        if user_input == "종료":
            render_main("게임을 종료합니다.")
            break

        elif user_input in ("동", "서", "남", "북"):
            message = player.move(user_input, schoolMap, settings["difficulty"])
            if player.hp <= 0:
                render_main("HP가 0이 되었습니다. 게임 오버...")
                break
            if message.endswith("(으)로 이동했습니다."):
                label = show_interaction(player.location)
                arrival_message = f"{message} {label}".rstrip() if label else message
                info = places[player.location].info
                if info:
                    if settings["ui_mode"] == "minimal":
                        render_main(f"{arrival_message}\n     {info}")
                    else:
                        render_panel(
                            [info],
                            f"{arrival_message} (사건이 있습니다)",
                            activate=False,
                            notification=True,
                        )
                else:
                    render_main(arrival_message)
            else:
                render_main(message)

        elif user_input == "상태":
            status_output(player.print_status(schoolMap, settings["ui_mode"]),
                "현재 사용자의 상태입니다.",
            )

        elif user_input == "가방":
            if check_bag():
                bag_output(open_bag(), "사용할 아이템의 숫자 혹은 이름을 입력하시오.")
            else:
                render_main("가방이 비어있습니다.")

        elif user_input == "임무목록":
            if check_task():
                task_output(open_task(), "현재 사용자의 임무입니다.")
            else:
                render_main("현재 진행 중인 임무가 없습니다.")

        elif user_input == "도움말":
            help_output(
                print_help(),
                "조작법에 해당하는 명령어를 입력하여 게임을 진행하시오.",
            )

        elif user_input == "구매":
            place = places.get(player.location)
            if place and place.can_buy():
                buy_output(
                    show_shop(player.location),
                    "구매할 아이템의 이름 또는 번호를 입력하시오.",
                    player.location,
                )
            else:
                render_main("이 장소에서는 구매할 수 없습니다.")

        elif user_input == "판매":
            place = places.get(player.location)
            if place and place.can_sell():
                sell_output(
                    show_sell(player.location),
                    "판매할 아이템의 이름 또는 번호를 입력하시오.",
                    player.location,
                )
            else:
                render_main("이 장소에서는 판매할 수 없습니다.")

        elif user_input == "임무":
            if do_task() == "finish":
                dump_log()
                break

        elif user_input == "난이도":
            render_main("변경할 난이도를 입력하시오 (1. 보통 | 2. 어려움)")
            diff_in = game_input().strip()
            if diff_in in ["1", "보통"]:
                settings["difficulty"] = "보통"
                render_main("난이도를 '보통'으로 변경했습니다.")
            elif diff_in in ["2", "어려움"]:
                settings["difficulty"] = "어려움"
                render_main("난이도를 '어려움'으로 변경했습니다.")
            else:
                render_main(f"난이도를 변경하지 않았습니다. (현재: {settings['difficulty']})")

        elif user_input == "저장":
            render_main("저장할 파일 이름을 입력하시오.")
            message = save_game()
            render_main(message)

        elif user_input == "불러오기":
            if check_load_empty("saves"):
                render_main("저장된 파일이 없습니다.")
            else:
                load_output("saves", "불러올 파일의 번호를 입력하시오. (0: 폴더 변경)")

        else:
            render_main("잘못된 입력입니다. (도움말: 명령어 안내)")